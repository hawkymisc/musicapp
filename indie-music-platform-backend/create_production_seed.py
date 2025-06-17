#!/usr/bin/env python3
"""
本番環境用のSeedデータ作成スクリプト

Container Apps環境で実行して、デモデータを作成します。
"""

import sys
import os
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_production_seed_data():
    """本番環境用のSeedデータを作成"""
    try:
        from sqlalchemy.orm import Session
        from app.db.session import SessionLocal, engine
        from app.models.base import Base
        from app.models.user import User
        from app.schemas.user import UserRole
        from app.models.track import Track
        from app.models.purchase import Purchase, PaymentMethod, PurchaseStatus

        print("🌱 本番環境用Seedデータの作成を開始します...")

        # テーブルを作成
        print("🔧 データベーステーブルを作成しています...")
        Base.metadata.create_all(bind=engine)

        session = SessionLocal()

        try:
            # 既存データの確認
            existing_users = session.query(User).count()
            existing_tracks = session.query(Track).count()
            
            print(f"📊 現在の状況: ユーザー {existing_users}名, 楽曲 {existing_tracks}曲")

            if existing_tracks > 0:
                print("✅ データが既に存在します。作成をスキップします。")
                return

            # デモ用アーティストユーザーの作成
            artists_data = [
                {
                    "email": "moonlight.echo@musicshelf.net",
                    "display_name": "Moonlight Echo",
                    "firebase_uid": f"prod_artist_uid_{uuid.uuid4().hex[:8]}",
                },
                {
                    "email": "urban.soul.collective@musicshelf.net", 
                    "display_name": "Urban Soul Collective",
                    "firebase_uid": f"prod_artist_uid_{uuid.uuid4().hex[:8]}",
                },
                {
                    "email": "acoustic.garden@musicshelf.net",
                    "display_name": "Acoustic Garden", 
                    "firebase_uid": f"prod_artist_uid_{uuid.uuid4().hex[:8]}",
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

            session.flush()  # IDを取得するためにflush
            print(f"✅ アーティスト {len(artists)}名を作成しました")

            # デモ用楽曲の作成
            tracks_data = [
                {
                    "title": "Midnight Reflections",
                    "description": "深夜の静寂に響く内省的なエレクトロニック楽曲。",
                    "genre": "エレクトロニック",
                    "duration": 285,
                    "price": 450.0,
                    "artist_index": 0,
                    "cover_art_url": "https://example.com/demo/covers/midnight_reflections.jpg",
                    "audio_file_url": "https://example.com/demo/audio/midnight_reflections.mp3"
                },
                {
                    "title": "City Lights Serenade",
                    "description": "都市の夜景にインスパイアされたソウルフルなR&B。",
                    "genre": "R&B",
                    "duration": 240,
                    "price": 380.0,
                    "artist_index": 1,
                    "cover_art_url": "https://example.com/demo/covers/city_lights_serenade.jpg",
                    "audio_file_url": "https://example.com/demo/audio/city_lights_serenade.mp3"
                },
                {
                    "title": "Forest Dawn",
                    "description": "森の夜明けをアコースティックサウンドで描いた美しいインストゥルメンタル。",
                    "genre": "フォーク", 
                    "duration": 220,
                    "price": 320.0,
                    "artist_index": 2,
                    "cover_art_url": "https://example.com/demo/covers/forest_dawn.jpg",
                    "audio_file_url": "https://example.com/demo/audio/forest_dawn.mp3"
                }
            ]

            tracks = []
            base_date = date.today() - timedelta(days=30)

            for i, data in enumerate(tracks_data):
                release_date = base_date + timedelta(days=random.randint(0, 30))
                play_count = random.randint(50, 1000)

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

            session.commit()
            print(f"✅ 楽曲 {len(tracks)}曲を作成しました")

            # 最終確認
            final_users = session.query(User).count()
            final_tracks = session.query(Track).count()
            print(f"🎉 Seedデータの作成が完了しました！")
            print(f"📊 最終データ: ユーザー {final_users}名, 楽曲 {final_tracks}曲")

        except Exception as e:
            session.rollback()
            print(f"❌ エラーが発生しました: {e}")
            raise
        finally:
            session.close()

    except Exception as e:
        print(f"💥 初期化エラー: {e}")
        raise

if __name__ == "__main__":
    create_production_seed_data()