import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
from unittest.mock import patch, MagicMock

# オリジナルの設定を保存
original_modules = {}
for mod_name in ['firebase_admin', 'firebase_admin.auth', 'firebase_admin.credentials']:
    if mod_name in sys.modules:
        original_modules[mod_name] = sys.modules[mod_name]

# Firebase関連のモジュールをモック化
firebase_admin_mock = MagicMock()
firebase_auth_mock = MagicMock()
firebase_credentials_mock = MagicMock()

# 検証関数のモック
def mock_verify_id_token(token, **kwargs):
    if token == "artist_token":
        return {"uid": "firebaseuid_artist"}
    elif token == "listener_token":
        return {"uid": "firebaseuid_listener"}
    else:
        raise Exception("Invalid token")

firebase_auth_mock.verify_id_token = mock_verify_id_token
sys.modules['firebase_admin'] = firebase_admin_mock
sys.modules['firebase_admin.auth'] = firebase_auth_mock
sys.modules['firebase_admin.credentials'] = firebase_credentials_mock

# テスト環境設定
import os
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# シンプルなテスト
def test_health_check():
    from app.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}

# テスト終了時に元のモジュールを復元
def teardown_module(module):
    for mod_name, mod in original_modules.items():
        sys.modules[mod_name] = mod
