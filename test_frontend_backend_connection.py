#!/usr/bin/env python3
"""
フロントエンドとバックエンドの接続テスト
"""
import requests
import json
import time

def test_frontend_backend_connection():
    """フロントエンドとバックエンドの接続テスト"""
    
    # テスト対象のURL
    backend_url = "http://127.0.0.1:8000"
    frontend_url = "http://localhost:5173"  # Viteの標準ポート
    
    print("=== フロントエンドとバックエンドの接続テスト ===\n")
    
    # 1. バックエンドのヘルスチェック
    print("1. バックエンドのヘルスチェック")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ バックエンド: 正常動作")
            print(f"  レスポンス: {response.json()}")
        else:
            print(f"  ❌ バックエンド: エラー (ステータス: {response.status_code})")
            return False
    except Exception as e:
        print(f"  ❌ バックエンド: 接続失敗 ({e})")
        return False
    
    # 2. フロントエンドのヘルスチェック
    print("\n2. フロントエンドのヘルスチェック")
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("  ✅ フロントエンド: 正常動作")
        else:
            print(f"  ❌ フロントエンド: エラー (ステータス: {response.status_code})")
    except Exception as e:
        print(f"  ❌ フロントエンド: 接続失敗 ({e})")
        print("  ⚠️  フロントエンドが起動していない可能性があります")
    
    # 3. バックエンドAPIエンドポイントのテスト
    print("\n3. バックエンドAPIエンドポイントのテスト")
    
    api_tests = [
        ("ルートエンドポイント", "/"),
        ("ヘルスチェック", "/health"),
        ("直接テスト", "/direct-test"),
        ("楽曲一覧", "/api/v1/tracks/"),
        ("アーティスト取得", "/api/v1/artists/featured"),
    ]
    
    for test_name, endpoint in api_tests:
        try:
            print(f"  テスト中: {test_name} ({endpoint})")
            response = requests.get(f"{backend_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"    ✅ {test_name}: 成功")
                if endpoint == "/health":
                    print(f"    データ: {response.json()}")
            elif response.status_code == 404:
                print(f"    ⚠️  {test_name}: エンドポイントが見つかりません (404)")
            else:
                print(f"    ❌ {test_name}: ステータス {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ {test_name}: エラー ({e})")
    
    # 4. CORS設定のテスト
    print("\n4. CORS設定のテスト")
    try:
        headers = {
            'Origin': frontend_url,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{backend_url}/health", headers=headers, timeout=5)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        if cors_headers['Access-Control-Allow-Origin']:
            print("  ✅ CORS設定: 正常に設定されています")
            print(f"    許可されたオリジン: {cors_headers['Access-Control-Allow-Origin']}")
        else:
            print("  ⚠️  CORS設定: ヘッダーが見つかりません")
            
    except Exception as e:
        print(f"  ❌ CORS設定: テスト失敗 ({e})")
    
    print("\n=== 接続テスト完了 ===")
    return True

if __name__ == "__main__":
    print("サーバーの起動を確認中...")
    time.sleep(2)
    test_frontend_backend_connection()
