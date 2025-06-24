from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

# ロガー設定
logger = logging.getLogger(__name__)

# データベースエンジンの作成
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 接続確認
)

# セッションローカルの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# データベーステーブルの作成
def create_tables():
    try:
        # モデルのベースクラスをインポート
        from app.models.base import Base
        # 全モデルをインポートしてメタデータに登録
        from app.models.user import User
        from app.models.track import Track
        from app.models.purchase import Purchase
        from app.models.play_history import PlayHistory
        
        Base.metadata.create_all(bind=engine)
        logger.info("データベーステーブルが正常に作成されました")
    except Exception as e:
        logger.error(f"データベーステーブルの作成に失敗しました: {str(e)}")
        raise


# FastAPI依存性注入用のデータベースセッション取得関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
