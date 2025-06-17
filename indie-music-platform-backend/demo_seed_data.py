#!/usr/bin/env python3
"""
デモ・QA環境用のリアルなSeedデータ作成スクリプト

実際のインディーズアーティストを模した魅力的なデータで、
プラットフォームのデモンストレーションに適した内容を作成します。

使用方法:
    python demo_seed_data.py
    python demo_seed_data.py --reset  # データベースリセット付き
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


def create_demo_seed_data(reset_db=False):
    """デモ・QA環境用のSeedデータを作成
    
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
        print("🌱 デモ・QA環境用Seedデータの作成を開始します...")
        
        # 既存データの確認
        try:
            existing_users = session.query(User).count()
            if existing_users > 0 and not reset_db:
                print(f"既に{existing_users}件のユーザーが存在します。重複を避けるためにスキップします。")
                print("データベースをリセットしたい場合は demo_seed_data.py --reset を使用してください。")
                return
        except:
            existing_users = 0
        
        # デモ用リスナーユーザーの作成
        listeners = create_demo_listeners(session)
        print(f"✅ デモリスナー {len(listeners)}名を作成しました")
        
        # デモ用アーティストユーザーの作成
        artists = create_demo_artists(session)
        print(f"✅ デモアーティスト {len(artists)}名を作成しました")
        
        # デモ用楽曲の作成
        tracks = create_demo_tracks(session, artists)
        print(f"✅ デモ楽曲 {len(tracks)}曲を作成しました")
        
        # デモ用購入履歴の作成
        purchases = create_demo_purchases(session, listeners, tracks)
        print(f"✅ デモ購入履歴 {len(purchases)}件を作成しました")
        
        session.commit()
        print("🎉 デモSeedデータの作成が完了しました！")
        
        # 作成されたデータの概要を表示
        print_demo_summary(session)
        
    except Exception as e:
        session.rollback()
        print(f"❌ エラーが発生しました: {e}")
        raise
    finally:
        session.close()


