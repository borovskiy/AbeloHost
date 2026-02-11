from fastapi import Depends
from sqlalchemy import select, func, cast, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from datetime import datetime

from app.core.db_connector import get_db
from app.enums.enum_aggregate import TransactionFieldEnum
from app.enums.enum_status import APITypeStatusEnum
from app.enums.enum_type_pay import APITypePayEnum
from app.repo.transaction_repo import TransactionRepository
from app.schemas.report_schema import TransactionFilter, ReportResponse, DailyShift
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


async def report_services(session: AsyncSession = Depends(get_db)) -> ReportServices:
    return ReportServices(session)
