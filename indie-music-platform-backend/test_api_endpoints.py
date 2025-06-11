#!/usr/bin/env python
"""
インディーズミュージックプラットフォーム APIエンドポイントテスト

このスクリプトは、バックエンドAPIの各エンドポイントを呼び出し、
正常に動作するかどうかを確認します。
"""
import requests
import json
import sys
import time
import subprocess
import os
import signal
from datetime import datetime

# テスト結果の出力ファイル
OUTPUT_FILE = "api_test_results.json"
# APIのベースURL
BASE_URL = "http://127.0.0.1:8000/api"

def start_server():
    """バックエンドサーバーを起動"""
    print("バックエンドサーバーを起動しています...")
    process = subprocess.Popen(['python', 'test_startup.py'],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
    # サーバーの起動を待つ
    time.sleep(3)
    print("サーバーが起動しました")
    return process

def stop_server(process):
    """バックエンドサーバーを停止"""
    print("サーバーを停止しています...")
    process.terminate()
    process.wait()
    print("サーバーが停止しました")
    
def make_request(endpoint, method="GET", data=None, headers=None):
    """指定されたエンドポイントにリクエストを送信"""
    url = f"{BASE_URL}{endpoint}"
    print(f"{method} {url}")
    
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)
    
    try:
        if method == "GET":
            response = requests.get(url, headers=default_headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers=default_headers, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=default_headers, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=default_headers, timeout=5)
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}
        
        return {
            "status": "success" if response.status_code < 400 else "error",
            "status_code": response.status_code,
            "response": response.json() if response.text else None
        }
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

def test_basic_endpoints():
    """基本的なエンドポイントをテスト"""
    results = {}
    
    # ヘルスチェック
    results["health"] = make_request("/health")
    
    # ルートエンドポイント
    results["root"] = make_request("")
    
    return results

def test_v1_endpoints():
    """v1 APIエンドポイントをテスト"""
    results = {}
    
    # テストエンドポイント
    results["test"] = make_request("/v1/test")
    
    # 楽曲一覧
    results["tracks"] = make_request("/v1/tracks")
    
    # ユーザー関連（認証が必要なためエラーになることを確認）
    results["users_me"] = make_request("/v1/users/me")
    
    # 認証テスト
    auth_data = {"email": "test@example.com", "password": "password123"}
    results["auth_login"] = make_request("/v1/auth/login", method="POST", data=auth_data)
    
    # テスト用のトークンを取得できればさらにテスト
    if results["auth_login"]["status"] == "success":
        token = results["auth_login"]["response"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 認証済みユーザー情報取得
        results["auth_me"] = make_request("/v1/auth/me", headers=headers)
    
    return results

def run_tests():
    """すべてのテストを実行"""
    process = start_server()
    
    try:
        results = {
            "timestamp": datetime.now().isoformat(),
            "basic_endpoints": test_basic_endpoints(),
            "v1_endpoints": test_v1_endpoints()
        }
        
        # 結果の出力
        print("\n----- テスト結果 -----")
        for category, category_results in results.items():
            if category == "timestamp":
                continue
                
            print(f"\n## {category}")
            for endpoint, result in category_results.items():
                status = result["status"]
                status_code = result.get("status_code", "N/A")
                print(f"- {endpoint}: {status} ({status_code})")
        
        # 結果をファイルに保存
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n詳細な結果は {OUTPUT_FILE} に保存されました")
        
    finally:
        stop_server(process)

if __name__ == "__main__":
    run_tests()
