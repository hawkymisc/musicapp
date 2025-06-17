#!/usr/bin/env python3
"""
QA環境専用のSeedデータ作成スクリプト

QAテストに特化したデータパターンを作成します。
- エッジケースを含むテストデータ
- 境界値テスト用のデータ
- E2Eテストシナリオに対応したデータ

使用方法:
    python qa_seed_data.py
    python qa_seed_data.py --reset  # データベースリセット付き
"""

import sys
import os
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.user import User
from app.schemas.user import UserRole
from app.models.track import Track
from app.models.purchase import Purchase, PaymentMethod, PurchaseStatus


def create_qa_seed_data(reset_db=False):
    """QA環境専用のSeedデータを作成
    
    Args:
        reset_db (bool): データベースをリセットするかどうか
    """
    # データベースリセット
    if reset_db:
        print("🗑️ データベースをリセットしています...")
        Base.metadata.drop_all(bind=engine)
    
    # テーブルを作成
    print("🔧 データベーステーブルを作成しています...")
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        print("🧪 QA環境専用Seedデータの作成を開始します...")
        
        # 既存データの確認
        try:
            existing_users = session.query(User).count()
            if existing_users > 0 and not reset_db:
                print(f"既に{existing_users}件のユーザーが存在します。重複を避けるためにスキップします。")
                print("データベースをリセットしたい場合は qa_seed_data.py --reset を使用してください。")
                return
        except:
            existing_users = 0
        
        # QA用リスナーユーザーの作成
        listeners = create_qa_listeners(session)
        print(f"✅ QAリスナー {len(listeners)}名を作成しました")
        
        # QA用アーティストユーザーの作成
        artists = create_qa_artists(session)
        print(f"✅ QAアーティスト {len(artists)}名を作成しました")
        
        # QA用楽曲の作成
        tracks = create_qa_tracks(session, artists)
        print(f"✅ QA楽曲 {len(tracks)}曲を作成しました")
        
        # QA用購入履歴の作成
        purchases = create_qa_purchases(session, listeners, tracks)
        print(f"✅ QA購入履歴 {len(purchases)}件を作成しました")
        
        session.commit()
        print("🎉 QA Seedデータの作成が完了しました！")
        
        # 作成されたデータの概要を表示
        print_qa_summary(session)
        
    except Exception as e:
        session.rollback()
        print(f"❌ エラーが発生しました: {e}")
        raise
    finally:
        session.close()


def create_qa_listeners(session: Session) -> list[User]:
    """QA用リスナーユーザーを作成（E2Eテスト対応）"""
    listeners_data = [
        # E2Eテスト用の固定アカウント
        {
            "email": "e2e_listener@example.com",
            "display_name": "E2Eテストリスナー",
            "firebase_uid": "e2e_listener_uid_fixed_12345"
        },
        {
            "email": "test_user_1@musicshelf.net",
            "display_name": "テストユーザー１",
            "firebase_uid": f"qa_listener_uid_{uuid.uuid4().hex[:8]}"
        },
        {
            "email": "test_user_2@musicshelf.net",
            "display_name": "テストユーザー２",
            "firebase_uid": f"qa_listener_uid_{uuid.uuid4().hex[:8]}"
        },
        # 境界値テスト用（長い名前）
        {
            "email": "very_long_email_address_for_testing_boundary_values@musicshelf.net",
            "display_name": "非常に長い表示名を持つテストユーザーで境界値をテストするためのアカウント",
            "firebase_uid": f"qa_listener_uid_{uuid.uuid4().hex[:8]}"
        },
        # 特殊文字テスト用
        {
            "email": "special_chars_test@musicshelf.net",
            "display_name": "特殊文字テスト用ユーザー 🎵 ♪ ♫",
            "firebase_uid": f"qa_listener_uid_{uuid.uuid4().hex[:8]}"
        }
    ]
    
    listeners = []
    for data in listeners_data:
        listener = User(
            email=data["email"],
            display_name=data["display_name"],
            firebase_uid=data["firebase_uid"],
            user_role=UserRole.LISTENER,
            is_verified=True
        )
        session.add(listener)
        listeners.append(listener)
    
    session.flush()
    return listeners


