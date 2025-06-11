#!/usr/bin/env python
"""
テストサーバーAPIテスト

このスクリプトは、テストサーバーのAPIエンドポイントをテストします。
"""
import requests
import sys

def test_api():
    """テストサーバーのAPIをテスト"""
    # テスト対象のエンドポイント
    endpoints = [
        # 基本エンドポイント
        {"url": "http://127.0.0.1:8001/test-simple", "method": "GET", "desc": "シンプルなテストエンドポイント"},
        
        # APIエンドポイント
        {"url": "http://127.0.0.1:8001/api/v1/test", "method": "GET", "desc": "APIテストエンドポイント"},
        {"url": "http://127.0.0.1:8001/api/v1/debug", "method": "GET", "desc": "APIデバッグエンドポイント"},
        {"url": "http://127.0.0.1:8001/api/direct-test", "method": "GET", "desc": "直接テストエンドポイント"},
        
        # 実際のAPIエンドポイント
        {"url": "http://127.0.0.1:8001/api/v1/tracks", "method": "GET", "desc": "楽曲一覧"}
    ]
    
    print("\n=== テストサーバーAPIテスト結果 ===\n")
    print(f"{'エンドポイント':<40} {'ステータス':<10} {'結果'}")
    print("-" * 80)
    
    # 各エンドポイントをテスト
    for endpoint in endpoints:
        url = endpoint["url"]
        method = endpoint["method"]
        desc = endpoint["desc"]
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=3)
            elif method == "POST":
                response = requests.post(url, json={}, timeout=3)
            else:
                continue
            
            status = response.status_code
            if status < 400:
                result = "成功"
                try:
                    data = response.json()
                    result += f" - {str(data)[:50]}"
                except:
                    result += " - レスポンスはJSONではありません"
            else:
                result = "失敗"
                try:
                    data = response.json()
                    result += f" - {str(data)[:50]}"
                except:
                    result += f" - {response.text[:50]}"
        except requests.exceptions.RequestException as e:
            status = "エラー"
            result = str(e)
        
        print(f"{url:<40} {str(status):<10} {result}")
    
    print("\n注意: サーバーが起動していることを確認してください（test_server_simple.py）")

if __name__ == "__main__":
    test_api()
