#!/usr/bin/env python3
"""
インディーズミュージックプラットフォーム用のSeedデータ作成スクリプト

使用方法:
    python seed_data.py
"""

import asyncio
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.user import User
from app.schemas.user import UserRole
from app.models.track import Track
from app.models.purchase import Purchase, PaymentMethod, PurchaseStatus


def create_seed_data():
    """Seedデータを作成"""
    # テーブルを作成
    print("🔧 データベーステーブルを作成しています...")
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        print("🌱 Seedデータの作成を開始します...")
        
        # 既存データの確認
        try:
            existing_users = session.query(User).count()
            if existing_users > 0:
                print(f"既に{existing_users}件のユーザーが存在します。追加でSeedデータを作成します。")
        except:
            existing_users = 0
        
        # リスナーユーザーの作成
        listeners = create_listeners(session)
        print(f"✅ リスナー {len(listeners)}名を作成しました")
        
        # アーティストユーザーの作成
        artists = create_artists(session)
        print(f"✅ アーティスト {len(artists)}名を作成しました")
        
        # 楽曲の作成
        tracks = create_tracks(session, artists)
        print(f"✅ 楽曲 {len(tracks)}曲を作成しました")
        
        # 購入履歴の作成
        purchases = create_purchases(session, listeners, tracks)
        print(f"✅ 購入履歴 {len(purchases)}件を作成しました")
        
        session.commit()
        print("🎉 Seedデータの作成が完了しました！")
        
        # 作成されたデータの概要を表示
        print_summary(session)
        
    except Exception as e:
        session.rollback()
        print(f"❌ エラーが発生しました: {e}")
        raise
    finally:
        session.close()