def create_qa_artists(session: Session) -> list[User]:
    """QA用アーティストユーザーを作成（E2Eテスト対応）"""
    artists_data = [
        # E2Eテスト用の固定アカウント
        {
            "email": "e2e_artist@example.com",
            "display_name": "E2Eテストアーティスト",
            "firebase_uid": "e2e_artist_uid_fixed_12345",
            "bio": "E2Eテスト用のアーティストアカウントです。"
        },
        # 通常のQAテスト用アーティスト
        {
            "email": "qa_artist_1@musicshelf.net",
            "display_name": "QAテストバンド",
            "firebase_uid": f"qa_artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "QAテスト用のバンドです。様々なテストシナリオに対応。"
        },
        {
            "email": "qa_artist_2@musicshelf.net",
            "display_name": "テストソロアーティスト",
            "firebase_uid": f"qa_artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "テスト用のソロアーティスト。楽曲アップロード機能のテストに使用。"
        },
        # 境界値テスト用（長いバイオ）
        {
            "email": "boundary_test_artist@musicshelf.net",
            "display_name": "境界値テストアーティスト",
            "firebase_uid": f"qa_artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "非常に長いバイオグラフィーを持つアーティストで、テキストフィールドの境界値をテストするためのアカウントです。" * 10
        },
        # 特殊ケース：未認証アーティスト
        {
            "email": "unverified_artist@musicshelf.net",
            "display_name": "未認証アーティスト",
            "firebase_uid": f"qa_artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "認証テスト用の未認証アーティスト。",
            "is_verified": False
        }
    ]
    
    artists = []
    for data in artists_data:
        artist = User(
            email=data["email"],
            display_name=data["display_name"],
            firebase_uid=data["firebase_uid"],
            user_role=UserRole.ARTIST,
            is_verified=data.get("is_verified", True)
        )
        session.add(artist)
        artists.append(artist)
    
    session.flush()
    return artists


