"""
フルスタック統合テストスイート

バックエンド、データベース、外部サービス（モック）の
完全な統合をテストします。
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from seed_data import create_seed_data


class TestFullIntegration:
    """フルスタック統合テストクラス"""
    
    @classmethod
    def setup_class(cls):
        """統合テスト用のセットアップ"""
        print("🔧 統合テスト環境をセットアップ中...")
        
        # Seedデータの作成
        create_seed_data()
        
        cls.client = TestClient(app)
        cls.session = SessionLocal()
        
        print("✅ 統合テスト環境のセットアップ完了")
    
    @classmethod  
    def teardown_class(cls):
        """統合テスト環境のクリーンアップ"""
        cls.session.close()
    
    # ==================== 認証統合フローテスト ====================
    
    @patch('app.services.auth_service.firebase_admin')
    def test_complete_authentication_flow(self, mock_firebase):
        """Firebase認証統合フロー"""
        # Firebase認証のモック
        mock_firebase.auth.verify_id_token.return_value = {
            'uid': 'test_firebase_uid',
            'email': 'integration_test@example.com'
        }
        
        # 1. ユーザー登録
        user_data = {
            "email": "integration_test@example.com",
            "display_name": "統合テストユーザー",
            "firebase_uid": "test_firebase_uid",
            "user_role": "LISTENER"
        }
        
        register_response = self.client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 200
        
        user_id = register_response.json()["id"]
        
        # 2. Firebase トークン検証
        headers = {"Authorization": "Bearer mock_firebase_token"}
        
        with patch('app.api.dependencies.auth.verify_firebase_token') as mock_verify:
            mock_verify.return_value = user_data["firebase_uid"]
            
            me_response = self.client.get("/api/v1/auth/me", headers=headers)
            assert me_response.status_code == 200
            assert me_response.json()["id"] == user_id
    
    # ==================== 楽曲管理統合フローテスト ====================
    
    @patch('app.services.storage.boto3')
    def test_complete_track_upload_flow(self, mock_boto3):
        """楽曲アップロード完全フロー"""
        # S3アップロードのモック
        mock_s3_client = MagicMock()
        mock_boto3.client.return_value = mock_s3_client
        mock_s3_client.upload_fileobj.return_value = None
        mock_s3_client.generate_presigned_url.return_value = "https://s3.amazonaws.com/test-url"
        
        # アーティスト認証
        headers = {"Authorization": "Bearer mock_artist_token"}
        
        # 1. 音声ファイルアップロード
        audio_files = {'file': ('test_audio.mp3', b'mock audio content', 'audio/mpeg')}
        
        with patch('app.api.dependencies.auth.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id="artist_id", user_role="ARTIST")
            
            audio_response = self.client.post(
                "/api/v1/tracks/upload/audio",
                headers=headers,
                files=audio_files
            )
            assert audio_response.status_code == 200
            audio_url = audio_response.json()["url"]
        
        # 2. カバーアートアップロード
        cover_files = {'file': ('test_cover.jpg', b'mock image content', 'image/jpeg')}
        
        with patch('app.api.dependencies.auth.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id="artist_id", user_role="ARTIST")
            
            cover_response = self.client.post(
                "/api/v1/tracks/upload/cover",
                headers=headers,
                files=cover_files
            )
            assert cover_response.status_code == 200
            cover_url = cover_response.json()["url"]
        
        # 3. 楽曲メタデータ作成
        track_data = {
            "title": "統合テスト楽曲",
            "description": "統合テスト用の楽曲です",
            "genre": "テスト",
            "cover_art_url": cover_url,
            "audio_file_url": audio_url,
            "duration": 180,
            "price": 400.0,
            "release_date": "2024-01-01",
            "is_public": True
        }
        
        with patch('app.api.dependencies.auth.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id="artist_id", user_role="ARTIST")
            
            track_response = self.client.post(
                "/api/v1/tracks/",
                headers=headers,
                json=track_data
            )
            assert track_response.status_code == 200
            
            created_track = track_response.json()
            assert created_track["title"] == track_data["title"]
            assert created_track["audio_file_url"] == audio_url
            assert created_track["cover_art_url"] == cover_url
        
        # 4. 作成された楽曲の検索確認
        search_response = self.client.get(f"/api/v1/tracks/?search={track_data['title']}")
        assert search_response.status_code == 200
        
        search_results = search_response.json()
        assert len(search_results) > 0
        assert any(track["title"] == track_data["title"] for track in search_results)
    
    # ==================== 決済統合フローテスト ====================
    
    @patch('app.services.payment.stripe')
    def test_complete_purchase_flow(self, mock_stripe):
        """完全な購入決済フロー"""
        # Stripe決済のモック
        mock_payment_intent = MagicMock()
        mock_payment_intent.id = "pi_test_payment_intent"
        mock_payment_intent.status = "succeeded"
        mock_stripe.PaymentIntent.create.return_value = mock_payment_intent
        
        # リスナー認証
        headers = {"Authorization": "Bearer mock_listener_token"}
        
        # 1. 購入する楽曲を検索・選択
        tracks_response = self.client.get("/api/v1/tracks/?limit=1")
        tracks = tracks_response.json()
        target_track = tracks[0]
        
        # 2. 決済処理実行
        purchase_data = {
            "track_id": target_track["id"],
            "amount": target_track["price"],
            "payment_method": "CREDIT_CARD",
            "payment_token": "test_payment_token"
        }
        
        with patch('app.api.dependencies.auth.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id="listener_id", user_role="LISTENER")
            
            purchase_response = self.client.post(
                "/api/v1/purchases/",
                headers=headers,
                json=purchase_data
            )
            assert purchase_response.status_code == 200
            
            purchase_result = purchase_response.json()
            assert purchase_result["track_id"] == target_track["id"]
            assert purchase_result["status"] == "completed"
            assert purchase_result["transaction_id"] == "pi_test_payment_intent"
        
        # 3. 購入履歴確認
        with patch('app.api.dependencies.auth.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id="listener_id", user_role="LISTENER")
            
            history_response = self.client.get("/api/v1/purchases/", headers=headers)
            assert history_response.status_code == 200
            
            purchases = history_response.json()
            assert len(purchases) > 0
            assert any(p["track_id"] == target_track["id"] for p in purchases)
        
        # 4. ダウンロードURL取得
        with patch('app.api.dependencies.auth.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id="listener_id", user_role="LISTENER")
            
            download_response = self.client.get(
                f"/api/v1/purchases/track/{target_track['id']}/download",
                headers=headers
            )
            assert download_response.status_code == 200
            
            download_data = download_response.json()
            assert "download_url" in download_data
    
    # ==================== データ整合性統合テスト ====================
    
    def test_data_consistency_across_operations(self):
        """複数操作でのデータ整合性確認"""
        # 1. 初期データ状態確認
        initial_tracks = self.client.get("/api/v1/tracks/").json()
        initial_count = len(initial_tracks)
        
        # 2. 新しいアーティストと楽曲作成
        artist_data = {
            "email": "consistency_artist@example.com",
            "display_name": "整合性テストアーティスト",
            "firebase_uid": "consistency_artist_uid",
            "user_role": "ARTIST"
        }
        
        artist_response = self.client.post("/api/v1/auth/register", json=artist_data)
        artist_id = artist_response.json()["id"]
        
        # アーティスト認証ヘッダー
        headers = {"Authorization": "Bearer mock_artist_token"}
        
        track_data = {
            "title": "整合性テスト楽曲",
            "description": "データ整合性確認用楽曲",
            "genre": "テスト",
            "cover_art_url": "https://example.com/cover.jpg",
            "audio_file_url": "https://example.com/audio.mp3",
            "duration": 200,
            "price": 350.0,
            "release_date": "2024-01-01",
            "is_public": True
        }
        
        with patch('app.api.dependencies.auth.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id=artist_id, user_role="ARTIST")
            
            track_response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            created_track = track_response.json()
            track_id = created_track["id"]
        
        # 3. データ整合性確認
        # 楽曲総数の増加確認
        updated_tracks = self.client.get("/api/v1/tracks/").json()
        assert len(updated_tracks) == initial_count + 1
        
        # アーティスト楽曲一覧に含まれることを確認
        artist_tracks_response = self.client.get(f"/api/v1/artists/{artist_id}/tracks")
        artist_tracks = artist_tracks_response.json()
        assert any(track["id"] == track_id for track in artist_tracks)
        
        # 楽曲詳細の整合性確認
        track_detail_response = self.client.get(f"/api/v1/tracks/{track_id}")
        track_detail = track_detail_response.json()
        assert track_detail["artist_id"] == artist_id
        assert track_detail["title"] == track_data["title"]
        
        # 4. 楽曲更新・削除の整合性
        update_data = {"title": "更新された楽曲タイトル", "price": 400.0}
        
        with patch('app.api.dependencies.auth.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id=artist_id, user_role="ARTIST")
            
            update_response = self.client.put(f"/api/v1/tracks/{track_id}", headers=headers, json=update_data)
            updated_track = update_response.json()
            assert updated_track["title"] == update_data["title"]
            assert updated_track["price"] == update_data["price"]
        
        # 更新が検索結果に反映されることを確認
        search_response = self.client.get(f"/api/v1/tracks/?search={update_data['title']}")
        search_results = search_response.json()
        assert any(track["id"] == track_id for track in search_results)
    
    # ==================== 同時実行・競合状態テスト ====================
    
    def test_concurrent_operations(self):
        """同時実行での競合状態テスト"""
        
        def create_user(user_id):
            """並行ユーザー作成"""
            user_data = {
                "email": f"concurrent_user_{user_id}@example.com",
                "display_name": f"同時実行ユーザー{user_id}",
                "firebase_uid": f"concurrent_uid_{user_id}",
                "user_role": "LISTENER"
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            return response.status_code == 200
        
        def purchase_track(user_id):
            """並行楽曲購入"""
            # 最初の楽曲を取得
            tracks_response = self.client.get("/api/v1/tracks/?limit=1")
            if tracks_response.status_code != 200:
                return False
            
            tracks = tracks_response.json()
            if not tracks:
                return False
                
            track = tracks[0]
            
            purchase_data = {
                "track_id": track["id"],
                "amount": track["price"],
                "payment_method": "CREDIT_CARD",
                "payment_token": f"test_token_{user_id}"
            }
            
            headers = {"Authorization": f"Bearer mock_token_{user_id}"}
            
            with patch('app.api.dependencies.auth.get_current_user') as mock_user:
                mock_user.return_value = MagicMock(id=f"user_{user_id}", user_role="LISTENER")
                
                response = self.client.post("/api/v1/purchases/", headers=headers, json=purchase_data)
                return response.status_code == 200
        
        # 1. 並行ユーザー作成テスト
        with ThreadPoolExecutor(max_workers=5) as executor:
            user_futures = [executor.submit(create_user, i) for i in range(5)]
            user_results = [future.result() for future in user_futures]
        
        # 全てのユーザー作成が成功することを確認
        assert all(user_results), "並行ユーザー作成でエラーが発生"
        
        # 2. 並行購入処理テスト
        with ThreadPoolExecutor(max_workers=3) as executor:
            purchase_futures = [executor.submit(purchase_track, i) for i in range(3)]
            purchase_results = [future.result() for future in purchase_futures]
        
        # 全ての購入が成功することを確認
        assert all(purchase_results), "並行購入処理でエラーが発生"
    
    # ==================== パフォーマンス統合テスト ====================
    
    def test_api_response_performance(self):
        """API レスポンス性能テスト"""
        
        performance_results = {}
        
        # 1. 楽曲一覧取得性能
        start_time = time.time()
        response = self.client.get("/api/v1/tracks/?limit=50")
        end_time = time.time()
        
        assert response.status_code == 200
        performance_results["track_list"] = end_time - start_time
        assert performance_results["track_list"] < 1.0, "楽曲一覧取得が1秒を超過"
        
        # 2. 検索性能
        start_time = time.time()
        response = self.client.get("/api/v1/tracks/?search=テスト&genre=ポップ")
        end_time = time.time()
        
        assert response.status_code == 200
        performance_results["search"] = end_time - start_time
        assert performance_results["search"] < 2.0, "検索処理が2秒を超過"
        
        # 3. 楽曲詳細取得性能
        tracks = self.client.get("/api/v1/tracks/?limit=1").json()
        track_id = tracks[0]["id"]
        
        start_time = time.time()
        response = self.client.get(f"/api/v1/tracks/{track_id}")
        end_time = time.time()
        
        assert response.status_code == 200
        performance_results["track_detail"] = end_time - start_time
        assert performance_results["track_detail"] < 0.5, "楽曲詳細取得が0.5秒を超過"
        
        # 4. 購入処理性能
        purchase_data = {
            "track_id": track_id,
            "amount": 300.0,
            "payment_method": "CREDIT_CARD", 
            "payment_token": "perf_test_token"
        }
        
        headers = {"Authorization": "Bearer mock_perf_token"}
        
        with patch('app.api.dependencies.auth.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id="perf_user", user_role="LISTENER")
            
            with patch('app.services.payment.stripe.PaymentIntent.create') as mock_payment:
                mock_payment.return_value = MagicMock(id="pi_perf_test", status="succeeded")
                
                start_time = time.time()
                response = self.client.post("/api/v1/purchases/", headers=headers, json=purchase_data)
                end_time = time.time()
        
        assert response.status_code == 200
        performance_results["purchase"] = end_time - start_time
        assert performance_results["purchase"] < 3.0, "購入処理が3秒を超過"
        
        # パフォーマンス結果のログ出力
        print("\n📊 API パフォーマンス結果:")
        for operation, duration in performance_results.items():
            print(f"  {operation}: {duration:.3f}秒")
    
    def test_database_query_optimization(self):
        """データベースクエリ最適化確認"""
        
        # 1. N+1問題の確認（楽曲とアーティスト情報）
        import logging
        
        # SQLAlchemyのクエリログを有効化
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        
        # 楽曲一覧取得（アーティスト情報含む）
        response = self.client.get("/api/v1/tracks/?limit=10")
        assert response.status_code == 200
        
        tracks = response.json()
        assert len(tracks) == 10
        
        # 各楽曲にアーティスト情報が含まれることを確認
        for track in tracks:
            assert "artist_name" in track
            assert track["artist_name"] is not None
        
        # 2. 検索クエリ効率性確認
        search_response = self.client.get("/api/v1/tracks/?search=test&genre=ポップ&limit=20")
        assert search_response.status_code == 200
        
        # 結果が正しくフィルタリングされていることを確認
        search_results = search_response.json()
        for track in search_results:
            assert track["genre"] == "ポップ"
    
    # ==================== エラーハンドリング統合テスト ====================
    
    def test_error_handling_integration(self):
        """エラーハンドリング統合テスト"""
        
        # 1. データベース接続エラーシミュレーション
        with patch('app.db.session.SessionLocal') as mock_session:
            mock_session.side_effect = Exception("Database connection error")
            
            response = self.client.get("/api/v1/tracks/")
            assert response.status_code == 500
            
            error_data = response.json()
            assert "detail" in error_data
        
        # 2. 外部サービスエラーシミュレーション
        with patch('app.services.payment.stripe.PaymentIntent.create') as mock_payment:
            mock_payment.side_effect = Exception("Payment service unavailable")
            
            purchase_data = {
                "track_id": "test_track_id",
                "amount": 300.0,
                "payment_method": "CREDIT_CARD",
                "payment_token": "error_test_token"
            }
            
            headers = {"Authorization": "Bearer mock_error_token"}
            
            with patch('app.api.dependencies.auth.get_current_user') as mock_user:
                mock_user.return_value = MagicMock(id="error_user", user_role="LISTENER")
                
                response = self.client.post("/api/v1/purchases/", headers=headers, json=purchase_data)
                assert response.status_code == 500
        
        # 3. 認証エラーハンドリング
        response = self.client.get("/api/v1/auth/me")  # 認証ヘッダーなし
        assert response.status_code == 401
        
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/api/v1/auth/me", headers=invalid_headers)
        assert response.status_code == 401
    
    # ==================== セキュリティ統合テスト ====================
    
    def test_security_integration(self):
        """セキュリティ統合テスト"""
        
        # 1. SQLインジェクション対策確認
        malicious_query = "'; DROP TABLE user; --"
        response = self.client.get(f"/api/v1/tracks/?search={malicious_query}")
        assert response.status_code == 200  # エラーにならずに正常処理される
        
        # 2. XSS対策確認
        xss_payload = "<script>alert('xss')</script>"
        track_data = {
            "title": xss_payload,
            "description": "テスト楽曲",
            "genre": "テスト",
            "duration": 180,
            "price": 300.0
        }
        
        headers = {"Authorization": "Bearer mock_artist_token"}
        
        with patch('app.api.dependencies.auth.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id="security_test_artist", user_role="ARTIST")
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            
            if response.status_code == 200:
                created_track = response.json()
                # XSSペイロードがサニタイズされていることを確認
                assert created_track["title"] != xss_payload
        
        # 3. 認可テスト（権限不正使用）
        # リスナーがアーティスト専用機能にアクセスしようとする
        with patch('app.api.dependencies.auth.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id="unauthorized_user", user_role="LISTENER")
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code == 403  # 権限なし
        
        # 4. レート制限テスト（簡易版）
        # 短時間での大量リクエスト
        responses = []
        for _ in range(100):
            response = self.client.get("/api/v1/tracks/?limit=1")
            responses.append(response.status_code)
        
        # 全てのリクエストが正常処理されるか、適切にレート制限されることを確認
        success_count = sum(1 for status in responses if status == 200)
        rate_limited_count = sum(1 for status in responses if status == 429)
        
        assert success_count > 0, "全てのリクエストが失敗"
        assert success_count + rate_limited_count == 100, "予期しないレスポンスコード"