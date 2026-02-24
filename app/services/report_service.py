from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd

from app.core.db_connector import get_db
from app.repo.transaction_repo import TransactionRepository
from app.schemas.report_schema import (
    TransactionFilter,
    ReportResponse,
    CountryStatsFilter,
    CountryReportResponse,
    CountryStat,
)
from app.services.base_services import BaseServices
from app.services.utils.utils_pandas_frame import get_user_id_for_n_countries


class ReportServices(BaseServices):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.report_repo = TransactionRepository(self.session)

    async def get_all_report_by_filter(
        self, filters: TransactionFilter
    ) -> ReportResponse:
        # Получаем агрегированные данные
        aggregated = await self.report_repo.get_aggregated_report(filters)
        # Получаем данные по дням, если нужно
        return ReportResponse(
            total_amount=aggregated.total_amount,
            transaction_count=aggregated.transaction_count,
            avg_amount=aggregated.avg_amount,
            min_amount=aggregated.min_amount,
            max_amount=aggregated.max_amount,
            daily_shifts=(
                await self.report_repo.get_daily_shifts(filters)
                if filters.include_daily_shift
                else None
            ),
        )

    async def get_report_country(self, countries_csv: str, filters: CountryStatsFilter):
        list_user_country_data = get_user_id_for_n_countries(countries_csv, filters)
        list_trans = await self.report_repo.get_trans_user_ids(
            list_user_country_data.list_id_for_search
        )
        # Создаём DataFrame из транзакций
        trans_data = [
            {
                "user_id": t.user_id,
                "amount": float(t.sum_pay),
            }  # используем sum_pay, конвертируем в float
            for t in list_trans
        ]
        df_trans = pd.DataFrame(trans_data)
        if df_trans.empty:
            return CountryReportResponse(stats=[])

        df_countries = pd.DataFrame(list_user_country_data.list_for_frame_user_country)
        # Объединяем транзакции с странами
        df_joined = df_trans.merge(df_countries, on="user_id", how="inner")
        # Агрегируем по странам
        agg_stats = (
            df_joined.groupby("country")
            .agg(
                transaction_count=("amount", "count"),
                total_amount=("amount", "sum"),
                average_amount=("amount", "mean"),
            )
            .reset_index()
        )
        # Сортировка
        sort_column = {
            "count": "transaction_count",
            "total": "total_amount",
            "avg": "average_amount",
        }.get(filters.sort_by or "count", "transaction_count")
        agg_stats = agg_stats.sort_values(by=sort_column, ascending=True)
        stats = [
            CountryStat(
                country=row["country"],
                transaction_count=int(row["transaction_count"]),
                total_amount=row["total_amount"],
                average_amount=row["average_amount"],
            )
            for _, row in agg_stats.iterrows()
        ]
        return stats


async def report_services(session: AsyncSession = Depends(get_db)) -> ReportServices:
    return ReportServices(session)
