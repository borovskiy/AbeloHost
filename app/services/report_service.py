from io import StringIO
from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd

from app.core.db_connector import get_db
from app.repo.transaction_repo import TransactionRepository
from app.schemas.report_schema import TransactionFilter, ReportResponse, DailyShift, CountryStatsFilter, CSVData, \
    CSVDataList, CountryReportResponse, CountryStat
from app.services.base_services import BaseServices


class ReportServices(BaseServices):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.report_repo = TransactionRepository(self.session)

    async def get_all_report_by_filter(self, filters: TransactionFilter) -> ReportResponse:
        # Получаем агрегированные данные
        aggregated = await self.report_repo.get_aggregated_report(filters)
        # Получаем данные по дням, если нужно
        return ReportResponse(
            total_amount=aggregated.total_amount,
            transaction_count=aggregated.transaction_count,
            avg_amount=aggregated.avg_amount,
            min_amount=aggregated.min_amount,
            max_amount=aggregated.max_amount,
            daily_shifts=await self.report_repo.get_daily_shifts(filters) if filters.include_daily_shift else None,
        )

    async def get_user_id_for_n_countries(self, countries_csv: str, filters: CountryStatsFilter) -> CSVDataList:
        try:
            countries_df = pd.read_csv(StringIO(countries_csv), sep=";")
        except Exception as e:
            raise ValueError(f"Ошибка парсинга CSV: {str(e)}")

        required_columns = {'user_id', 'country'}
        if not required_columns.issubset(countries_df.columns):
            missing = required_columns - set(countries_df.columns)
            raise ValueError(f"Отсутствуют обязательные колонки в CSV: {missing}")

        grouped = countries_df.groupby('country')['user_id'].apply(list).to_dict()
        # Сортируем страны по количеству пользователей (по убыванию)
        sorted_countries = sorted(
            grouped.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )
        # Ограничиваем top_n, если задано
        selected_countries = sorted_countries[:filters.top_n] if filters.top_n else sorted_countries

        # Одна итерация для формирования обоих списков
        list_id_for_search: List[int] = []
        list_id_data_csv: List[CSVData] = []
        list_for_frame_user_country: List[dict] = []
        for country_name, user_ids in selected_countries:
            list_for_frame_user_country.extend([{"user_id": id_user, "country": country_name} for id_user in user_ids])
            list_id_for_search.extend(user_ids)
            list_id_data_csv.append(
                CSVData(
                    country=country_name,
                    list_id_user_country=user_ids.copy()
                )
            )
        return CSVDataList(
            list_id_for_search=list_id_for_search,
            list_id_data_csv=list_id_data_csv,
            list_for_frame_user_country=list_for_frame_user_country
        )

    async def get_report_countre(self, countries_csv: str, filters: CountryStatsFilter):
        list_user_id = await self.get_user_id_for_n_countries(countries_csv, filters)
        list_trans = await self.report_repo.get_trans_user_ids(list_user_id.list_id_for_search)
        # Создаём DataFrame из транзакций
        trans_data = [
            {"user_id": t.user_id, "amount": float(t.sum_pay)}  # используем sum_pay, конвертируем в float
            for t in list_trans
        ]
        df_trans = pd.DataFrame(trans_data)

        if df_trans.empty:
            return CountryReportResponse(stats=[])

        df_countries = pd.DataFrame(list_user_id.list_for_frame_user_country)

        # Объединяем транзакции с странами
        df_joined = df_trans.merge(df_countries, on='user_id', how='inner')

        # Агрегируем по странам
        agg_stats = (
            df_joined.groupby('country')
            .agg(
                transaction_count=('amount', 'count'),
                total_amount=('amount', 'sum'),
                average_amount=('amount', 'mean')
            )
            .reset_index()
        )

        # Сортировка
        sort_column = {
            "count": "transaction_count",
            "total": "total_amount",
            "avg": "average_amount"
        }.get(filters.sort_by or "count", "transaction_count")
        ascending_order = not (filters.sort_by == "asc")  # по умолчанию сортировка по убыванию
        agg_stats = agg_stats.sort_values(by=sort_column, ascending=ascending_order)

        # Формируем результат
        stats = [
            CountryStat(
                country=row['country'],
                transaction_count=int(row['transaction_count']),
                total_amount=row['total_amount'],
                average_amount=row['average_amount']
            )
            for _, row in agg_stats.iterrows()
        ]

        return stats


async def report_services(session: AsyncSession = Depends(get_db)) -> ReportServices:
    return ReportServices(session)
