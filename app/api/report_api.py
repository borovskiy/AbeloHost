from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.report_schema import TransactionFilter
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

# @router.get("/report/by-country", status_code=201, response_model=TokenAccessSchemaRes)
# async def get_token(
#         user_auth_serv: Annotated[UserAuthServices, Depends(user_auth_services)],
#         model_user: TokenAccessSchemaReq,
# ):
#     """Create auth token"""
#     return await user_auth_serv.login_user(user_email=model_user.email, user_password_hash=model_user.hashed_password)
