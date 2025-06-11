
"""
テスト用のデータベース初期化スクリプト
"""
import os
import sys
import logging
import traceback

# テスト環境設定
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'

# ロガーの設定
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # データベース関連のインポート
    from app.db.session import get_db, create_tables
    from app.models.user import User, UserRole
    from app.models.track import Track
    import uuid
    import datetime
    from sqlalchemy.orm import Session
    
    # テーブル作成
    print("データベーステーブルを作成しています...")
    create_tables()
    print("データベーステーブルの作成が完了しました")
    
    # テストデータ登録
    print("テストデータを作成しています...")
    
    # データベースセッションの取得
    db_generator = get_db()
    db: Session = next(db_generator)
    
    try:
        # アーティストユーザー
        artist = User(
            id=str(uuid.uuid4()),
            email="artist@example.com",
            firebase_uid="firebaseuid_artist",
            display_name="Test Artist",
            user_role=UserRole.ARTIST,
            is_verified=True
        )
        
        # リスナーユーザー
        listener = User(
            id=str(uuid.uuid4()),
            email="listener@example.com",
            firebase_uid="firebaseuid_listener",
            display_name="Test Listener",
            user_role=UserRole.LISTENER,
            is_verified=True
        )
        
        db.add(artist)
        db.add(listener)
        db.commit()
        
        # 楽曲データ
        track = Track(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
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
        
        print(f"テストアーティスト '{artist.display_name}' を作成しました (ID: {artist.id})")
        print(f"テストリスナー '{listener.display_name}' を作成しました (ID: {listener.id})")
        print(f"テスト楽曲 '{track.title}' を作成しました (ID: {track.id})")
        
    finally:
        db.close()
    
    print("テストデータの作成が完了しました")
        
except Exception as e:
    print(f"エラーが発生しました: {e}")
    traceback.print_exc()
    sys.exit(1)
