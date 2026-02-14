from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import date, timedelta
from typing import Optional, List, Literal

from starlette import status

from app.enums.enum_status import APITypeStatusEnum
from app.enums.enum_type_pay import APITypePayEnum


class TransactionFilter(BaseModel):
    start_date: Optional[str] = Field(
        default=None,
        description="Начало периода (формат: YYYY-MM-DD)"
    )
    end_date: Optional[str] = Field(
        default=None,
        description="Конец периода (формат: YYYY-MM-DD)"
    )
    status: APITypeStatusEnum = APITypeStatusEnum.ALL
    type: APITypePayEnum = APITypePayEnum.ALL
    include_total: bool = False
    include_avg: bool = False
    include_min: bool = False
    include_max: bool = False
    include_daily_shift: bool = False
    full_info_data: bool = False
    @field_validator('start_date', mode='before')
    @classmethod
    def validate_start_date(cls, v):
        if v is None or v == '' or v == {}:
            return (date.today() - timedelta(days=30)).isoformat()
        return str(v)

    @field_validator('end_date', mode='before')
    @classmethod
    def validate_end_date(cls, v):
        if v is None or v == '' or v == {}:
            return date.today().isoformat()
        return str(v)

    @model_validator(mode='after')
    def validate_dates(self):
        """Проверяем, что начальная дата не позже конечной"""
        if self.start_date and self.end_date:
            start = date.fromisoformat(self.start_date)
            end = date.fromisoformat(self.end_date)
            if start > end:
                raise ValueError("start_date не может быть позже end_date")
        return self

    @property
    def start_date_parsed(self) -> date:
        return date.fromisoformat(self.start_date)

    @property
    def end_date_parsed(self) -> date:
        return date.fromisoformat(self.end_date)

    @model_validator(mode='after')
    def validate_aggregation_fields_with_status(self):
        """Проверяем, что поля агрегации могут быть True только при status=SUCCESSFUL"""
        aggregation_fields = ['include_total', 'include_avg', 'include_min', 'include_max']
        has_aggregation_enabled = any(getattr(self, field) for field in aggregation_fields)
        if has_aggregation_enabled and self.status != APITypeStatusEnum.SUCCESSFUL:
            enabled_fields = [field for field in aggregation_fields if getattr(self, field)]
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Поля агрегации {enabled_fields} могут быть включены только при status={APITypeStatusEnum.SUCCESSFUL}")
        return self

class CountryStatsFilter(BaseModel):
    sort_by: Literal["count", "total", "avg"] = Field(
        default="count",
        description="Метрика для сортировки: count, total, avg"
    )
    top_n: Optional[int] = Field(
        default=None,
        description="Ограничение количества стран",
        ge=1
    )

class AggregateReport(BaseModel):
    total_amount: Optional[float] = None
    transaction_count: Optional[float] = None
    avg_amount: Optional[float] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None

class CSVData(BaseModel):
    country: str
    list_id_user_country: List[int]

class CSVDataList(BaseModel):
    list_id_for_search: List[int] = []
    list_id_data_csv: List[CSVData] = []
    list_for_frame_user_country: List[dict] = []

class CountryStat(BaseModel):
    country: str
    transaction_count: int
    total_amount: float
    average_amount: float

class CountryReportResponse(BaseModel):
    stats: List[CountryStat]

class DailyShift(BaseModel):
    date: str
    total_amount: float
    count: int
    percent_change: Optional[float] = None


class ReportResponse(BaseModel):
    total_amount: Optional[float] = None
    transaction_count: Optional[float] = None
    avg_amount: Optional[float] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    daily_shifts: Optional[List[DailyShift]] = None