def create_demo_listeners(session: Session) -> list[User]:
    """デモ用リスナーユーザーを作成"""
    listeners_data = [
        {
            "email": "demo_listener1@musicshelf.net",
            "display_name": "音楽愛好家 太郎",
            "firebase_uid": f"demo_listener_uid_{uuid.uuid4().hex[:8]}"
        },
        {
            "email": "demo_listener2@musicshelf.net", 
            "display_name": "インディーズコレクター 花子",
            "firebase_uid": f"demo_listener_uid_{uuid.uuid4().hex[:8]}"
        },
        {
            "email": "demo_listener3@musicshelf.net",
            "display_name": "メロディーハンター 次郎",
            "firebase_uid": f"demo_listener_uid_{uuid.uuid4().hex[:8]}"
        },
        {
            "email": "demo_listener4@musicshelf.net",
            "display_name": "音楽評論家 美咲",
            "firebase_uid": f"demo_listener_uid_{uuid.uuid4().hex[:8]}"
        },
        {
            "email": "demo_listener5@musicshelf.net",
            "display_name": "新しい音楽を求める 健太",
            "firebase_uid": f"demo_listener_uid_{uuid.uuid4().hex[:8]}"
        },
        {
            "email": "demo_listener6@musicshelf.net",
            "display_name": "多ジャンル愛好家 さくら",
            "firebase_uid": f"demo_listener_uid_{uuid.uuid4().hex[:8]}"
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


def create_demo_artists(session: Session) -> list[User]:
    """デモ用アーティストユーザーを作成"""
    artists_data = [
        {
            "email": "moonlight.echo@musicshelf.net",
            "display_name": "Moonlight Echo",
            "firebase_uid": f"demo_artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "夜の静寂をエレクトロニックサウンドで表現するソロアーティスト。シンセサイザーとピアノを組み合わせた幻想的な楽曲が特徴。"
        },
        {
            "email": "urban.soul.collective@musicshelf.net",
            "display_name": "Urban Soul Collective",
            "firebase_uid": f"demo_artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "都市の鼓動をソウルフルなR&Bに込める5人組。ジャズとヒップホップの要素を巧みに織り交ぜた現代的なサウンドを追求。"
        },
        {
            "email": "acoustic.garden@musicshelf.net",
            "display_name": "Acoustic Garden",
            "firebase_uid": f"demo_artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "自然をテーマにしたアコースティックフォークデュオ。ギターとバイオリンが奏でる美しいハーモニーで心を癒す音楽を届ける。"
        },
        {
            "email": "neon.dreams@musicshelf.net",
            "display_name": "Neon Dreams",
            "firebase_uid": f"demo_artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "80年代シンセウェーブとモダンエレクトロニックを融合させたトリオ。レトロフューチャーなサウンドで新しい音楽体験を提供。"
        },
        {
            "email": "jazz.fusion.lab@musicshelf.net",
            "display_name": "Jazz Fusion Lab",
            "firebase_uid": f"demo_artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "実験的なジャズフュージョンを追求するインストゥルメンタルバンド。複雑なリズムと美しいメロディーが共存する革新的な音楽。"
        },
        {
            "email": "indie.rock.rebels@musicshelf.net",
            "display_name": "Indie Rock Rebels",
            "firebase_uid": f"demo_artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "エネルギッシュなインディーロックバンド。力強いギターリフと情熱的なボーカルで現代の若者の心を代弁する。"
        },
        {
            "email": "classical.crossover@musicshelf.net",
            "display_name": "Classical Crossover",
            "firebase_uid": f"demo_artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "クラシック音楽の美しさを現代に伝えるクロスオーバーアンサンブル。伝統的な楽器とモダンなアレンジで新しい音楽を創造。"
        },
        {
            "email": "lofi.hip.hop.cafe@musicshelf.net",
            "display_name": "Lo-Fi Hip Hop Café",
            "firebase_uid": f"demo_artist_uid_{uuid.uuid4().hex[:8]}",
            "bio": "リラックスできるLo-Fiヒップホップを制作するプロデューサー。勉強や作業のBGMに最適な心地よいビートを提供。"
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


def create_demo_tracks(session: Session, artists: list[User]) -> list[Track]:
    """デモ用楽曲を作成"""
    tracks_data = [
        # Moonlight Echo の楽曲
        {
            "title": "Midnight Reflections",
            "description": "深夜の静寂に響く内省的なエレクトロニック楽曲。シンセサイザーの幻想的な音色が心の奥深くに響く名作。",
            "genre": "エレクトロニック",
            "duration": 285,
            "price": 450.0,
            "artist_index": 0,
            "cover_art_url": "https://example.com/demo/covers/midnight_reflections.jpg",
            "audio_file_url": "https://example.com/demo/audio/midnight_reflections.mp3"
        },
        {
            "title": "Digital Constellation",
            "description": "デジタル世界の星座をイメージした壮大なアンビエント楽曲。宇宙の広がりを感じる神秘的なサウンドスケープ。",
            "genre": "エレクトロニック",
            "duration": 320,
            "price": 480.0,
            "artist_index": 0,
            "cover_art_url": "https://example.com/demo/covers/digital_constellation.jpg",
            "audio_file_url": "https://example.com/demo/audio/digital_constellation.mp3"
        },
        
        # Urban Soul Collective の楽曲
        {
            "title": "City Lights Serenade",
            "description": "都市の夜景にインスパイアされたソウルフルなR&B。ジャズピアノとモダンなビートが絶妙に融合した傑作。",
            "genre": "R&B",
            "duration": 240,
            "price": 380.0,
            "artist_index": 1,
            "cover_art_url": "https://example.com/demo/covers/city_lights_serenade.jpg",
            "audio_file_url": "https://example.com/demo/audio/city_lights_serenade.mp3"
        },
        {
            "title": "Underground Groove",
            "description": "アンダーグラウンドシーンから生まれた力強いグルーヴ。社会へのメッセージを込めた現代的なソウルミュージック。",
            "genre": "R&B",
            "duration": 195,
            "price": 350.0,
            "artist_index": 1,
            "cover_art_url": "https://example.com/demo/covers/underground_groove.jpg",
            "audio_file_url": "https://example.com/demo/audio/underground_groove.mp3"
        },
        
        # Acoustic Garden の楽曲
        {
            "title": "Forest Dawn",
            "description": "森の夜明けをアコースティックサウンドで描いた美しいインストゥルメンタル。自然の息吹を感じる癒しの名曲。",
            "genre": "フォーク",
            "duration": 220,
            "price": 320.0,
            "artist_index": 2,
            "cover_art_url": "https://example.com/demo/covers/forest_dawn.jpg",
            "audio_file_url": "https://example.com/demo/audio/forest_dawn.mp3"
        },
        {
            "title": "River's Song",
            "description": "川のせせらぎをテーマにしたフォーク楽曲。ギターとバイオリンが奏でる優しいメロディーが心を和ませる。",
            "genre": "フォーク",
            "duration": 255,
            "price": 300.0,
            "artist_index": 2,
            "cover_art_url": "https://example.com/demo/covers/rivers_song.jpg",
            "audio_file_url": "https://example.com/demo/audio/rivers_song.mp3"
        },
        
        # Neon Dreams の楽曲
        {
            "title": "Synthwave Highway",
            "description": "80年代シンセウェーブサウンドでドライブ気分を味わえる楽曲。ネオンライトが輝く夜の高速道路をイメージ。",
            "genre": "シンセウェーブ",
            "duration": 270,
            "price": 420.0,
            "artist_index": 3,
            "cover_art_url": "https://example.com/demo/covers/synthwave_highway.jpg",
            "audio_file_url": "https://example.com/demo/audio/synthwave_highway.mp3"
        },
        {
            "title": "Retro Future",
            "description": "レトロフューチャーな世界観を音楽で表現。過去と未来が交差するサイバーパンクなエレクトロニックサウンド。",
            "genre": "シンセウェーブ",
            "duration": 305,
            "price": 450.0,
            "artist_index": 3,
            "cover_art_url": "https://example.com/demo/covers/retro_future.jpg",
            "audio_file_url": "https://example.com/demo/audio/retro_future.mp3"
        },
        
        # Jazz Fusion Lab の楽曲
        {
            "title": "Experimental Jazz Suite",
            "description": "実験的なジャズフュージョンの組曲。複雑なリズムチェンジと即興演奏が織りなす音楽的冒険。",
            "genre": "ジャズフュージョン",
            "duration": 480,
            "price": 550.0,
            "artist_index": 4,
            "cover_art_url": "https://example.com/demo/covers/experimental_jazz_suite.jpg",
            "audio_file_url": "https://example.com/demo/audio/experimental_jazz_suite.mp3"
        },
        {
            "title": "Fusion Metropolis",
            "description": "都市の躍動感をジャズフュージョンで表現。テクニカルな演奏と美しいメロディーが共存する現代ジャズの傑作。",
            "genre": "ジャズフュージョン",
            "duration": 340,
            "price": 480.0,
            "artist_index": 4,
            "cover_art_url": "https://example.com/demo/covers/fusion_metropolis.jpg",
            "audio_file_url": "https://example.com/demo/audio/fusion_metropolis.mp3"
        },
        
        # Indie Rock Rebels の楽曲
        {
            "title": "Revolution Anthem",
            "description": "新しい時代への反抗を歌ったエネルギッシュなインディーロック。力強いギターリフが印象的な現代のアンセム。",
            "genre": "インディーロック",
            "duration": 225,
            "price": 390.0,
            "artist_index": 5,
            "cover_art_url": "https://example.com/demo/covers/revolution_anthem.jpg",
            "audio_file_url": "https://example.com/demo/audio/revolution_anthem.mp3"
        },
        {
            "title": "Youth Dreams",
            "description": "若者の夢と希望を歌ったエモーショナルなバラード。心に響く歌詞とメロディーが世代を超えて愛される名曲。",
            "genre": "インディーロック",
            "duration": 290,
            "price": 360.0,
            "artist_index": 5,
            "cover_art_url": "https://example.com/demo/covers/youth_dreams.jpg",
            "audio_file_url": "https://example.com/demo/audio/youth_dreams.mp3"
        },
        
        # Classical Crossover の楽曲
        {
            "title": "Modern Bach Variations",
            "description": "バッハの楽曲を現代的にアレンジしたクロスオーバー作品。クラシックの美しさと現代的なサウンドが融合。",
            "genre": "クラシッククロスオーバー",
            "duration": 380,
            "price": 520.0,
            "artist_index": 6,
            "cover_art_url": "https://example.com/demo/covers/modern_bach_variations.jpg",
            "audio_file_url": "https://example.com/demo/audio/modern_bach_variations.mp3"
        },
        {
            "title": "Electronic Symphony",
            "description": "エレクトロニック要素を取り入れた革新的な交響曲。伝統的なオーケストラとシンセサイザーの壮大なコラボレーション。",
            "genre": "クラシッククロスオーバー",
            "duration": 450,
            "price": 580.0,
            "artist_index": 6,
            "cover_art_url": "https://example.com/demo/covers/electronic_symphony.jpg",
            "audio_file_url": "https://example.com/demo/audio/electronic_symphony.mp3"
        },
        
        # Lo-Fi Hip Hop Café の楽曲
        {
            "title": "Study Session",
            "description": "集中したい時にぴったりのLo-Fiヒップホップ。心地よいビートとメロディーが作業効率を高める。",
            "genre": "Lo-Fi Hip Hop",
            "duration": 180,
            "price": 250.0,
            "artist_index": 7,
            "cover_art_url": "https://example.com/demo/covers/study_session.jpg",
            "audio_file_url": "https://example.com/demo/audio/study_session.mp3"
        },
        {
            "title": "Rainy Afternoon",
            "description": "雨の午後にぴったりのリラックスできるLo-Fiビート。カフェで過ごすゆったりとした時間をイメージ。",
            "genre": "Lo-Fi Hip Hop",
            "duration": 200,
            "price": 280.0,
            "artist_index": 7,
            "cover_art_url": "https://example.com/demo/covers/rainy_afternoon.jpg",
            "audio_file_url": "https://example.com/demo/audio/rainy_afternoon.mp3"
        },
        {
            "title": "Coffee Break Beats",
            "description": "コーヒーブレイクの時間を豊かにするLo-Fiヒップホップ。温かいコーヒーのように心を和ませるビート。",
            "genre": "Lo-Fi Hip Hop",
            "duration": 165,
            "price": 240.0,
            "artist_index": 7,
            "cover_art_url": "https://example.com/demo/covers/coffee_break_beats.jpg",
            "audio_file_url": "https://example.com/demo/audio/coffee_break_beats.mp3"
        }
    ]
    
    tracks = []
    base_date = date.today() - timedelta(days=180)  # 6ヶ月前から開始
    
    for i, data in enumerate(tracks_data):
        # リリース日をランダムに設定（過去6ヶ月以内）
        release_date = base_date + timedelta(days=random.randint(0, 180))
        
        # 再生回数をランダムに設定（デモ用なのでリアルな数値）
        play_count = random.randint(50, 2500)
        
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


def create_demo_purchases(session: Session, listeners: list[User], tracks: list[Track]) -> list[Purchase]:
    """デモ用購入履歴を作成"""
    purchases = []
    payment_methods = [PaymentMethod.CREDIT_CARD, PaymentMethod.PAYPAL, PaymentMethod.APPLE_PAY]
    
    # 人気楽曲を設定（購入数を多くする）
    popular_tracks = tracks[:8]  # 最初の8曲を人気楽曲とする
    
    # 各リスナーにランダムな購入履歴を作成
    for listener in listeners:
        # 各リスナーが3-8曲購入（デモ用なのでより多め）
        num_purchases = random.randint(3, 8)
        
        # 人気楽曲を優先的に選択
        popular_picks = random.randint(1, min(3, len(popular_tracks)))
        regular_picks = num_purchases - popular_picks
        
        purchased_tracks = []
        purchased_tracks.extend(random.sample(popular_tracks, popular_picks))
        if regular_picks > 0:
            remaining_tracks = [t for t in tracks if t not in purchased_tracks]
            purchased_tracks.extend(random.sample(remaining_tracks, min(regular_picks, len(remaining_tracks))))
        
        for track in purchased_tracks:
            # 購入日をランダムに設定（過去60日以内）
            purchase_date = datetime.utcnow() - timedelta(days=random.randint(0, 60))
            
            purchase = Purchase(
                user_id=listener.id,
                track_id=track.id,
                amount=float(track.price),
                purchase_date=purchase_date,
                payment_method=random.choice(payment_methods),
                transaction_id=f"demo_txn_{uuid.uuid4().hex[:16]}",
                status=PurchaseStatus.COMPLETED
            )
            session.add(purchase)
            purchases.append(purchase)
    
    session.flush()
    return purchases


def print_demo_summary(session: Session):
    """作成されたデモデータの概要を表示"""
    print("\n📊 作成されたデモデータの概要:")
    print(f"👥 ユーザー総数: {session.query(User).count()}名")
    print(f"🎤 アーティスト: {session.query(User).filter(User.user_role == UserRole.ARTIST).count()}名")
    print(f"👂 リスナー: {session.query(User).filter(User.user_role == UserRole.LISTENER).count()}名")
    print(f"🎵 楽曲総数: {session.query(Track).count()}曲")
    print(f"💰 購入履歴: {session.query(Purchase).count()}件")
    
    # ジャンル別楽曲数
    print("\n🎼 ジャンル別楽曲数:")
    genres = ["エレクトロニック", "R&B", "フォーク", "シンセウェーブ", "ジャズフュージョン", 
              "インディーロック", "クラシッククロスオーバー", "Lo-Fi Hip Hop"]
    for genre_name in genres:
        count = session.query(Track).filter(Track.genre == genre_name).count()
        if count > 0:
            print(f"  {genre_name}: {count}曲")
    
    # 人気アーティスト（購入数順）
    print("\n🌟 人気アーティスト（購入数順）:")
    from sqlalchemy import func
    popular_artists = session.query(
        User.display_name,
        func.count(Purchase.id).label('purchase_count')
    ).join(Track, User.id == Track.artist_id)\
     .join(Purchase, Track.id == Purchase.track_id)\
     .group_by(User.id, User.display_name)\
     .order_by(func.count(Purchase.id).desc())\
     .limit(5).all()
    
    for i, (artist_name, purchase_count) in enumerate(popular_artists, 1):
        print(f"  {i}. {artist_name}: {purchase_count}回購入")
    
    # 総売上
    total_sales = sum([p.amount for p in session.query(Purchase).all()])
    print(f"\n💵 総売上: ¥{total_sales:,.0f}")
    
    print("\n🚀 デモ環境の準備が完了しました！")
    print("   - 多様なジャンルの楽曲")
    print("   - リアルなユーザー購買行動")
    print("   - プラットフォームデモに最適なデータ")


if __name__ == "__main__":
    import sys
    reset_db = "--reset" in sys.argv or "-r" in sys.argv
    
    print("🎵 MusicShelf デモ・QA環境用Seedデータ作成")
    print("=" * 50)
    
    try:
        create_demo_seed_data(reset_db=reset_db)
    except KeyboardInterrupt:
        print("\n⚠️  ユーザーによってキャンセルされました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)