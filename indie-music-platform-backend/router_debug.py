#!/usr/bin/env python
"""
インディーズミュージックプラットフォーム APIルーター診断

このスクリプトは、APIルーターの登録状況を詳細にログ出力します。
"""
import os
import sys
import uvicorn
import logging
from unittest.mock import MagicMock

# ロギング設定 - 詳細に出力
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('router_debug.log')
    ]
)
logger = logging.getLogger("router_debug")

# 環境変数設定 - テスト/開発環境用
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///./dev.db'
os.environ['AWS_ACCESS_KEY_ID'] = 'test-key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-secret'
os.environ['AWS_REGION'] = 'ap-northeast-1'
os.environ['S3_BUCKET_NAME'] = 'test-bucket'
firebase_credentials_path = os.path.join(os.getcwd(), 'tests/mocks/firebase_credentials.json')
os.environ['FIREBASE_CREDENTIALS_PATH'] = firebase_credentials_path
os.environ['STRIPE_API_KEY'] = 'test-stripe-key'
os.environ['STRIPE_WEBHOOK_SECRET'] = 'test-webhook-secret'

# AWS/botocoreモジュールのモック化
sys.modules['boto3'] = MagicMock()
class BotocoreMock(MagicMock):
    class exceptions(MagicMock):
        ClientError = Exception
sys.modules['botocore'] = BotocoreMock()
sys.modules['botocore.exceptions'] = BotocoreMock.exceptions
sys.modules['botocore.session'] = MagicMock()
sys.modules['botocore.client'] = MagicMock()

# Firebase関連モジュールのモック化
firebase_admin_mock = MagicMock()
firebase_auth_mock = MagicMock()
firebase_credentials_mock = MagicMock()
firebase_admin_mock.initialize_app = MagicMock(return_value=None)
firebase_auth_mock.verify_id_token = MagicMock(return_value={"uid": "test-uid"})
firebase_credentials_mock.Certificate = MagicMock(return_value=None)
sys.modules['firebase_admin'] = firebase_admin_mock
sys.modules['firebase_admin.auth'] = firebase_auth_mock
sys.modules['firebase_admin.credentials'] = firebase_credentials_mock

# すべてのAPIルーターをデバッグするためのフック関数
def debug_router_setup():
    from fastapi import APIRouter
    
    # APIRouterのオリジナルメソッドを保存
    original_include_router = APIRouter.include_router
    
    # APIRouterをオーバーライドしてデバッグログを追加
    def debug_include_router(self, router, *args, **kwargs):
        prefix = kwargs.get('prefix', '')
        tags = kwargs.get('tags', [])
        logger.debug(f"ルーター登録: prefix='{prefix}', tags={tags}, ルーター={router}")
        
        # 登録されているルートを詳細にログ出力
        for route in router.routes:
            path = prefix + route.path
            logger.debug(f"  - エンドポイント: {route.methods} {path}")
        
        # オリジナルメソッドを呼び出し
        return original_include_router(self, router, *args, **kwargs)
    
    # APIRouterのメソッドを置き換え
    APIRouter.include_router = debug_include_router
    logger.info("APIRouterのデバッグモードを有効化しました")

try:
    # APIRouterのデバッグ機能を有効化
    debug_router_setup()
    
    # アプリケーションをインポート
    logger.info("アプリケーションをインポートします...")
    from app.main import app
    logger.info("アプリケーションインポート成功")
    
    # アプリケーションのルートを表示
    logger.info("登録されているすべてのルート:")
    for route in app.routes:
        logger.info(f"  - {route}")
    
    # サーバー設定
    logger.info("Uvicornサーバーを設定します...")
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="debug"
    )
    server = uvicorn.Server(config)
    
    # サーバー起動
    if __name__ == "__main__":
        logger.info("開発サーバーを起動します...")
        print("💻 バックエンドサーバーが http://127.0.0.1:8000 で起動しました")
        print("Ctrl+Cで終了します")
        server.run()
except Exception as e:
    logger.error(f"エラーが発生しました: {e}", exc_info=True)
    sys.exit(1)
