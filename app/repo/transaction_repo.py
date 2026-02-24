import logging
from datetime import date, datetime, timezone
from typing import List, Sequence

from sqlalchemy import select, func, cast, Select, Text, literal_column, case

from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.enum_aggregate import TransactionFieldEnum
from app.enums.enum_status import APITypeStatusEnum
from app.enums.enum_type_pay import APITypePayEnum
from app.models import TransactionModel
from app.repo.base_repository import BaseRepo
from app.schemas.report_schema import TransactionFilter, DailyShift, AggregateReport


class TransactionRepository(BaseRepo[TransactionModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.trans_model = TransactionModel

    async def get_report_by_filter(
        self, query: Select, filters: TransactionFilter
    ) -> Select:
        # Базовый запрос с фильтрацией по дате, статусам, типам
        if filters.start_date:
            start_datetime = datetime.combine(
                filters.start_date_parsed, datetime.min.time()
            )
            query = query.where(self.trans_model.date_pay >= start_datetime)
        if filters.end_date:
            end_datetime = datetime.combine(
                filters.end_date_parsed, datetime.max.time()
            )
            query = query.where(self.trans_model.date_pay <= end_datetime)
        if filters.status != APITypeStatusEnum.ALL:
            query = query.where(self.trans_model.status == filters.status)
        if filters.type != APITypePayEnum.ALL:
            query = query.where(self.trans_model.type == filters.type)

        return query

    async def get_trans_user_ids(
        self, list_id: List[int]
    ) -> Sequence[TransactionModel]:
        smtp = select(self.trans_model).where(self.trans_model.user_id.in_(list_id))
        result = await self.session.execute(smtp)
        daily_data = result.scalars().all()
        return daily_data

    async def get_aggregated_report(
        self, filters: TransactionFilter
    ) -> AggregateReport:
        # Запрос для агрегации
        base_aggr = []
        resul_report_aggr = {}
        if filters.status == APITypeStatusEnum.SUCCESSFUL:
            if filters.include_avg:
                base_aggr.append(
                    func.avg(self.trans_model.sum_pay).label(
                        TransactionFieldEnum.AVG_AMOUNT.value
                    )
                )
                resul_report_aggr.update({TransactionFieldEnum.AVG_AMOUNT.value: 0})
            if filters.include_max:
                base_aggr.append(
                    func.max(self.trans_model.sum_pay).label(
                        TransactionFieldEnum.MAX_AMOUNT.value
                    )
                )
                resul_report_aggr.update({TransactionFieldEnum.MAX_AMOUNT.value: 0})
            if filters.include_min:
                base_aggr.append(
                    func.min(self.trans_model.sum_pay).label(
                        TransactionFieldEnum.MIN_AMOUNT.value
                    )
                )
                resul_report_aggr.update({TransactionFieldEnum.MIN_AMOUNT.value: 0})
            if filters.include_total:
                base_aggr.append(
                    func.count(self.trans_model.id).label(
                        TransactionFieldEnum.TRANSACTION_COUNT.value
                    )
                )
                resul_report_aggr.update(
                    {TransactionFieldEnum.TRANSACTION_COUNT.value: 0}
                )
            if (
                filters.include_avg
                or filters.include_max
                or filters.include_min
                or filters.include_total
            ):
                agg_query = select(*base_aggr)
            else:
                agg_query = select(self.trans_model)

            filtered_query = await self.get_report_by_filter(agg_query, filters)
            result = await self.session.execute(filtered_query)
            row = result.fetchone()
            for field in resul_report_aggr.keys():
                resul_report_aggr.update(
                    {field: float(row._get_by_key_impl_mapping(field))}
                )
            return AggregateReport(**resul_report_aggr)
        return AggregateReport()

    async def get_daily_shifts(self, filters: TransactionFilter):
        """
        Возвращает ежедневные суммы транзакций с процентным изменением
        относительно предыдущего дня.
        """
        # Применяем фильтры к базовому запросу (это должен быть запрос с WHERE условиями)
        cte_filtered = await self.get_report_by_filter(
            select(self.trans_model.date_pay, self.trans_model.sum_pay), filters
        )
        cte_filtered = cte_filtered.cte(
            name=TransactionFieldEnum.FILTERED_TRANSACTION.value
        )
        # Агрегируем по дням
        day_trunc_expr = func.date_trunc(
            TransactionFieldEnum.DAY.value, cte_filtered.c.date_pay
        )
        base_query = (
            select(
                day_trunc_expr.label(TransactionFieldEnum.DAY_DATE.value),
                func.sum(cte_filtered.c.sum_pay).label(
                    TransactionFieldEnum.DAILY_TOTAL.value
                ),
                func.count().label(TransactionFieldEnum.DAILY_COUNT.value),
            )
            .select_from(cte_filtered)
            .group_by(day_trunc_expr)
        )

        cte_daily_totals = base_query.cte(name=TransactionFieldEnum.DAILY_TOTALS.value)
        # Добавляем LAG и вычисляем процентное изменение
        with_prev = (
            select(
                cte_daily_totals.c.day_date,
                cte_daily_totals.c.daily_total,
                cte_daily_totals.c.daily_count,
                func.lag(cte_daily_totals.c.daily_total)
                .over(order_by=cte_daily_totals.c.day_date)
                .label(TransactionFieldEnum.PREV_DAY_TOTAL.value),
            )
            .select_from(cte_daily_totals)
            .subquery()
        )

        # Вычисляем percentage_change
        final_query = (
            select(
                with_prev.c.day_date,
                with_prev.c.daily_total,
                with_prev.c.daily_count,
                with_prev.c.prev_day_total,
                case(
                    (with_prev.c.prev_day_total.is_(None), literal_column("NULL")),
                    (with_prev.c.prev_day_total == 0, literal_column("NULL")),
                    else_=func.round(
                        (
                            (with_prev.c.daily_total - with_prev.c.prev_day_total)
                            / with_prev.c.prev_day_total
                        )
                        * 100,
                        2,
                    ),
                ).label(TransactionFieldEnum.PERCENTAGE_CHANGE.value),
            )
            .select_from(with_prev)
            .order_by(with_prev.c.day_date)
        )
        result = await self.session.execute(final_query)
        daily_data = result.fetchall()

        return [
            DailyShift(
                date=row.day_date.date().isoformat(),
                total_amount=float(row.daily_total) if row.daily_total else None,
                count=row.daily_count,
                percent_change=(
                    float(row.percentage_change) if row.prev_day_total else None
                ),
            )
            for row in daily_data
        ]
