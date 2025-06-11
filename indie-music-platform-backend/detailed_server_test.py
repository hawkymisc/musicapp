
"""
バックエンドサーバー起動テスト - 詳細ログ
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

# サーバー起動
try:
    logger.info("--- Uvicornサーバーの起動を試みます ---")
    logger.info("デバッグレベルで詳細情報を出力します")
    
    if __name__ == "__main__":
        logger.info("uvicorn.run()を呼び出します...")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
except Exception as e:
    logger.error(f"サーバー起動エラー: {e}")
    logger.error("詳細なエラー情報:")
    traceback.print_exc()
    sys.exit(1)
