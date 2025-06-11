"""
テスト用の設定ファイル
"""
import os
import sys
from unittest.mock import patch, MagicMock

# Firebase初期化のモック化
firebase_admin_mock = MagicMock()
firebase_auth_mock = MagicMock()
firebase_credentials_mock = MagicMock()

sys.modules['firebase_admin'] = firebase_admin_mock
sys.modules['firebase_admin.auth'] = firebase_auth_mock
sys.modules['firebase_admin.credentials'] = firebase_credentials_mock

# Firebase認証関数のモック
def mock_verify_id_token(token, **kwargs):
    if token == "artist_token":
        return {"uid": "firebaseuid_artist"}
    elif token == "listener_token":
        return {"uid": "firebaseuid_listener"}
    else:
        raise Exception("Invalid token")

firebase_auth_mock.verify_id_token = mock_verify_id_token

# 環境変数の設定
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'test_secret_key'
os.environ['FIREBASE_CREDENTIALS_PATH'] = 'tests/mocks/firebase_credentials.json'
os.environ['FIREBASE_API_KEY'] = 'test_api_key'
os.environ['S3_BUCKET_NAME'] = 'test-bucket'
os.environ['S3_REGION'] = 'ap-northeast-1'
os.environ['STRIPE_API_KEY'] = 'test_stripe_key'
os.environ['STRIPE_WEBHOOK_SECRET'] = 'test_webhook_secret'