def create_qa_tracks(session: Session, artists: list[User]) -> list[Track]:
    """QA用楽曲を作成（テストシナリオ対応）"""
    tracks_data = [
        # E2Eテスト用の固定楽曲
        {
            "title": "E2Eテスト楽曲",
            "description": "E2Eテスト用の楽曲です。購入・再生機能のテストに使用。",
            "genre": "テスト",
            "duration": 180,
            "price": 500.0,
            "artist_index": 0,
            "cover_art_url": "https://example.com/qa/covers/e2e_test_track.jpg",
            "audio_file_url": "https://example.com/qa/audio/e2e_test_track.mp3"
        },
        
        # 通常のQAテスト楽曲
        {
            "title": "QAテストソング",
            "description": "QAテスト用の楽曲。様々な機能テストに対応。",
            "genre": "ポップ",
            "duration": 240,
            "price": 300.0,
            "artist_index": 1,
            "cover_art_url": "https://example.com/qa/covers/qa_test_song.jpg",
            "audio_file_url": "https://example.com/qa/audio/qa_test_song.mp3"
        },
        
        # 価格境界値テスト用楽曲
        {
            "title": "最小価格楽曲",
            "description": "最小価格での楽曲テスト。",
            "genre": "テスト",
            "duration": 30,
            "price": 100.0,  # 最小価格
            "artist_index": 1,
            "cover_art_url": "https://example.com/qa/covers/min_price_track.jpg",
            "audio_file_url": "https://example.com/qa/audio/min_price_track.mp3"
        },
        {
            "title": "高価格楽曲",
            "description": "高価格での楽曲テスト。",
            "genre": "プレミアム",
            "duration": 600,
            "price": 2000.0,  # 高価格
            "artist_index": 2,
            "cover_art_url": "https://example.com/qa/covers/high_price_track.jpg",
            "audio_file_url": "https://example.com/qa/audio/high_price_track.mp3"
        },
        
        # 長いタイトル・説明テスト用
        {
            "title": "非常に長いタイトルを持つ楽曲でUIの表示テストを行うためのテストケース楽曲",
            "description": "非常に長い説明文を持つ楽曲です。" + "この楽曲は文字数制限やUIの表示崩れをテストするためのものです。" * 5,
            "genre": "境界値テスト",
            "duration": 300,
            "price": 400.0,
            "artist_index": 2,
            "cover_art_url": "https://example.com/qa/covers/long_title_track.jpg",
            "audio_file_url": "https://example.com/qa/audio/long_title_track.mp3"
        },
        
        # 特殊文字テスト用
        {
            "title": "特殊文字楽曲 🎵 ♪ ♫ ♬",
            "description": "特殊文字やEmoji、多言語文字を含む楽曲。한국어 中文 العربية Русский",
            "genre": "多言語テスト",
            "duration": 200,
            "price": 350.0,
            "artist_index": 2,
            "cover_art_url": "https://example.com/qa/covers/special_chars_track.jpg",
            "audio_file_url": "https://example.com/qa/audio/special_chars_track.mp3"
        },
        
        # 非公開楽曲テスト用
        {
            "title": "非公開テスト楽曲",
            "description": "非公開状態での楽曲テスト。表示・検索制御のテストに使用。",
            "genre": "プライベート",
            "duration": 180,
            "price": 300.0,
            "artist_index": 3,
            "cover_art_url": "https://example.com/qa/covers/private_track.jpg",
            "audio_file_url": "https://example.com/qa/audio/private_track.mp3",
            "is_public": False
        },
        
        # ジャンルテスト用楽曲
        {
            "title": "ジャンル未分類楽曲",
            "description": "ジャンルが設定されていない楽曲でのテスト。",
            "genre": None,  # ジャンル未設定
            "duration": 150,
            "price": 250.0,
            "artist_index": 3,
            "cover_art_url": "https://example.com/qa/covers/no_genre_track.jpg",
            "audio_file_url": "https://example.com/qa/audio/no_genre_track.mp3"
        },
        
        # 再生回数テスト用
        {
            "title": "人気楽曲（高再生回数）",
            "description": "高い再生回数を持つ楽曲でのランキングテスト。",
            "genre": "ヒット",
            "duration": 210,
            "price": 400.0,
            "artist_index": 1,
            "cover_art_url": "https://example.com/qa/covers/popular_track.jpg",
            "audio_file_url": "https://example.com/qa/audio/popular_track.mp3",
            "play_count": 10000  # 高再生回数
        },
        
        # 新着楽曲テスト用
        {
            "title": "新着楽曲",
            "description": "リリース日テスト用の新着楽曲。",
            "genre": "新着",
            "duration": 190,
            "price": 320.0,
            "artist_index": 4,
            "cover_art_url": "https://example.com/qa/covers/new_release.jpg",
            "audio_file_url": "https://example.com/qa/audio/new_release.mp3",
            "release_date": date.today()  # 今日リリース
        }
    ]
    
    tracks = []
    base_date = date.today() - timedelta(days=30)  # 1ヶ月前から開始
    
    for i, data in enumerate(tracks_data):
        # 特別な指定がない場合はランダムな日付
        release_date = data.get("release_date", base_date + timedelta(days=random.randint(0, 30)))
        play_count = data.get("play_count", random.randint(0, 1000))
        is_public = data.get("is_public", True)
        
        track = Track(
            title=data["title"],
            description=data["description"],
            genre=data["genre"],
            cover_art_url=data["cover_art_url"],
            audio_file_url=data["audio_file_url"],
            duration=data["duration"],
            price=Decimal(str(data["price"])),
            release_date=release_date,
            artist_id=artists[data["artist_index"]].id,
            is_public=is_public,
            play_count=play_count
        )
        session.add(track)
        tracks.append(track)
    
    session.flush()
    return tracks


