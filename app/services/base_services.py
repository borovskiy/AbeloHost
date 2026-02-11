import logging

from sqlalchemy.ext.asyncio import AsyncSession


class BaseServices:
    def __init__(self, session: AsyncSession):
        self.log = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {"component": self.__class__.__name__}
        )
        self.session = session
