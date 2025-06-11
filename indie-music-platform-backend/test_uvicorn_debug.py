
"""
バックエンドサーバー起動テスト - Uvicornの詳細デバッグ
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

# 環境変数設定
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['AWS_REGION'] = 'us-east-1'
logger.info("環境変数を設定しました")

# Firebaseのモック
logger.info("Firebaseモジュールのモック化")
import sys
sys.modules['firebase_admin'] = type('MockFirebase', (), {'initialize_app': lambda x: None})
sys.modules['firebase_admin.auth'] = type('MockFirebaseAuth', (), {
    'verify_id_token': lambda token, **kwargs: {'uid': 'test_uid'} if token else None
})
sys.modules['firebase_admin.credentials'] = type('MockFirebaseCredentials', (), {
    'Certificate': lambda path: None
})

try:
    logger.info("FastAPIとuvicornのインポート")
    from fastapi import FastAPI
    import uvicorn
    
    # 最小限のFastAPIアプリケーション
    app = FastAPI(title="テストサーバー")
    
    @app.get("/")
    async def root():
        return {"message": "Hello World"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    # サーバー起動をラップして詳細なエラー情報を取得
    if __name__ == "__main__":
        try:
            logger.info("uvicorn.run()を呼び出します...")
            logger.info("引数: app={}, host={}, port={}, log_level={}".format(
                app, "127.0.0.1", 8000, "debug"
            ))
            
            # uvicornの内部構造を詳細に追跡
            import inspect
            
            # Config, Server, Applicationのクラスを詳しく調べる
            logger.info("uvicorn.Config クラスの検査:")
            config_source = inspect.getsource(uvicorn.Config)
            logger.info(f"Config クラス定義: {config_source[:200]}...")
            
            # Configインスタンスを作成して詳細を追跡
            logger.info("uvicorn.Config インスタンスの作成")
            config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="debug")
            logger.info(f"Config インスタンス: {config}")
            
            # サーバーインスタンスを作成して詳細を追跡
            logger.info("uvicorn.Server インスタンスの作成")
            server = uvicorn.Server(config)
            logger.info(f"Server インスタンス: {server}")
            
            # 実行
            logger.info("server.run() の呼び出し")
            server.run()
        except Exception as e:
            logger.error(f"uvicorn起動エラー: {e}")
            logger.error("詳細なエラー情報:")
            traceback.print_exc()
except Exception as e:
    logger.error(f"全体的なエラー: {e}")
    logger.error("詳細なエラー情報:")
    traceback.print_exc()
    sys.exit(1)
