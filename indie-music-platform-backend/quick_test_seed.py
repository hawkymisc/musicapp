#!/usr/bin/env python3
"""
クイックテスト用のSeedデータ作成
"""

import sys
import os
import uuid
from datetime import datetime, date
from decimal import Decimal

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.user import User
from app.schemas.user import UserRole
from app.models.track import Track
from app.models.purchase import Purchase, PaymentMethod, PurchaseStatus


def quick_test():
    """クイックテスト"""
    print("🔧 テーブルを作成中...")
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        print("🌱 テストデータを作成中...")
        
        # テストアーティストを作成
        artist = User(
            email="quick_artist@example.com",
            display_name="クイックアーティスト",
            firebase_uid=f"quick_artist_{uuid.uuid4().hex[:8]}",
            user_role=UserRole.ARTIST,
            is_verified=True
        )
        session.add(artist)
        session.flush()
        
        # テスト楽曲を作成
        track = Track(
            title="クイックテスト楽曲",
            description="これはクイックテスト用の楽曲です。",
            genre="テスト",
            cover_art_url="https://example.com/test.jpg",
            audio_file_url="https://example.com/test.mp3",
            duration=120,
            price=Decimal("100.0"),
            release_date=date.today(),
            artist_id=artist.id,
            is_public=True,
            play_count=1
        )
        session.add(track)
        
        session.commit()
        
        print("✅ テストデータ作成完了!")
        print(f"   アーティスト: {artist.display_name}")
        print(f"   楽曲: {track.title}")
        
        # 確認
        print(f"\n📊 現在のデータ:")
        print(f"   ユーザー数: {session.query(User).count()}")
        print(f"   楽曲数: {session.query(Track).count()}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ エラー: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    quick_test()