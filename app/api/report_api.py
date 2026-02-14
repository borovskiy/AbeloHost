from typing import Annotated, Literal, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from app.schemas.report_schema import TransactionFilter, CountryStatsFilter, CountryStat
from app.services.report_service import ReportServices, report_services

router = APIRouter(
    prefix="/reports",
    tags=["Report"],
)


@router.get("/report", status_code=200)
async def register_user(
        report_serv: Annotated[ReportServices, Depends(report_services)],
        trans_filter: TransactionFilter = Depends(),
):
    """Получение репорта"""
    return await report_serv.get_all_report_by_filter(trans_filter)


@router.post("/report/by-country", status_code=200, response_model=List[CountryStat])
async def get_country_stats(
        report_serv: Annotated["ReportServices", Depends(report_services)],
        countries_file: Annotated[UploadFile, File(
            description="CSV файл с данными о странах (должен содержать колонки: user_id, country)"
        )],
        sort_by: Annotated[Literal["count", "total", "avg"], Form()] = "count",
        top_n: Annotated[int | None, Form()] = None,
):
    """
    Получение статистики по странам.
    Загружает файл с данными о странах пользователей и объединяет с транзакциями из БД.
    **Формат CSV файла:**
    ```
    user_id,country
    1,USA
    2,Russia
    3,Germany
    ```
    """
    # Валидация типа файла
    if not countries_file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Только CSV файлы разрешены"
        )
    # Чтение файла
    try:
        content = await countries_file.read()
        file_str = content.decode('utf-8')
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка чтения файла: {str(e)}"
        )
    # Создание фильтра
    filters = CountryStatsFilter(sort_by=sort_by, top_n=top_n)
    # Вызов сервиса
    return await report_serv.get_report_countre(
        countries_csv=file_str,
        filters=filters
    )
