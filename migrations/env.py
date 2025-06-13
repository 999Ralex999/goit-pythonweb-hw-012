import sys
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# 👇 Додаємо базу та моделі
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.config import settings
from app.models.base import Base
from app.models.user import User
from app.models.contact import Contact

# ⬇️ Конфіг Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ⬇️ Встановлюємо URL до бази (через sync драйвер!)
config.set_main_option("sqlalchemy.url", settings.DB_SYNC_URL)

# ⬇️ Метадата для автогенерації схем
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Міграції в offline-режимі (без з’єднання з базою)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Міграції в online-режимі (зі з’єднанням до бази)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
