#!/usr/bin/env python3
"""
サーバー動作確認テスト
"""
import sys
import requests
import json
import time

def test_server():
    """サーバー動作テスト"""
    base_url = "http://127.0.0.1:8000"
    
    tests = [
        ("ヘルスチェック", "/health"),
        ("ルートエンドポイント", "/"),
        ("直接テスト", "/direct-test"),
        ("API docs", "/docs")
    ]
    
    print("=== サーバー動作テスト ===")
    
    for test_name, endpoint in tests:
        try:
            print(f"\n{test_name} ({endpoint}) をテスト中...")
            
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            print(f"  ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                if 'application/json' in response.headers.get('Content-Type', ''):
                    data = response.json()
                    print(f"  レスポンス: {json.dumps(data, ensure_ascii=False, indent=2)}")
                else:
                    content = response.text[:200]
                    print(f"  レスポンス: {content}...")
                print(f"  ✓ {test_name} 成功")
            else:
                print(f"  ✗ {test_name} 失敗 (ステータス: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"  ✗ {test_name} 失敗: サーバーに接続できません")
        except requests.exceptions.Timeout:
            print(f"  ✗ {test_name} 失敗: タイムアウト")
        except Exception as e:
            print(f"  ✗ {test_name} 失敗: {e}")

if __name__ == "__main__":
    # サーバーの起動を少し待つ
    print("サーバーの起動を待っています...")
    time.sleep(2)
    
    test_server()
