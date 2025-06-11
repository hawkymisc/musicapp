#!/usr/bin/env python
"""
インディーズミュージックプラットフォーム マイグレーション付き起動スクリプト

このスクリプトは:
1. データベースマイグレーションを実行
2. テスト用サンプルデータを挿入（オプション）
3. アプリケーションを起動

使用方法:
python run_with_migration.py [--with-sample-data]
"""
import os
import sys
import uvicorn
import logging
import argparse
import subprocess
from unittest.mock import MagicMock
import traceback
from datetime import date, datetime

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app_startup.log')
    ]
)
logger = logging.getLogger("app_startup")

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

def run_migrations():
    """Alembicマイグレーションを実行"""
    logger.info("データベースマイグレーションを実行します...")
    try:
        # alembic.iniファイルを使用してマイグレーションを実行
        result = subprocess.run(['alembic', 'upgrade', 'head'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("マイグレーションが成功しました:")
            logger.info(result.stdout)
        else:
            logger.error("マイグレーションでエラーが発生しました:")
            logger.error(result.stderr)
    except Exception as e:
        logger.error(f"マイグレーション実行中にエラーが発生しました: {e}")
        traceback.print_exc()

def create_sample_data():
    """テスト用のサンプルデータを作成"""
    logger.info("サンプルデータを作成しています...")
    
    # SQLAlchemyのモデルをインポート
    from app.models.user import User
    from app.models.track import Track
    from app.schemas.user import UserRole
    from app.db.session import get_db
    from sqlalchemy.orm import Session
    from sqlalchemy import inspect
    
    db = next(get_db())
    
    try:
        # テーブルが存在するか確認
        inspector = inspect(db.bind)
        if not inspector.has_table("user") or not inspector.has_table("track"):
            logger.error("テーブルが存在しません。マイグレーションが正常に実行されていない可能性があります。")
            return
        
        # すでにデータがあるか確認
        user_count = db.query(User).count()
        track_count = db.query(Track).count()
        
        if user_count > 0 or track_count > 0:
            logger.info(f"すでにデータが存在します。ユーザー: {user_count}、楽曲: {track_count}")
            return
        
        # テスト用ユーザーの作成
        test_artist = User(
            id="artist1",
            email="artist@example.com",
            firebase_uid="firebase_artist1",
            display_name="テストアーティスト",
            user_role=UserRole.ARTIST,
            is_verified=True
        )
        
        test_listener = User(
            id="listener1",
            email="listener@example.com",
            firebase_uid="firebase_listener1",
            display_name="テストリスナー",
            user_role=UserRole.LISTENER,
            is_verified=True
        )
        
        db.add(test_artist)
        db.add(test_listener)
        db.flush()
        
        # テスト用楽曲の作成
        tracks = [
            Track(
                id="track1",
                artist_id="artist1",
                title="夏の終わりに",
                description="夏の終わりの切ない気持ちを表現した楽曲です。",
                genre="ポップス",
                cover_art_url="https://example.com/covers/summer_end.jpg",
                audio_file_url="https://example.com/tracks/summer_end.mp3",
                duration=210,
                price=300,
                release_date=date(2025, 1, 15),
                is_public=True,
                play_count=120
            ),
            Track(
                id="track2",
                artist_id="artist1",
                title="星空のセレナーデ",
                description="星空の下で奏でるセレナーデをイメージした曲です。",
                genre="バラード",
                cover_art_url="https://example.com/covers/starry_night.jpg",
                audio_file_url="https://example.com/tracks/starry_night.mp3",
                duration=240,
                price=350,
                release_date=date(2025, 2, 1),
                is_public=True,
                play_count=85
            ),
            Track(
                id="track3",
                artist_id="artist1",
                title="雨の日の窓辺",
                description="雨の日の静かな窓辺での時間を表現しています。",
                genre="ジャズ",
                cover_art_url="https://example.com/covers/rainy_window.jpg",
                audio_file_url="https://example.com/tracks/rainy_window.mp3",
                duration=180,
                price=250,
                release_date=date(2025, 2, 15),
                is_public=True,
                play_count=62
            )
        ]
        
        for track in tracks:
            db.add(track)
        
        db.commit()
        logger.info(f"サンプルデータを作成しました: {len(tracks)}曲")
    
    except Exception as e:
        db.rollback()
        logger.error(f"サンプルデータ作成中にエラーが発生しました: {e}")
        traceback.print_exc()
    finally:
        db.close()

def start_app(with_sample_data=False):
    """アプリケーションを起動"""
    try:
        # モジュールのキャッシュをクリア
        if 'app.main' in sys.modules:
            del sys.modules['app.main']
        if 'app.api.router' in sys.modules:
            del sys.modules['app.api.router']
            
        # マイグレーションの実行
        run_migrations()
        
        # サンプルデータの作成
        if with_sample_data:
            create_sample_data()
            
        # アプリケーションのインポート
        logger.info("アプリケーションをインポートします...")
        from app.main import app
        logger.info("アプリケーションインポート成功")
        
        # 明示的なサーバー設定
        logger.info("Uvicornサーバーを設定します...")
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        # サーバー起動
        logger.info("開発サーバーを起動します...")
        print("💻 バックエンドサーバーが http://127.0.0.1:8000 で起動しました")
        print("Ctrl+Cで終了します")
        server.run()
        
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="アプリケーション起動スクリプト")
    parser.add_argument("--with-sample-data", action="store_true", help="サンプルデータを作成する")
    args = parser.parse_args()
    
    start_app(with_sample_data=args.with_sample_data)
