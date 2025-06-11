import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
from unittest.mock import patch, MagicMock

# テスト設定を先にインポート
import tests.test_settings

# Firebaseをモック
firebase_admin_mock = MagicMock()
firebase_auth_mock = MagicMock()

patch('firebase_admin.initialize_app', return_value=None).start()

from app.db.session import get_db
from app.main import app

# モデルのインポート（テーブル生成のため）
from app.models.base import Base
from app.models.user import User
from app.schemas.user import UserRole
from app.models.track import Track
import os
import datetime
import uuid


# テスト用のDB URL
TEST_DATABASE_URL = "sqlite:///:memory:"

# テスト用のエンジン
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# テスト用のセッションローカル
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


@pytest.fixture(scope="function")
def db():
    # テスト用のデータベーススキーマ作成
    Base.metadata.create_all(bind=engine)
    
    # セッションインスタンスを返す
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # テスト終了後にデータベースをクリア
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    # FastAPIのテストクライアント
    with TestClient(app=app) as c:
        yield c


@pytest.fixture(scope="function")
def test_artist(db):
    # テスト用のアーティストユーザー
    artist = User(
        id=str(uuid.uuid4()),
        email="artist@example.com",
        firebase_uid="firebaseuid_artist",
        display_name="Test Artist",
        user_role=UserRole.ARTIST,
        is_verified=True
    )
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist


@pytest.fixture(scope="function")
def test_listener(db):
    # テスト用のリスナーユーザー
    listener = User(
        id=str(uuid.uuid4()),
        email="listener@example.com",
        firebase_uid="firebaseuid_listener",
        display_name="Test Listener",
        user_role=UserRole.LISTENER,
        is_verified=True
    )
    db.add(listener)
    db.commit()
    db.refresh(listener)
    return listener


@pytest.fixture(scope="function")
def test_track(db, test_artist):
    # テスト用の楽曲
    track = Track(
        id=str(uuid.uuid4()),
        artist_id=test_artist.id,
        title="Test Track",
        description="This is a test track",
        genre="Rock",
        cover_art_url="https://example.com/cover.jpg",
        audio_file_url="https://example.com/audio.mp3",
        duration=180,  # 3分
        price=500,  # 500円
        release_date=datetime.date.today(),
        is_public=True,
        play_count=0
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


# Firebase認証のモック
@pytest.fixture(scope="function")
def mock_firebase_auth():
    def mock_verify_id_token(token, **kwargs):
        if token == "artist_token":
            return {"uid": "firebaseuid_artist"}
        elif token == "listener_token":
            return {"uid": "firebaseuid_listener"}
        else:
            raise Exception("Invalid token")
    
    # Firebase認証関数をモック
    with patch('firebase_admin.auth.verify_id_token', side_effect=mock_verify_id_token):
        yield
