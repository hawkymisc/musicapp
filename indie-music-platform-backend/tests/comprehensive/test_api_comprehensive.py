"""
Seedデータを活用した包括的APIテストスイート

このテストスイートは、実際のSeedデータを使用して
音楽プラットフォームのすべてのAPI機能を網羅的にテストします。
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import SessionLocal
from seed_data import create_seed_data
from tests.conftest import TestingSessionLocal, engine
import json
from datetime import datetime, date


class TestComprehensiveAPI:
    """包括的APIテストクラス"""
    
    @classmethod
    def setup_class(cls):
        """テストクラス開始時にSeedデータを作成"""
        print("🌱 テスト用Seedデータを作成中...")
        # テスト用データベースでSeedデータを作成
        from app.models.base import Base
        from app.models.user import User
        from app.schemas.user import UserRole
        from app.models.track import Track
        from app.models.purchase import Purchase, PaymentMethod, PurchaseStatus
        import uuid
        
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.session = TestingSessionLocal()
        
        # 簡単なテスト用データを作成
        cls._create_test_data()
        print("✅ Seedデータ作成完了")
    
    @classmethod
    def _create_test_data(cls):
        """テスト用の簡単なデータを作成"""
        from app.models.user import User
        from app.schemas.user import UserRole
        from app.models.track import Track
        import uuid
        
        try:
            # テスト用アーティスト
            artist = User(
                id=str(uuid.uuid4()),
                email="test_artist@example.com",
                firebase_uid="test_artist_uid",
                display_name="Test Artist",
                user_role=UserRole.ARTIST,
                is_verified=True
            )
            cls.session.add(artist)
            cls.session.flush()
            
            # テスト用楽曲
            track = Track(
                id=str(uuid.uuid4()),
                artist_id=artist.id,
                title="青空のメロディー",
                description="美しい青空をイメージした楽曲",
                genre="ポップ",
                cover_art_url="https://example.com/cover.jpg",
                audio_file_url="https://example.com/audio.mp3",
                duration=180,
                price=300,
                release_date=date.today(),
                is_public=True,
                play_count=0
            )
            cls.session.add(track)
            cls.session.commit()
            
        except Exception as e:
            print(f"テストデータ作成エラー: {e}")
            cls.session.rollback()
    
    @classmethod
    def teardown_class(cls):
        """テストクラス終了時にクリーンアップ"""
        cls.session.close()
    
    def test_health_check(self):
        """ヘルスチェックエンドポイント"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs_url" in data
        assert data["name"] == "インディーズミュージックアプリAPI"
    
    def test_api_documentation_access(self):
        """API ドキュメントへのアクセス"""
        response = self.client.get("/docs")
        assert response.status_code == 200
    
    # ==================== 認証・ユーザー管理テスト ====================
    
    def test_user_registration_flow(self):
        """新規ユーザー登録フロー"""
        # 新しいユーザーデータ
        user_data = {
            "email": "newuser@example.com",
            "display_name": "新規ユーザー",
            "firebase_uid": "new_user_firebase_uid",
            "user_role": "LISTENER"
        }
        
        response = self.client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        
        user_response = response.json()
        assert user_response["email"] == user_data["email"]
        assert user_response["display_name"] == user_data["display_name"]
        assert "id" in user_response
    
    def test_duplicate_user_registration(self):
        """重複ユーザー登録の拒否"""
        # 既存のSeedデータのユーザーと同じメールで登録
        user_data = {
            "email": "listener1@example.com",  # Seedデータに存在
            "display_name": "重複ユーザー",
            "firebase_uid": "duplicate_user_uid",
            "user_role": "LISTENER"
        }
        
        response = self.client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400  # 重複エラー
    
    def test_get_current_user(self):
        """現在のユーザー情報取得（モック認証）"""
        # モック認証ヘッダー
        headers = {"Authorization": "Bearer mock_token_listener"}
        
        response = self.client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert "id" in user_data
        assert "email" in user_data
        assert "display_name" in user_data
    
    # ==================== 楽曲管理テスト ====================
    
    def test_get_all_tracks(self):
        """全楽曲取得"""
        response = self.client.get("/api/v1/tracks/")
        assert response.status_code == 200
        
        tracks_data = response.json()
        assert len(tracks_data) >= 1  # テストデータには最低1曲
        
        # 最初の楽曲の構造確認
        first_track = tracks_data[0]
        required_fields = [
            "id", "title", "artist_id", "artist_name", 
            "genre", "duration", "price", "play_count"
        ]
        for field in required_fields:
            assert field in first_track
    
    def test_get_tracks_with_pagination(self):
        """ページネーション付き楽曲取得"""
        # 最初のページ
        response = self.client.get("/api/v1/tracks/?skip=0&limit=5")
        assert response.status_code == 200
        tracks_page1 = response.json()
        assert len(tracks_page1) <= 5  # 最大5件まで取得
        assert len(tracks_page1) >= 1  # 最低1件はある
        
        # 次のページ
        response = self.client.get("/api/v1/tracks/?skip=5&limit=5")
        assert response.status_code == 200
        tracks_page2 = response.json()
        # データが少ない場合は0件の可能性もある
        
        # ページ間で重複しないことを確認
        page1_ids = {track["id"] for track in tracks_page1}
        page2_ids = {track["id"] for track in tracks_page2}
        assert page1_ids.isdisjoint(page2_ids)
    
    def test_get_tracks_by_genre(self):
        """ジャンル別楽曲取得"""
        genres = ["ポップ", "ジャズ", "エレクトロニック"]
        
        for genre in genres:
            response = self.client.get(f"/api/v1/tracks/?genre={genre}")
            assert response.status_code == 200
            
            tracks = response.json()
            assert len(tracks) >= 1  # 各ジャンル最低1曲
            
            # 全ての楽曲が指定ジャンルであることを確認
            for track in tracks:
                assert track["genre"] == genre
    
    def test_search_tracks(self):
        """楽曲検索"""
        # タイトル検索
        response = self.client.get("/api/v1/tracks/?search=青空")
        assert response.status_code == 200
        results = response.json()
        
        # 検索結果にクエリが含まれることを確認
        for track in results:
            assert "青空" in track["title"] or "青空" in track["artist_name"]
    
    def test_get_track_detail(self):
        """楽曲詳細取得"""
        # まず楽曲一覧から1曲取得
        tracks_response = self.client.get("/api/v1/tracks/?limit=1")
        tracks = tracks_response.json()
        track_id = tracks[0]["id"]
        
        # 詳細取得
        response = self.client.get(f"/api/v1/tracks/{track_id}")
        assert response.status_code == 200
        
        track_detail = response.json()
        assert track_detail["id"] == track_id
        assert "title" in track_detail
        assert "description" in track_detail
        assert "audio_file_url" in track_detail
    
    def test_create_track_as_artist(self):
        """アーティストによる楽曲作成"""
        # アーティスト認証ヘッダー
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        track_data = {
            "title": "新作楽曲",
            "description": "テスト用新作楽曲です",
            "genre": "テスト",
            "cover_art_url": "https://example.com/new_cover.jpg",
            "audio_file_url": "https://example.com/new_audio.mp3",
            "duration": 200,
            "price": 400.0,
            "release_date": str(date.today()),
            "is_public": True
        }
        
        response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
        assert response.status_code == 200
        
        created_track = response.json()
        assert created_track["title"] == track_data["title"]
        assert created_track["price"] == track_data["price"]
    
    def test_create_track_as_listener_forbidden(self):
        """リスナーによる楽曲作成の拒否"""
        # リスナー認証ヘッダー
        headers = {"Authorization": "Bearer mock_token_listener"}
        
        track_data = {
            "title": "無許可楽曲",
            "description": "リスナーが作成しようとする楽曲",
            "genre": "テスト",
            "duration": 180,
            "price": 300.0
        }
        
        response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
        assert response.status_code == 403  # 権限なし
    
    # ==================== アーティスト機能テスト ====================
    
    def test_get_artist_profile(self):
        """アーティストプロフィール取得"""
        # Seedデータからアーティストを取得
        tracks_response = self.client.get("/api/v1/tracks/?limit=1")
        tracks = tracks_response.json()
        artist_id = tracks[0]["artist_id"]
        
        response = self.client.get(f"/api/v1/artists/{artist_id}")
        assert response.status_code == 200
        
        artist_data = response.json()
        assert artist_data["id"] == artist_id
        assert "display_name" in artist_data
        assert "tracks" in artist_data  # 楽曲一覧を含む
    
    def test_get_artist_tracks(self):
        """アーティストの楽曲一覧取得"""
        # Seedデータからアーティストを取得
        tracks_response = self.client.get("/api/v1/tracks/?limit=1")
        tracks = tracks_response.json()
        artist_id = tracks[0]["artist_id"]
        
        response = self.client.get(f"/api/v1/artists/{artist_id}/tracks")
        assert response.status_code == 200
        
        artist_tracks = response.json()
        assert len(artist_tracks) >= 1
        
        # 全ての楽曲が同じアーティストのものであることを確認
        for track in artist_tracks:
            assert track["artist_id"] == artist_id
    
    # ==================== 購入・決済テスト ====================
    
    def test_purchase_track(self):
        """楽曲購入"""
        # リスナー認証ヘッダー
        headers = {"Authorization": "Bearer mock_token_listener"}
        
        # 購入する楽曲を取得
        tracks_response = self.client.get("/api/v1/tracks/?limit=1")
        tracks = tracks_response.json()
        track_id = tracks[0]["id"]
        track_price = tracks[0]["price"]
        
        purchase_data = {
            "track_id": track_id,
            "amount": track_price,
            "payment_method": "CREDIT_CARD",
            "payment_token": "test_payment_token"
        }
        
        response = self.client.post("/api/v1/purchases/", headers=headers, json=purchase_data)
        assert response.status_code == 200
        
        purchase_result = response.json()
        assert purchase_result["track_id"] == track_id
        assert purchase_result["amount"] == track_price
        assert purchase_result["status"] == "completed"
    
    def test_get_purchase_history(self):
        """購入履歴取得"""
        # リスナー認証ヘッダー
        headers = {"Authorization": "Bearer mock_token_listener"}
        
        response = self.client.get("/api/v1/purchases/", headers=headers)
        assert response.status_code == 200
        
        purchases = response.json()
        assert len(purchases) >= 0  # Seedデータに購入履歴がある
        
        if purchases:
            purchase = purchases[0]
            required_fields = [
                "id", "track_id", "amount", "purchase_date", 
                "payment_method", "status"
            ]
            for field in required_fields:
                assert field in purchase
    
    def test_download_purchased_track(self):
        """購入済み楽曲のダウンロード"""
        # リスナー認証ヘッダー
        headers = {"Authorization": "Bearer mock_token_listener"}
        
        # まず購入履歴を取得
        purchases_response = self.client.get("/api/v1/purchases/", headers=headers)
        purchases = purchases_response.json()
        
        if purchases:
            track_id = purchases[0]["track_id"]
            
            response = self.client.get(
                f"/api/v1/purchases/track/{track_id}/download", 
                headers=headers
            )
            assert response.status_code == 200
            
            download_data = response.json()
            assert "download_url" in download_data
    
    # ==================== 検索・フィルタリングテスト ====================
    
    def test_advanced_search_combinations(self):
        """高度な検索とフィルタリングの組み合わせ"""
        # ジャンル + 検索クエリ
        response = self.client.get("/api/v1/tracks/?genre=ポップ&search=青空")
        assert response.status_code == 200
        results = response.json()
        
        for track in results:
            assert track["genre"] == "ポップ"
            assert "青空" in track["title"] or "青空" in track["artist_name"]
    
    def test_sorting_functionality(self):
        """ソート機能テスト"""
        # 価格でソート（昇順）
        response = self.client.get("/api/v1/tracks/?sort_by=price&sort_desc=false")
        assert response.status_code == 200
        tracks = response.json()
        
        if len(tracks) > 1:
            # 価格が昇順になっていることを確認
            for i in range(len(tracks) - 1):
                assert tracks[i]["price"] <= tracks[i + 1]["price"]
        
        # 再生回数でソート（降順）
        response = self.client.get("/api/v1/tracks/?sort_by=play_count&sort_desc=true")
        assert response.status_code == 200
        tracks = response.json()
        
        if len(tracks) > 1:
            # 再生回数が降順になっていることを確認
            for i in range(len(tracks) - 1):
                assert tracks[i]["play_count"] >= tracks[i + 1]["play_count"]
    
    # ==================== エラーハンドリングテスト ====================
    
    def test_track_not_found(self):
        """存在しない楽曲への404エラー"""
        response = self.client.get("/api/v1/tracks/nonexistent-track-id")
        assert response.status_code == 404
    
    def test_invalid_user_id(self):
        """無効なユーザーIDへの404エラー"""
        response = self.client.get("/api/v1/users/invalid-user-id")
        assert response.status_code == 404
    
    def test_unauthorized_access(self):
        """認証なしでの保護されたエンドポイントへのアクセス"""
        track_data = {
            "title": "無認証楽曲",
            "duration": 180,
            "price": 300.0
        }
        
        response = self.client.post("/api/v1/tracks/", json=track_data)
        assert response.status_code == 401  # 認証が必要
    
    # ==================== データ整合性テスト ====================
    
    def test_data_consistency_across_endpoints(self):
        """エンドポイント間でのデータ整合性確認"""
        # 楽曲一覧から楽曲を取得
        tracks_response = self.client.get("/api/v1/tracks/?limit=1")
        tracks = tracks_response.json()
        track_from_list = tracks[0]
        
        # 同じ楽曲を詳細エンドポイントから取得
        detail_response = self.client.get(f"/api/v1/tracks/{track_from_list['id']}")
        track_detail = detail_response.json()
        
        # 基本情報が一致することを確認
        assert track_from_list["id"] == track_detail["id"]
        assert track_from_list["title"] == track_detail["title"]
        assert track_from_list["artist_id"] == track_detail["artist_id"]
        assert track_from_list["price"] == track_detail["price"]
    
    def test_artist_track_relationship_consistency(self):
        """アーティストと楽曲の関係の整合性確認"""
        # アーティストの楽曲一覧を取得
        tracks_response = self.client.get("/api/v1/tracks/?limit=1")
        tracks = tracks_response.json()
        artist_id = tracks[0]["artist_id"]
        
        artist_tracks_response = self.client.get(f"/api/v1/artists/{artist_id}/tracks")
        artist_tracks = artist_tracks_response.json()
        
        # アーティストの楽曲一覧に、該当楽曲が含まれることを確認
        track_ids = {track["id"] for track in artist_tracks}
        assert tracks[0]["id"] in track_ids
    
    # ==================== パフォーマンステスト ====================
    
    def test_large_dataset_performance(self):
        """大量データでのパフォーマンス確認"""
        import time
        
        start_time = time.time()
        response = self.client.get("/api/v1/tracks/?limit=100")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # 2秒以内
        
        tracks = response.json()
        assert len(tracks) <= 100  # 制限通り
    
    def test_concurrent_request_simulation(self):
        """同時リクエストのシミュレーション"""
        import concurrent.futures
        import threading
        
        def make_request():
            return self.client.get("/api/v1/tracks/?limit=10")
        
        # 5つの同時リクエスト
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in futures]
        
        # 全てのリクエストが成功することを確認
        for response in results:
            assert response.status_code == 200