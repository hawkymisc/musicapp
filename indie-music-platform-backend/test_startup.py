#!/usr/bin/env python
"""
インディーズミュージックプラットフォーム テスト環境サーバー起動スクリプト

このスクリプトは、依存関係の問題を解決するために、AWS/Firebase等の外部サービスをモック化し、
環境変数を適切に設定した上でバックエンドサーバーを起動します。
"""
import os
import sys
import uvicorn
import logging
from unittest.mock import MagicMock
import traceback

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_startup.log')
    ]
)
logger = logging.getLogger("test_startup")

# 環境情報の出力
logger.info(f"Python Version: {sys.version}")
logger.info(f"Working Directory: {os.getcwd()}")
logger.info(f"sys.path: {sys.path}")

# 環境変数設定 - テスト/開発環境用
os.environ['TESTING'] = 'True'  # テストモードでFirebase初期化をスキップ
os.environ['DATABASE_URL'] = 'sqlite:///./dev.db'  # 開発用SQLiteデータベース

# AWS関連の環境変数（テスト用ダミー値）
os.environ['AWS_ACCESS_KEY_ID'] = 'test-key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-secret'
os.environ['AWS_REGION'] = 'ap-northeast-1'
os.environ['S3_BUCKET_NAME'] = 'test-bucket'

# Firebase認証情報
firebase_credentials_path = os.path.join(os.getcwd(), 'tests/mocks/firebase_credentials.json')
os.environ['FIREBASE_CREDENTIALS_PATH'] = firebase_credentials_path

# Stripe決済関連（テスト用ダミー値）
os.environ['STRIPE_API_KEY'] = 'test-stripe-key'
os.environ['STRIPE_WEBHOOK_SECRET'] = 'test-webhook-secret'

logger.info("環境変数を設定しました:")
for key in ['TESTING', 'DATABASE_URL', 'AWS_REGION', 'FIREBASE_CREDENTIALS_PATH']:
    logger.info(f"  {key}={os.environ.get(key)}")

# AWS/botocoreモジュールのモック化（S3接続問題回避）
logger.info("AWS/Firebase関連モジュールをモック化します...")
sys.modules['boto3'] = MagicMock()

# botocoreモジュールのモック
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

# Firebaseモックの詳細設定
firebase_admin_mock.initialize_app = MagicMock(return_value=None)
firebase_auth_mock.verify_id_token = MagicMock(return_value={"uid": "test-uid"})
firebase_credentials_mock.Certificate = MagicMock(return_value=None)

sys.modules['firebase_admin'] = firebase_admin_mock
sys.modules['firebase_admin.auth'] = firebase_auth_mock
sys.modules['firebase_admin.credentials'] = firebase_credentials_mock

try:
    # キャッシュを無効化してアプリケーションをインポート
    logger.info("アプリケーションをインポートします...")
    # 既存のモジュールをアンロード
    if 'app.main' in sys.modules:
        del sys.modules['app.main']
    if 'app.api.router' in sys.modules:
        del sys.modules['app.api.router']
        
    # モジュールをリロード
    from app.main import app
    logger.info("アプリケーションインポート成功")
    
    # 明示的なサーバー設定
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
    logger.error(f"エラーが発生しました: {e}")
    traceback.print_exc()
    sys.exit(1)
