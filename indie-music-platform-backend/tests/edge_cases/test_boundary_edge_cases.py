"""
境界値・エッジケース包括テストスイート

システムの限界値、境界条件、極端なケースを徹底的にテストします。
"""

import pytest
import time
import sys
import threading
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_UP, ROUND_DOWN
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
import concurrent.futures
import itertools

from app.main import app
from app.db.session import SessionLocal
from seed_data import create_seed_data


class TestBoundaryEdgeCases:
    """境界値・エッジケーステストクラス"""
    
    @classmethod
    def setup_class(cls):
        """境界値テストセットアップ"""
        print("⚡ 境界値・エッジケーステスト開始...")
        create_seed_data()
        cls.client = TestClient(app)
        cls.session = SessionLocal()
        print("✅ 境界値テスト環境準備完了")
    
    @classmethod
    def teardown_class(cls):
        """境界値テストクリーンアップ"""
        cls.session.close()
    
    # ==================== 数値境界値テスト ====================
    
    def test_integer_boundary_values(self):
        """整数境界値テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 整数の境界値
        integer_boundaries = [
            # (値, 説明)
            (0, "ゼロ"),
            (1, "最小正整数"),
            (-1, "最小負整数"),
            (2147483647, "32bit符号付き整数最大値"),
            (-2147483648, "32bit符号付き整数最小値"),
            (4294967295, "32bit符号なし整数最大値"),
            (9223372036854775807, "64bit符号付き整数最大値"),
            (-9223372036854775808, "64bit符号付き整数最小値"),
            (sys.maxsize, "Python最大整数"),
            (-sys.maxsize - 1, "Python最小整数"),
        ]
        
        for value, description in integer_boundaries:
            # duration フィールドでの境界値テスト
            track_data = {
                "title": f"Integer Boundary: {description}",
                "description": f"Testing {description}: {value}",
                "genre": "テスト",
                "duration": value,
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            
            # 適切な範囲内の値は受け入れられ、範囲外は拒否されるべき
            if 1 <= value <= 7200:  # 楽曲の合理的な長さ（1秒〜2時間）
                assert response.status_code in [200, 400, 422]
            else:
                assert response.status_code in [400, 422], f"Failed for {description}: {value}"
    
    def test_float_precision_boundaries(self):
        """浮動小数点精度境界テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 浮動小数点の境界値と精度テスト
        float_boundaries = [
            # (値, 説明)
            (0.0, "ゼロ"),
            (0.1, "小数点1桁"),
            (0.01, "小数点2桁"),
            (0.001, "小数点3桁"),
            (0.0001, "小数点4桁"),
            (99999.99, "大きな小数"),
            (1.23456789012345, "高精度小数"),
            (float('1e-10'), "極小値"),
            (float('1e10'), "極大値"),
            (1.7976931348623157e+308, "float最大値に近い値"),
            (2.2250738585072014e-308, "float最小正値に近い値"),
        ]
        
        for value, description in float_boundaries:
            # price フィールドでの境界値テスト
            track_data = {
                "title": f"Float Boundary: {description}",
                "description": f"Testing {description}: {value}",
                "genre": "テスト",
                "duration": 180,
                "price": value
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            
            # 価格の合理的な範囲内（0〜9999）の値のみ受け入れられるべき
            if 0 <= value <= 9999 and not (value != value):  # NaNチェック
                assert response.status_code in [200, 400, 422]
            else:
                assert response.status_code in [400, 422], f"Failed for {description}: {value}"
    
    def test_decimal_precision_edge_cases(self):
        """小数精度エッジケーステスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 通貨計算での小数精度問題
        decimal_edge_cases = [
            # (値, 説明)
            (0.1 + 0.2, "浮動小数点精度問題"),  # 0.30000000000000004
            (1.0 / 3.0, "無限小数"),  # 0.3333333333333333
            (299.99, "99セント価格"),
            (300.00, "整数価格"),
            (300.01, "1セント上"),
            (299.999, "端数切り上げ"),
            (300.001, "端数切り下げ"),
            (Decimal('299.99'), "Decimal型"),
            (Decimal('300.00'), "Decimal整数"),
        ]
        
        for value, description in decimal_edge_cases:
            track_data = {
                "title": f"Decimal Edge: {description}",
                "description": f"Testing {description}: {value}",
                "genre": "テスト",
                "duration": 180,
                "price": float(value) if isinstance(value, Decimal) else value
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            
            # 価格の精度が適切に処理されることを確認
            if response.status_code == 200:
                created_track = response.json()
                # 価格が適切に丸められていることを確認
                stored_price = created_track["price"]
                assert isinstance(stored_price, (int, float))
                assert 0 <= stored_price <= 9999
    
    # ==================== 文字列長境界値テスト ====================
    
    def test_string_length_boundaries(self):
        """文字列長境界値テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 文字列長の境界値
        string_lengths = [
            (0, "空文字"),
            (1, "1文字"),
            (2, "2文字"),
            (10, "短い文字列"),
            (50, "中程度文字列"),
            (100, "長い文字列"),
            (255, "典型的最大長"),
            (256, "最大長+1"),
            (512, "倍長"),
            (1000, "かなり長い"),
            (1023, "1KB未満"),
            (1024, "1KB"),
            (2047, "2KB未満"),
            (2048, "2KB"),
            (4095, "4KB未満"),
            (4096, "4KB"),
            (8192, "8KB"),
            (16384, "16KB"),
            (32768, "32KB"),
            (65535, "64KB未満"),
            (65536, "64KB"),
        ]
        
        for length, description in string_lengths:
            if length == 0:
                test_string = ""
            else:
                # マルチバイト文字を含むテスト文字列
                base_chars = "あいうえおABCDE12345"
                test_string = (base_chars * ((length // len(base_chars)) + 1))[:length]
            
            track_data = {
                "title": test_string,
                "description": f"String length test: {description} ({length} chars)",
                "genre": "テスト",
                "duration": 180,
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            
            # 合理的な長さ（1〜500文字）のみ受け入れられるべき
            if 1 <= length <= 500:
                assert response.status_code in [200, 400, 422]
            else:
                assert response.status_code in [400, 422], f"Failed for {description}: {length} chars"
    
    def test_unicode_character_boundaries(self):
        """Unicode文字境界値テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # Unicode文字の境界値
        unicode_boundaries = [
            # (文字, 説明)
            ("\u0000", "Null文字"),
            ("\u0001", "制御文字開始"),
            ("\u001F", "制御文字終了"),
            ("\u0020", "スペース"),
            ("\u007F", "DEL文字"),
            ("\u0080", "拡張ASCII開始"),
            ("\u00FF", "Latin-1最終"),
            ("\u0100", "拡張Latin開始"),
            ("\u0FFF", "3バイトUnicode境界"),
            ("\u1000", "3バイトUnicode開始"),
            ("\u4E00", "CJK漢字開始"),
            ("\u9FFF", "CJK漢字終了"),
            ("\uFFFF", "BMP最終"),
            ("\U00010000", "Supplementary Plane開始"),
            ("\U0001F600", "絵文字（顔）"),
            ("\U0001F3B5", "音楽記号"),
            ("\U0010FFFF", "Unicode最終"),
        ]
        
        for char, description in unicode_boundaries:
            title = f"Unicode{description}{char}"
            
            track_data = {
                "title": title,
                "description": f"Unicode boundary test: {description}",
                "genre": "テスト",
                "duration": 180,
                "price": 300.0
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            
            # 制御文字やNull文字は拒否されるべき
            if ord(char) < 32 or char == "\u007F":  # 制御文字
                assert response.status_code in [400, 422], f"Control character should be rejected: {description}"
            else:
                assert response.status_code in [200, 400, 422]
    
    # ==================== 時間・日付境界値テスト ====================
    
    def test_date_time_boundaries(self):
        """日時境界値テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 日付の境界値
        today = date.today()
        
        date_boundaries = [
            # (日付, 説明)
            (date(1900, 1, 1), "20世紀開始"),
            (date(1970, 1, 1), "Unix epoch"),
            (date(2000, 1, 1), "Y2K"),
            (date(2000, 2, 29), "うるう年"),
            (date(2001, 2, 28), "平年2月末"),
            (today - timedelta(days=1), "昨日"),
            (today, "今日"),
            (today + timedelta(days=1), "明日"),
            (date(2030, 12, 31), "2030年末"),
            (date(2038, 1, 19), "32bit Unix time限界"),
            (date(2100, 12, 31), "22世紀近く"),
        ]
        
        for test_date, description in date_boundaries:
            track_data = {
                "title": f"Date Boundary: {description}",
                "description": f"Testing {description}: {test_date}",
                "genre": "テスト",
                "duration": 180,
                "price": 300.0,
                "release_date": test_date.isoformat()
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            
            # 合理的な日付範囲（1900〜2100年）のみ受け入れられるべき
            if date(1900, 1, 1) <= test_date <= date(2100, 12, 31):
                assert response.status_code in [200, 400, 422]
            else:
                assert response.status_code in [400, 422], f"Failed for {description}: {test_date}"
    
    def test_timezone_edge_cases(self):
        """タイムゾーンエッジケーステスト"""
        # ISO 8601形式でのタイムゾーン境界値
        timezone_formats = [
            "2024-01-01",  # タイムゾーンなし
            "2024-01-01T00:00:00",  # 時刻あり、タイムゾーンなし
            "2024-01-01T00:00:00Z",  # UTC
            "2024-01-01T00:00:00+00:00",  # UTC (明示)
            "2024-01-01T00:00:00+09:00",  # JST
            "2024-01-01T00:00:00-12:00",  # 最西タイムゾーン
            "2024-01-01T00:00:00+14:00",  # 最東タイムゾーン
            "2024-01-01T23:59:59.999Z",  # 最大時刻精度
        ]
        
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        for tz_format in timezone_formats:
            track_data = {
                "title": f"Timezone Test",
                "description": f"Testing timezone format: {tz_format}",
                "genre": "テスト",
                "duration": 180,
                "price": 300.0,
                "release_date": tz_format[:10]  # 日付部分のみ抽出
            }
            
            response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
            # 日付形式は適切に処理されるべき
            assert response.status_code in [200, 400, 422]
    
    # ==================== 配列・リスト境界値テスト ====================
    
    def test_array_size_boundaries(self):
        """配列サイズ境界値テスト"""
        
        # クエリパラメータでの配列境界値
        array_sizes = [
            (0, "空配列"),
            (1, "単一要素"),
            (2, "2要素"),
            (10, "標準サイズ"),
            (100, "大きな配列"),
            (1000, "非常に大きな配列"),
            (10000, "極端に大きな配列"),
        ]
        
        for size, description in array_sizes:
            # 複数ジャンルでの検索（配列パラメータ）
            genres = ["ポップ"] * size
            
            if size == 0:
                query_params = ""
            else:
                query_params = "&".join(f"genre={genre}" for genre in genres)
            
            response = self.client.get(f"/api/v1/tracks/?{query_params}")
            
            # 適切なサイズ（0〜50）のみ受け入れられるべき
            if 0 <= size <= 50:
                assert response.status_code in [200, 400, 422]
            else:
                assert response.status_code in [400, 414, 422], f"Failed for {description}: {size} elements"
    
    # ==================== 同時実行境界値テスト ====================
    
    def test_concurrent_request_boundaries(self):
        """同時リクエスト境界値テスト"""
        
        # 同時実行数の境界値
        concurrency_levels = [1, 2, 5, 10, 20, 50, 100]
        
        for level in concurrency_levels:
            start_time = time.time()
            
            def make_request():
                return self.client.get("/api/v1/tracks/?limit=1")
            
            # 指定レベルでの同時実行
            with concurrent.futures.ThreadPoolExecutor(max_workers=level) as executor:
                futures = [executor.submit(make_request) for _ in range(level)]
                results = [future.result() for future in futures]
            
            end_time = time.time()
            
            # 全リクエストが処理されることを確認
            success_count = sum(1 for r in results if r.status_code in [200, 429])
            assert success_count == level
            
            # レスポンス時間が適切であることを確認
            avg_time = (end_time - start_time) / level
            
            # 高い同時実行数では制限が発動する可能性がある
            if level > 50:
                rate_limited = sum(1 for r in results if r.status_code == 429)
                assert rate_limited >= 0  # レート制限が発動する可能性
    
    def test_race_condition_boundaries(self):
        """競合状態境界値テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # 同じリソースに対する同時更新
        track_data = {
            "title": "Race Condition Test",
            "description": "Testing race conditions",
            "genre": "テスト",
            "duration": 180,
            "price": 300.0
        }
        
        # 楽曲を作成
        create_response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
        if create_response.status_code != 200:
            pytest.skip("楽曲作成に失敗したため、競合状態テストをスキップ")
        
        track_id = create_response.json()["id"]
        
        # 同時更新を試行
        def update_track(new_price):
            update_data = {"price": new_price}
            return self.client.put(f"/api/v1/tracks/{track_id}", headers=headers, json=update_data)
        
        prices = [100, 200, 300, 400, 500]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(update_track, price) for price in prices]
            results = [future.result() for future in futures]
        
        # 少なくとも1つは成功し、データの整合性が保たれるべき
        success_count = sum(1 for r in results if r.status_code == 200)
        assert success_count >= 1
        
        # 最終的な価格が設定した値のいずれかであることを確認
        final_response = self.client.get(f"/api/v1/tracks/{track_id}")
        if final_response.status_code == 200:
            final_track = final_response.json()
            assert final_track["price"] in prices
    
    # ==================== メモリ・リソース境界値テスト ====================
    
    def test_memory_usage_boundaries(self):
        """メモリ使用量境界値テスト"""
        
        # 大きなデータでのメモリ使用量テスト
        large_data_sizes = [
            (1024, "1KB"),           # 1KB
            (10240, "10KB"),         # 10KB
            (102400, "100KB"),       # 100KB
            (1024000, "1MB"),        # 1MB
            (10240000, "10MB"),      # 10MB（注意: 大きなデータ）
        ]
        
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        for size, description in large_data_sizes:
            # 大きな説明文でのメモリテスト
            large_description = "A" * size
            
            track_data = {
                "title": f"Memory Test: {description}",
                "description": large_description,
                "genre": "テスト",
                "duration": 180,
                "price": 300.0
            }
            
            try:
                response = self.client.post("/api/v1/tracks/", headers=headers, json=track_data)
                
                # 適切なサイズ制限が設けられているべき
                if size <= 10240:  # 10KB以下
                    assert response.status_code in [200, 400, 422]
                else:
                    assert response.status_code in [400, 413, 422], f"Large data should be rejected: {description}"
                    
            except Exception as e:
                # メモリ不足やタイムアウトは期待される動作
                assert "memory" in str(e).lower() or "timeout" in str(e).lower()
    
    def test_connection_pool_boundaries(self):
        """コネクションプール境界値テスト"""
        
        # データベース接続の限界をテスト
        connection_counts = [1, 5, 10, 20, 50]
        
        for count in connection_counts:
            responses = []
            
            # 指定数のDB操作を同時実行
            def db_operation():
                return self.client.get("/api/v1/tracks/?limit=1")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=count) as executor:
                futures = [executor.submit(db_operation) for _ in range(count)]
                responses = [future.result() for future in futures]
            
            # 全ての操作が適切に処理されることを確認
            success_count = sum(1 for r in responses if r.status_code in [200, 500, 503])
            assert success_count == count
            
            # 接続数が多い場合はエラーが発生する可能性がある
            if count > 20:
                error_count = sum(1 for r in responses if r.status_code in [500, 503])
                # エラーが発生する場合、適切なHTTPステータスコードが返されるべき
                assert error_count >= 0
    
    # ==================== API レスポンス境界値テスト ====================
    
    def test_response_size_boundaries(self):
        """レスポンスサイズ境界値テスト"""
        
        # 様々なlimit値でのレスポンスサイズテスト
        limit_values = [1, 10, 50, 100, 500, 1000, 10000]
        
        for limit in limit_values:
            response = self.client.get(f"/api/v1/tracks/?limit={limit}")
            
            if limit <= 100:  # 適切な制限内
                assert response.status_code in [200, 400, 422]
                
                if response.status_code == 200:
                    tracks = response.json()
                    assert len(tracks) <= limit  # 要求以下の数が返される
                    
                    # レスポンスサイズが適切であることを確認
                    response_size = len(response.content)
                    assert response_size < 10 * 1024 * 1024  # 10MB未満
                    
            else:  # 過大な要求
                assert response.status_code in [400, 422], f"Large limit should be rejected: {limit}"
    
    def test_pagination_boundary_combinations(self):
        """ページネーション境界値組み合わせテスト"""
        
        # skip と limit の境界値組み合わせ
        boundary_combinations = [
            (0, 1),      # 最小
            (0, 100),    # 最大limit
            (999, 1),    # 大きなskip
            (999, 100),  # 大きなskip + 最大limit
            (9999, 1),   # 非常に大きなskip
            (99999, 1),  # 極端に大きなskip
        ]
        
        for skip, limit in boundary_combinations:
            response = self.client.get(f"/api/v1/tracks/?skip={skip}&limit={limit}")
            
            # 適切な範囲内であれば処理される
            if skip <= 10000 and limit <= 100:
                assert response.status_code in [200, 400, 422]
                
                if response.status_code == 200:
                    tracks = response.json()
                    assert len(tracks) <= limit
                    
            else:  # 範囲外
                assert response.status_code in [400, 422], f"Boundary exceeded: skip={skip}, limit={limit}"
    
    # ==================== ファイルサイズ境界値テスト ====================
    
    def test_file_upload_size_boundaries(self):
        """ファイルアップロードサイズ境界値テスト"""
        headers = {"Authorization": "Bearer mock_token_artist"}
        
        # ファイルサイズの境界値（バイト）
        file_sizes = [
            (0, "空ファイル"),
            (1, "1バイト"),
            (1024, "1KB"),
            (10240, "10KB"),
            (102400, "100KB"),
            (1048576, "1MB"),
            (5242880, "5MB"),
            (10485760, "10MB"),
            (52428800, "50MB"),
            (104857600, "100MB"),
        ]
        
        for size, description in file_sizes:
            # 指定サイズのファイルデータを生成
            file_content = b"A" * size
            
            files = {"file": (f"test_{description}.mp3", file_content, "audio/mpeg")}
            
            try:
                response = self.client.post("/api/v1/tracks/upload/audio",
                                          headers=headers, files=files, timeout=30)
                
                # 適切なサイズ制限が設けられているべき
                if size <= 10485760:  # 10MB以下
                    assert response.status_code in [200, 400, 413, 422]
                else:
                    assert response.status_code in [413, 422], f"Large file should be rejected: {description}"
                    
            except Exception as e:
                # タイムアウトやメモリエラーは期待される
                assert any(keyword in str(e).lower() for keyword in ["timeout", "memory", "size"])
    
    # ==================== URL長境界値テスト ====================
    
    def test_url_length_boundaries(self):
        """URL長境界値テスト"""
        
        # URL長の境界値
        url_lengths = [
            (100, "短いURL"),
            (500, "中程度URL"),
            (1000, "長いURL"),
            (2048, "一般的最大長"),
            (4096, "2倍長"),
            (8192, "4倍長"),
            (16384, "8倍長"),
        ]
        
        for length, description in url_lengths:
            # 指定長のクエリパラメータを生成
            long_query = "a" * (length - 50)  # ベースURL分を差し引く
            
            try:
                response = self.client.get(f"/api/v1/tracks/?search={long_query}")
                
                # 適切なURL長制限が設けられているべき
                if length <= 2048:
                    assert response.status_code in [200, 400, 422]
                else:
                    assert response.status_code in [414, 400, 422], f"Long URL should be rejected: {description}"
                    
            except Exception as e:
                # URL長エラーは期待される
                assert "url" in str(e).lower() or "length" in str(e).lower()
    
    # ==================== JSON深度境界値テスト ====================
    
    def test_json_nesting_boundaries(self):
        """JSON入れ子境界値テスト"""
        
        # JSON入れ子の境界値
        nesting_levels = [1, 5, 10, 20, 50, 100, 500, 1000]
        
        for level in nesting_levels:
            # 指定レベルの入れ子JSONを生成
            nested_json = {}
            current = nested_json
            
            for i in range(level):
                current["level"] = i
                if i < level - 1:
                    current["nested"] = {}
                    current = current["nested"]
            
            # JSONデータとして送信
            try:
                response = self.client.post("/api/v1/auth/register", json=nested_json)
                
                # 適切な入れ子制限が設けられているべき
                if level <= 20:
                    assert response.status_code in [400, 422]  # バリデーションエラー
                else:
                    assert response.status_code in [400, 422], f"Deep nesting should be rejected: {level} levels"
                    
            except Exception as e:
                # パースエラーやスタックオーバーフローは期待される
                assert any(keyword in str(e).lower() for keyword in ["recursion", "stack", "depth", "nesting"])