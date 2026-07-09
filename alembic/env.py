from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 🆕 在檔案頂端補上匯入
from asyncio import run
from sqlalchemy.ext.asyncio import AsyncEngine

import os
import sys

# 將專案根目錄加入 Python 搜尋路徑，確保能匯入 app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 匯入你的 Base 與所有模型
from app.database import Base
from app import models  # 確保模型被讀取到

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """在『離線模式』下執行遷移（只生成 SQL 腳本，不連線資料庫）"""
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在『連線模式』下執行遷移（直接更新資料庫）"""
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    if isinstance(connectable, AsyncEngine):

        async def run_async():
            async with connectable.connect() as connection:
                await connection.run_sync(do_run_migrations)

        run(run_async())
    else:
        # 如果是一般同步引擎（保留相容性）
        with connectable.connect() as connection:
            do_run_migrations(connection)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # 連線模式則呼叫我們升級好的非同步版本
    run_migrations_online()
