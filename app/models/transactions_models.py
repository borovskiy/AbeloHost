from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Integer, ForeignKey, DECIMAL, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.enum_status import TypeStatusEnum
from app.enums.enum_type_pay import TypePayEnum
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user_models import UserModel


class TransactionModel(BaseModel):
    __tablename__ = "transactions"

    date_pay: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    sum_pay: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    status: Mapped[TypeStatusEnum] = mapped_column(Enum(TypeStatusEnum), nullable=False)
    type: Mapped[TypePayEnum] = mapped_column(Enum(TypePayEnum), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="transactions")