def create_qa_purchases(session: Session, listeners: list[User], tracks: list[Track]) -> list[Purchase]:
    """QA用購入履歴を作成（テストシナリオ対応）"""
    purchases = []
    payment_methods = list(PaymentMethod)
    purchase_statuses = list(PurchaseStatus)
    
    # E2Eテスト用の固定購入履歴
    e2e_listener = listeners[0]  # E2Eテストリスナー
    e2e_track = tracks[0]  # E2Eテスト楽曲
    
    # 成功した購入
    e2e_purchase = Purchase(
        user_id=e2e_listener.id,
        track_id=e2e_track.id,
        amount=float(e2e_track.price),
        purchase_date=datetime.utcnow() - timedelta(days=1),
        payment_method=PaymentMethod.CREDIT_CARD,
        transaction_id="e2e_test_txn_12345",
        status=PurchaseStatus.COMPLETED
    )
    session.add(e2e_purchase)
    purchases.append(e2e_purchase)
    
    # 通常のテスト用購入履歴
    for listener in listeners[1:]:  # E2Eテストリスナー以外
        # 各リスナーが1-4曲購入
        num_purchases = random.randint(1, 4)
        purchased_tracks = random.sample(tracks[1:], min(num_purchases, len(tracks) - 1))
        
        for track in purchased_tracks:
            # 購入日をランダムに設定
            purchase_date = datetime.utcnow() - timedelta(days=random.randint(0, 30))
            
            # テスト用に様々な決済状況を作成
            status = random.choice([
                PurchaseStatus.COMPLETED,  # 80%の確率
                PurchaseStatus.COMPLETED,
                PurchaseStatus.COMPLETED,
                PurchaseStatus.COMPLETED,
                PurchaseStatus.PENDING,    # 10%の確率
                PurchaseStatus.FAILED      # 10%の確率
            ])
            
            purchase = Purchase(
                user_id=listener.id,
                track_id=track.id,
                amount=float(track.price),
                purchase_date=purchase_date,
                payment_method=random.choice(payment_methods),
                transaction_id=f"qa_txn_{uuid.uuid4().hex[:16]}",
                status=status
            )
            session.add(purchase)
            purchases.append(purchase)
    
    # 特殊ケース：失敗した決済のテストデータ
    failed_purchase = Purchase(
        user_id=listeners[1].id,
        track_id=tracks[1].id,
        amount=float(tracks[1].price),
        purchase_date=datetime.utcnow() - timedelta(hours=1),
        payment_method=PaymentMethod.CREDIT_CARD,
        transaction_id="qa_failed_txn_12345",
        status=PurchaseStatus.FAILED
    )
    session.add(failed_purchase)
    purchases.append(failed_purchase)
    
    # 特殊ケース：ペンディング中の決済
    pending_purchase = Purchase(
        user_id=listeners[2].id,
        track_id=tracks[2].id,
        amount=float(tracks[2].price),
        purchase_date=datetime.utcnow() - timedelta(minutes=30),
        payment_method=PaymentMethod.PAYPAL,
        transaction_id="qa_pending_txn_12345",
        status=PurchaseStatus.PENDING
    )
    session.add(pending_purchase)
    purchases.append(pending_purchase)
    
    session.flush()
    return purchases


def print_qa_summary(session: Session):
    """作成されたQAデータの概要を表示"""
    print("\n📊 作成されたQAデータの概要:")
    print(f"👥 ユーザー総数: {session.query(User).count()}名")
    print(f"🎤 アーティスト: {session.query(User).filter(User.user_role == UserRole.ARTIST).count()}名")
    print(f"👂 リスナー: {session.query(User).filter(User.user_role == UserRole.LISTENER).count()}名")
    print(f"🎵 楽曲総数: {session.query(Track).count()}曲")
    print(f"   - 公開楽曲: {session.query(Track).filter(Track.is_public == True).count()}曲")
    print(f"   - 非公開楽曲: {session.query(Track).filter(Track.is_public == False).count()}曲")
    print(f"💰 購入履歴: {session.query(Purchase).count()}件")
    
    # 購入ステータス別
    print("\n💳 購入ステータス別:")
    for status in PurchaseStatus:
        count = session.query(Purchase).filter(Purchase.status == status).count()
        print(f"   - {status.value}: {count}件")
    
    # テスト用アカウント
    print("\n🧪 テスト用固定アカウント:")
    print("   - E2Eテストリスナー: e2e_listener@example.com")
    print("   - E2Eテストアーティスト: e2e_artist@example.com")
    
    # 境界値テストデータ
    print("\n📏 境界値テストデータ:")
    print("   - 最小価格楽曲: ¥100")
    print("   - 高価格楽曲: ¥2,000")
    print("   - 長いタイトル楽曲: あり")
    print("   - 特殊文字楽曲: あり")
    print("   - ジャンル未設定楽曲: あり")
    
    print("\n🚀 QA環境の準備が完了しました！")
    print("   - E2Eテスト対応の固定データ")
    print("   - 境界値テスト用データ")
    print("   - エラーケーステスト用データ")
    print("   - 多言語・特殊文字対応データ")


if __name__ == "__main__":
    import sys
    reset_db = "--reset" in sys.argv or "-r" in sys.argv
    
    print("🧪 MusicShelf QA環境用Seedデータ作成")
    print("=" * 50)
    
    try:
        create_qa_seed_data(reset_db=reset_db)
    except KeyboardInterrupt:
        print("\n⚠️  ユーザーによってキャンセルされました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)