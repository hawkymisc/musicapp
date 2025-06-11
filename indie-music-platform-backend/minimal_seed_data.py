#!/usr/bin/env python3
"""
最小限のSeedデータ作成スクリプト（テスト用）

使用方法:
    python minimal_seed_data.py
"""

import sys
import os
import uuid
from datetime import datetime, date
from decimal import Decimal

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.user import UserRole
from app.models.track import Track
from app.models.purchase import Purchase, PaymentMethod, PurchaseStatus


def create_minimal_seed_data():
    """最小限のSeedデータを作成"""
    session = SessionLocal()
    
    try:
        print("🌱 最小限のSeedデータを作成します...")
        
        # テストアーティストを作成
        test_artist = User(
            email="test_artist@example.com",
            display_name="テストアーティスト",
            firebase_uid=f"test_artist_uid_{uuid.uuid4().hex[:8]}",
            user_role=UserRole.ARTIST,
            is_verified=True
        )
        session.add(test_artist)
        session.flush()
        
        # テストリスナーを作成
        test_listener = User(
            email="test_listener@example.com",
            display_name="テストリスナー",
            firebase_uid=f"test_listener_uid_{uuid.uuid4().hex[:8]}",
            user_role=UserRole.LISTENER,
            is_verified=True
        )
        session.add(test_listener)
        session.flush()
        
        # テスト楽曲を作成
        test_track = Track(
            title="テスト楽曲",
            description="これはテスト用の楽曲です。",
            genre="ポップ",
            cover_art_url="https://example.com/covers/test_track.jpg",
            audio_file_url="https://example.com/audio/test_track.mp3",
            duration=180,
            price=Decimal("300.0"),
            release_date=date.today(),
            artist_id=test_artist.id,
            is_public=True,
            play_count=100
        )
        session.add(test_track)
        session.flush()
        
        # テスト購入履歴を作成
        test_purchase = Purchase(
            user_id=test_listener.id,
            track_id=test_track.id,
            amount=300.0,
            purchase_date=datetime.utcnow(),
            payment_method=PaymentMethod.CREDIT_CARD,
            transaction_id=f"test_txn_{uuid.uuid4().hex[:16]}",
            status=PurchaseStatus.COMPLETED
        )
        session.add(test_purchase)
        
        session.commit()
        
        print("✅ 最小限のSeedデータを作成しました:")
        print(f"   - アーティスト: {test_artist.display_name} ({test_artist.email})")
        print(f"   - リスナー: {test_listener.display_name} ({test_listener.email})")
        print(f"   - 楽曲: {test_track.title}")
        print(f"   - 購入履歴: 1件")
        
        return {
            "artist": test_artist,
            "listener": test_listener,
            "track": test_track,
            "purchase": test_purchase
        }
        
    except Exception as e:
        session.rollback()
        print(f"❌ エラーが発生しました: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    create_minimal_seed_data()