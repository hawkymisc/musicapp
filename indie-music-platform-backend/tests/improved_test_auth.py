import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
from unittest.mock import patch, MagicMock

# Firebase関連のモジュールをモック化
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.auth'] = MagicMock()
sys.modules['firebase_admin.credentials'] = MagicMock()

# テスト環境設定を読み込む
import os
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# アプリケーションのインポート
from app.main import app
from app.db.session import get_db
from app.models.base import Base
from app.models.user import User
from app.schemas.user import UserRole

# インメモリSQLiteデータベース設定
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テスト用のデータベースセッション依存性
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# アプリケーションのデータベース依存性を上書き
app.dependency_overrides[get_db] = override_get_db

# テストクライアント
client = TestClient(app)

# Firebase認証のモック
def mock_verify_id_token(token, **kwargs):
    if token == "artist_token":
        return {"uid": "firebaseuid_artist"}
    elif token == "listener_token":
        return {"uid": "firebaseuid_listener"}
    else:
        raise Exception("Invalid token")

# Firebase認証関数をモック
sys.modules['firebase_admin.auth'].verify_id_token = mock_verify_id_token

# テスト前の設定
def setup_module(module):
    # テーブル作成
    Base.metadata.create_all(bind=engine)
    
    # テストユーザーの作成
    db = TestingSessionLocal()
    
    # アーティストユーザー
    artist = User(
        id="test-artist-id",
        email="artist@example.com",
        firebase_uid="firebaseuid_artist",
        display_name="Test Artist",
        user_role=UserRole.ARTIST,
        is_verified=True
    )
    
    # リスナーユーザー
    listener = User(
        id="test-listener-id",
        email="listener@example.com",
        firebase_uid="firebaseuid_listener",
        display_name="Test Listener",
        user_role=UserRole.LISTENER,
        is_verified=True
    )
    
    db.add(artist)
    db.add(listener)
    db.commit()
    db.close()

# テスト終了後のクリーンアップ
def teardown_module(module):
    Base.metadata.drop_all(bind=engine)

# テスト：ユーザー登録
def test_register_user():
    user_data = {
        "email": "newuser@example.com",
        "firebase_uid": "firebaseuid_new",
        "display_name": "New User",
        "user_role": UserRole.LISTENER.value
    }
    
    response = client.post(
        "/api/v1/auth/register",
        json=user_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["display_name"] == user_data["display_name"]
    assert data["user_role"] == user_data["user_role"]

# テスト：ヘルスチェック
def test_health_check():
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}

# テスト：現在のユーザー情報の取得
def test_get_current_user():
    # リスナーとして認証するヘッダー
    headers = {"Authorization": "Bearer listener_token"}
    
    # 現在のユーザー情報を取得
    response = client.get(
        "/api/v1/auth/me",
        headers=headers
    )
    
    # 応答のステータスコードを確認
    assert response.status_code == status.HTTP_200_OK
    
    # 応答データを確認
    data = response.json()
    assert data["email"] == "listener@example.com"
    assert data["display_name"] == "Test Listener"
    assert data["user_role"] == UserRole.LISTENER.value
