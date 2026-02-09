import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.base import BaseModel
from app.core.settings import settings

import app.models
config = context.config
DATABASE_URL = settings.DATABASE_URL
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = BaseModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Sync функция для conn.run_sync()."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode (async)."""
    engine: AsyncEngine = create_async_engine(DATABASE_URL, future=True)

    async with engine.connect() as conn:
        await conn.run_sync(do_run_migrations)

    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
