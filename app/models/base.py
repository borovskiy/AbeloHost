from sqlalchemy import func, Integer, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    """
    Основная модель с временем сохранения и ид
    Можно делать миксином но тут не стал
    """
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[int] = mapped_column(
        BigInteger,
        server_default=func.extract('epoch', func.now()),
        nullable=False
    )
    updated_at: Mapped[int] = mapped_column(
        BigInteger,
        server_default=func.extract('epoch', func.now()),
        nullable=False
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
