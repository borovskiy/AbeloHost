from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.transactions_models import TransactionModel


class UserModel(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))

    # Relationships
    transactions: Mapped[list["TransactionModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
