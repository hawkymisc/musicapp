import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv

# プロジェクトパスをシステムパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# .envファイルを読み込む
load_dotenv()

# アプリケーションのモデルをインポート
from app.models.base import Base
from app.models.user import User
from app.models.track import Track
from app.models.purchase import Purchase
from app.models.play_history import PlayHistory

# alembicの設定
config = context.config

# 環境変数からデータベースURLを設定
config.set_main_option(
    "sqlalchemy.url",
    f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@"
    f"{os.environ.get('POSTGRES_SERVER')}:{os.environ.get('POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}"
)

# Alembicによるログの設定
fileConfig(config.config_file_name)

# モデルのメタデータをTarget Metadataとして設定
target_metadata = Base.metadata


def run_migrations_offline():
    """
    オフラインマイグレーションを実行
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


def run_migrations_online():
    """
    オンラインマイグレーションを実行
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


