#!/usr/bin/env python
"""
インディーズミュージックプラットフォーム サーバー起動スクリプト (問題解決用)

このスクリプトは、環境変数を適切に設定し、FirebaseとAWSの初期化をコントロールすることで
バックエンドサーバーを確実に起動するためのものです。
"""
import os
import sys
import uvicorn
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
logger = logging.getLogger("startup_script")

# 環境情報の出力
logger.info(f"Python Version: {sys.version}")
logger.info(f"Working Directory: {os.getcwd()}")

# 環境変数設定 - 開発モード用
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

try:
    # アプリケーションをインポート
    logger.info("アプリケーションをインポートします...")
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
        server.run()
except Exception as e:
    logger.error(f"エラーが発生しました: {e}")
    traceback.print_exc()
    sys.exit(1)
