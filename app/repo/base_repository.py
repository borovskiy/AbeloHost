import logging
from abc import ABC
from typing import Generic, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepo(Generic[ModelType], ABC):
    def __init__(self, session: AsyncSession):
        self.log = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {"component": self.__class__.__name__}
        )
        self.session = session