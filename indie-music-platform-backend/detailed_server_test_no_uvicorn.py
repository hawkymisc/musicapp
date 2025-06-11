
"""
バックエンドサーバー起動テスト - 詳細ログ (Uvicornなし)
"""
import os
import sys
import logging
import traceback

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("server_test")

# 環境情報の出力
logger.info(f"Python Version: {sys.version}")
logger.info(f"Python Path: {sys.executable}")
logger.info(f"Working Directory: {os.getcwd()}")
logger.info(f"sys.path: {sys.path}")

# 環境変数設定
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
logger.info("環境変数を設定しました")

# 依存関係のバージョン確認
try:
    logger.info("--- 依存パッケージのバージョン確認 ---")
    
    import fastapi
    logger.info(f"FastAPI: {fastapi.__version__}")
    
    import uvicorn
    logger.info(f"Uvicorn: {uvicorn.__version__}")
    
    import sqlalchemy
    logger.info(f"SQLAlchemy: {sqlalchemy.__version__}")
    
    import pydantic
    logger.info(f"Pydantic: {pydantic.__version__}")
    
    logger.info("依存パッケージの確認が完了しました")
except ImportError as e:
    logger.error(f"パッケージのインポートエラー: {e}")
    traceback.print_exc()

# FastAPIアプリケーションの作成
try:
    logger.info("--- 最小限のFastAPIアプリの作成 ---")
    from fastapi import FastAPI
    
    app = FastAPI(title="テストサーバー")
    
    @app.get("/")
    async def root():
        return {"message": "Hello World"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    logger.info("FastAPIアプリケーションの作成が完了しました")
except Exception as e:
    logger.error(f"FastAPIアプリケーション作成エラー: {e}")
    traceback.print_exc()

# 実際のプロジェクトのインポートテスト
try:
    logger.info("--- プロジェクトコードのインポートテスト ---")
    
    # app.core.config
    logger.info("app.core.config のインポート...")
    from app.core.config import settings
    logger.info(f"設定インポート成功: DATABASE_URL={settings.DATABASE_URL}")
    
    # app.db.session
    logger.info("app.db.session のインポート...")
    from app.db.session import get_db, create_tables
    logger.info("データベース接続設定インポート成功")
    
    # app.models
    logger.info("app.models のインポート...")
    from app.models.user import User, UserRole
    from app.models.track import Track
    logger.info("モデルインポート成功")
    
    # app.core.security (問題が疑われる部分)
    logger.info("app.core.security のインポート...")
    import inspect
    
    try:
        from app.core.security import get_current_user, get_current_active_user
        logger.info("security.py インポート成功")
    except Exception as security_error:
        logger.error(f"security.py インポートエラー: {security_error}")
        
        # security.pyファイルの内容を表示
        try:
            with open("app/core/security.py", "r") as file:
                security_content = file.read()
                logger.info("security.py の内容:")
                logger.info(security_content)
        except Exception as read_error:
            logger.error(f"security.py の内容を読み取れませんでした: {read_error}")
    
    # app.main
    logger.info("app.main のインポート...")
    try:
        from app.main import app as main_app
        logger.info("app.main インポート成功")
    except Exception as main_error:
        logger.error(f"app.main インポートエラー: {main_error}")
    
    logger.info("プロジェクトコードのインポートテスト完了")
except Exception as e:
    logger.error(f"プロジェクトコードのインポートエラー: {e}")
    traceback.print_exc()

logger.info("詳細サーバーテスト完了")