def create_listeners(session: Session) -> list[User]:
    """リスナーユーザーを作成"""
    listeners_data = [
        {
            "email": "listener1@example.com",
            "display_name": "音楽好きの田中",
            "firebase_uid": f"listener_uid_{uuid.uuid4().hex[:8]}"
        },
        {
            "email": "listener2@example.com", 
            "display_name": "インディーズファンの佐藤",
            "firebase_uid": f"listener_uid_{uuid.uuid4().hex[:8]}"
        },
        {
            "email": "listener3@example.com",
            "display_name": "メロディー愛好家の鈴木",
            "firebase_uid": f"listener_uid_{uuid.uuid4().hex[:8]}"
        },
        {
            "email": "listener4@example.com",
            "display_name": "音楽コレクターの高橋",
            "firebase_uid": f"listener_uid_{uuid.uuid4().hex[:8]}"
        },
        {
            "email": "listener5@example.com",
            "display_name": "新しい音楽を探す山田",
            "firebase_uid": f"listener_uid_{uuid.uuid4().hex[:8]}"
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
    
    session.flush()  # IDを取得するためにflush
    return listeners


def create_artists(session: Session) -> list[User]:
    """アーティストユーザーを作成"""
    artists_data = [
        {
            "email": "artist1@example.com",
            "display_name": "青空バンド",
            "firebase_uid": f"artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "爽やかなポップスを奏でる4人組バンド。青春をテーマにした楽曲で多くのファンを魅了しています。"
        },
        {
            "email": "artist2@example.com",
            "display_name": "夜想曲",
            "firebase_uid": f"artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "幻想的なエレクトロニックミュージックを創作するソロアーティスト。夜の街をイメージした楽曲が特徴。"
        },
        {
            "email": "artist3@example.com",
            "display_name": "森のささやき",
            "firebase_uid": f"artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "アコースティックフォークデュオ。自然をテーマにした優しいメロディーで心を癒します。"
        },
        {
            "email": "artist4@example.com",
            "display_name": "ストリートビート",
            "firebase_uid": f"artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "都市の鼓動をヒップホップに込めるラッパー。社会への鋭い視点を音楽で表現。"
        },
        {
            "email": "artist5@example.com",
            "display_name": "クラシカルモダン",
            "firebase_uid": f"artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "クラシック音楽とモダンな要素を融合させた革新的なアンサンブル。"
        },
        {
            "email": "artist6@example.com",
            "display_name": "ジャズカフェ",
            "firebase_uid": f"artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "温かいジャズサウンドでリラックスした時間を提供するトリオ。"
        }
    ]
    
    artists = []
    for data in artists_data:
        artist = User(
            email=data["email"],
            display_name=data["display_name"],
            firebase_uid=data["firebase_uid"],
            user_role=UserRole.ARTIST,
            is_verified=True
        )
        session.add(artist)
        artists.append(artist)
    
    session.flush()
    return artists


def create_tracks(session: Session, artists: list[User]) -> list[Track]:
    """楽曲を作成"""
    tracks_data = [
        # 青空バンドの楽曲
        {
            "title": "青い空の下で",
            "description": "夏の青空をテーマにした爽やかなポップソング。青春の1ページを彩る楽曲です。",
            "genre": "ポップ",
            "duration": 245,
            "price": 300.0,
            "artist_index": 0,
            "cover_art_url": "https://example.com/covers/blue_sky.jpg",
            "audio_file_url": "https://example.com/audio/blue_sky.mp3"
        },
        {
            "title": "夕暮れのメロディー",
            "description": "一日の終わりを優しく包むバラード。心に響く美しいハーモニーが特徴。",
            "genre": "ポップ",
            "duration": 280,
            "price": 350.0,
            "artist_index": 0,
            "cover_art_url": "https://example.com/covers/sunset_melody.jpg",
            "audio_file_url": "https://example.com/audio/sunset_melody.mp3"
        },
        
        # 夜想曲の楽曲
        {
            "title": "Digital Dreams",
            "description": "デジタル世界の夢をテーマにしたエレクトロニック楽曲。未来的なサウンドが印象的。",
            "genre": "エレクトロニック",
            "duration": 320,
            "price": 400.0,
            "artist_index": 1,
            "cover_art_url": "https://example.com/covers/digital_dreams.jpg",
            "audio_file_url": "https://example.com/audio/digital_dreams.mp3"
        },
        {
            "title": "Neon Nights",
            "description": "ネオンに彩られた夜の街を音楽で表現。都市の孤独と美しさを描いた作品。",
            "genre": "エレクトロニック",
            "duration": 295,
            "price": 380.0,
            "artist_index": 1,
            "cover_art_url": "https://example.com/covers/neon_nights.jpg",
            "audio_file_url": "https://example.com/audio/neon_nights.mp3"
        },
        
        # 森のささやきの楽曲
        {
            "title": "風のうた",
            "description": "森を吹き抜ける風をイメージしたアコースティック楽曲。自然の美しさを歌った名曲。",
            "genre": "フォーク",
            "duration": 210,
            "price": 250.0,
            "artist_index": 2,
            "cover_art_url": "https://example.com/covers/wind_song.jpg",
            "audio_file_url": "https://example.com/audio/wind_song.mp3"
        },
        {
            "title": "星空のセレナーデ",
            "description": "満天の星空の下で奏でるセレナーデ。ロマンチックで心温まる楽曲。",
            "genre": "フォーク",
            "duration": 235,
            "price": 280.0,
            "artist_index": 2,
            "cover_art_url": "https://example.com/covers/starry_serenade.jpg",
            "audio_file_url": "https://example.com/audio/starry_serenade.mp3"
        },
        
        # ストリートビートの楽曲
        {
            "title": "都市の鼓動",
            "description": "都市で生きる人々の想いを力強いラップで表現。社会への熱いメッセージが込められた楽曲。",
            "genre": "ヒップホップ",
            "duration": 260,
            "price": 320.0,
            "artist_index": 3,
            "cover_art_url": "https://example.com/covers/city_beat.jpg",
            "audio_file_url": "https://example.com/audio/city_beat.mp3"
        },
        {
            "title": "夢追い人",
            "description": "夢を追い続ける全ての人へ贈るエンパワーメントソング。希望に満ちたメッセージが心に響く。",
            "genre": "ヒップホップ",
            "duration": 275,
            "price": 350.0,
            "artist_index": 3,
            "cover_art_url": "https://example.com/covers/dream_chaser.jpg",
            "audio_file_url": "https://example.com/audio/dream_chaser.mp3"
        },
        
        # クラシカルモダンの楽曲
        {
            "title": "時の調べ",
            "description": "クラシックとモダンが融合した壮大な楽曲。時の流れをオーケストラで表現した名作。",
            "genre": "クラシック",
            "duration": 420,
            "price": 500.0,
            "artist_index": 4,
            "cover_art_url": "https://example.com/covers/time_melody.jpg",
            "audio_file_url": "https://example.com/audio/time_melody.mp3"
        },
        {
            "title": "革新の序曲",
            "description": "新しい時代の始まりを告げる革新的な序曲。伝統と革新が美しく調和した作品。",
            "genre": "クラシック",
            "duration": 380,
            "price": 450.0,
            "artist_index": 4,
            "cover_art_url": "https://example.com/covers/innovation_overture.jpg",
            "audio_file_url": "https://example.com/audio/innovation_overture.mp3"
        },
        
        # ジャズカフェの楽曲
        {
            "title": "コーヒーブレイク",
            "description": "リラックスしたカフェタイムにぴったりのジャズナンバー。温かいコーヒーのようなメロディー。",
            "genre": "ジャズ",
            "duration": 195,
            "price": 290.0,
            "artist_index": 5,
            "cover_art_url": "https://example.com/covers/coffee_break.jpg",
            "audio_file_url": "https://example.com/audio/coffee_break.mp3"
        },
        {
            "title": "雨の日のブルース",
            "description": "雨の日の憂鬱を癒すブルージーなジャズ。心に染み入る美しいサックスソロが印象的。",
            "genre": "ジャズ",
            "duration": 220,
            "price": 310.0,
            "artist_index": 5,
            "cover_art_url": "https://example.com/covers/rainy_blues.jpg",
            "audio_file_url": "https://example.com/audio/rainy_blues.mp3"
        }
    ]
    
    tracks = []
    base_date = date.today() - timedelta(days=90)  # 3ヶ月前から開始
    
    for i, data in enumerate(tracks_data):
        # リリース日をランダムに設定（過去3ヶ月以内）
        release_date = base_date + timedelta(days=random.randint(0, 90))
        
        # 再生回数をランダムに設定
        play_count = random.randint(10, 1000)
        
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
            is_public=True,
            play_count=play_count
        )
        session.add(track)
        tracks.append(track)
    
    session.flush()
    return tracks


def create_purchases(session: Session, listeners: list[User], tracks: list[Track]) -> list[Purchase]:
    """購入履歴を作成"""
    purchases = []
    payment_methods = [PaymentMethod.CREDIT_CARD, PaymentMethod.PAYPAL, PaymentMethod.APPLE_PAY]
    
    # 各リスナーにランダムな購入履歴を作成
    for listener in listeners:
        # 各リスナーが1-5曲購入
        num_purchases = random.randint(1, 5)
        purchased_tracks = random.sample(tracks, num_purchases)
        
        for track in purchased_tracks:
            # 購入日をランダムに設定（過去30日以内）
            purchase_date = datetime.utcnow() - timedelta(days=random.randint(0, 30))
            
            purchase = Purchase(
                user_id=listener.id,
                track_id=track.id,
                amount=float(track.price),
                purchase_date=purchase_date,
                payment_method=random.choice(payment_methods),
                transaction_id=f"txn_{uuid.uuid4().hex[:16]}",
                status=PurchaseStatus.COMPLETED
            )
            session.add(purchase)
            purchases.append(purchase)
    
    session.flush()
    return purchases


def print_summary(session: Session):
    """作成されたデータの概要を表示"""
    print("\n📊 作成されたデータの概要:")
    print(f"👥 ユーザー総数: {session.query(User).count()}名")
    print(f"🎤 アーティスト: {session.query(User).filter(User.user_role == UserRole.ARTIST).count()}名")
    print(f"👂 リスナー: {session.query(User).filter(User.user_role == UserRole.LISTENER).count()}名")
    print(f"🎵 楽曲総数: {session.query(Track).count()}曲")
    print(f"💰 購入履歴: {session.query(Purchase).count()}件")
    
    # ジャンル別楽曲数
    print("\n🎼 ジャンル別楽曲数:")
    genres = session.query(Track.genre, session.query(Track).filter(Track.genre == Track.genre).count()).distinct().all()
    for genre_name in ["ポップ", "エレクトロニック", "フォーク", "ヒップホップ", "クラシック", "ジャズ"]:
        count = session.query(Track).filter(Track.genre == genre_name).count()
        print(f"  {genre_name}: {count}曲")
    
    # 総売上
    total_sales = session.query(Purchase).count() * 300  # 概算
    print(f"\n💵 総売上（概算）: ¥{total_sales:,}")


if __name__ == "__main__":
    create_seed_data()