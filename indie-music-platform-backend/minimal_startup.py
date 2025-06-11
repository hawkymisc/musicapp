#!/usr/bin/env python
"""
インディーズミュージックプラットフォーム 最小限サーバー起動スクリプト

このスクリプトは、最小限の設定でサーバーを起動します。
外部依存関係を単純化し、まずは起動できることを確認します。
"""
import os
import sys
import logging
from unittest.mock import MagicMock

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('minimal_startup.log')
    ]
)
logger = logging.getLogger("minimal_startup")

# 環境変数設定 - テスト環境用
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# AWS関連のモック化
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()

# Firebase関連のモック化
firebase_admin_mock = MagicMock()
firebase_auth_mock = MagicMock()
firebase_credentials_mock = MagicMock()

sys.modules['firebase_admin'] = firebase_admin_mock
sys.modules['firebase_admin.auth'] = firebase_auth_mock
sys.modules['firebase_admin.credentials'] = firebase_credentials_mock

# 最小限のFastAPIアプリケーション
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="インディーズミュージックアプリAPI - 最小限版")

@app.get("/")
async def root():
    return {"message": "サーバーが起動しました"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# サーバー起動
if __name__ == "__main__":
    logger.info("最小限サーバーを起動します...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
