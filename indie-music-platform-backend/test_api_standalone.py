#!/usr/bin/env python3
"""
APIエンドポイントテスト（サーバー起動前提）
"""
import requests
import json
import time

def test_api_endpoints():
    """各APIエンドポイントのテスト"""
    base_url = "http://127.0.0.1:8001"
    
    print("=== APIエンドポイントテスト ===")
    print(f"テスト対象: {base_url}")
    print()
    
    # テスト用エンドポイント
    test_cases = [
        {
            "name": "ヘルスチェック",
            "method": "GET",
            "url": f"{base_url}/health",
            "expected_status": 200
        },
        {
            "name": "ルートエンドポイント",
            "method": "GET", 
            "url": f"{base_url}/",
            "expected_status": 200
        },
        {
            "name": "APIドキュメント",
            "method": "GET",
            "url": f"{base_url}/docs",
            "expected_status": 200
        },
        {
            "name": "OpenAPI仕様",
            "method": "GET",
            "url": f"{base_url}/openapi.json",
            "expected_status": 200
        },
        {
            "name": "直接テストエンドポイント",
            "method": "GET",
            "url": f"{base_url}/direct-test",
            "expected_status": 200
        }
    ]
    
    # CORS テスト用ヘッダー
    cors_headers = {
        'Origin': 'http://localhost:5173',
        'Content-Type': 'application/json'
    }
    
    results = []
    
    for test_case in test_cases:
        print(f"テスト: {test_case['name']}")
        
        try:
            # 通常のリクエスト
            response = requests.get(test_case['url'], timeout=5)
            status_ok = response.status_code == test_case['expected_status']
            
            # CORS確認リクエスト
            cors_response = requests.get(test_case['url'], headers=cors_headers, timeout=5)
            cors_header = cors_response.headers.get('Access-Control-Allow-Origin', '')
            
            result = {
                'name': test_case['name'],
                'status_code': response.status_code,
                'status_ok': status_ok,
                'cors_ok': bool(cors_header),
                'cors_header': cors_header,
                'content_length': len(response.content),
                'success': status_ok
            }
            
            if status_ok:
                print(f"  ✓ ステータス: {response.status_code}")
                if cors_header:
                    print(f"  ✓ CORS: {cors_header}")
                else:
                    print(f"  ⚠️ CORS設定なし")
                
                # レスポンスの一部を表示（JSONの場合）
                try:
                    if 'application/json' in response.headers.get('content-type', ''):
                        data = response.json()
                        print(f"  レスポンス: {json.dumps(data, ensure_ascii=False)[:100]}...")
                except:
                    print(f"  レスポンス長: {len(response.content)} bytes")
            else:
                print(f"  ✗ ステータス: {response.status_code} (期待値: {test_case['expected_status']})")
                
            results.append(result)
            
        except requests.exceptions.ConnectionError:
            print(f"  ✗ 接続エラー: サーバーが起動していない可能性があります")
            results.append({
                'name': test_case['name'],
                'success': False,
                'error': 'connection_error'
            })
        except Exception as e:
            print(f"  ✗ エラー: {e}")
            results.append({
                'name': test_case['name'],
                'success': False,
                'error': str(e)
            })
        
        print()
    
    # 結果サマリー
    successful_tests = [r for r in results if r.get('success', False)]
    total_tests = len(results)
    success_rate = len(successful_tests) / total_tests * 100
    
    print("=" * 50)
    print("📊 テスト結果サマリー")
    print("=" * 50)
    print(f"総テスト数: {total_tests}")
    print(f"成功: {len(successful_tests)}")
    print(f"失敗: {total_tests - len(successful_tests)}")
    print(f"成功率: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 すべてのAPIテストが成功しました！")
        print("バックエンドは正常に動作しています。")
    elif success_rate >= 50:
        print(f"\n⚠️ 一部のAPIテストが失敗しました。")
        print("基本的な機能は動作していますが、確認が必要です。")
    else:
        print(f"\n❌ 多くのAPIテストが失敗しました。")
        print("サーバーが起動していない可能性があります。")
    
    return success_rate >= 50

def main():
    """メイン実行"""
    print("APIテストを開始します...")
    print("注意: このテストを実行する前に、バックエンドサーバーを起動してください。")
    print("起動コマンド: ./.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001")
    print()
    
    # サーバー起動待機
    print("5秒待機してからテストを開始します...")
    time.sleep(5)
    
    success = test_api_endpoints()
    return success

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n次のステップ: フロントエンドとの接続テストを実行してください")
        exit_code = 0
    else:
        print("\n問題を解決してから再実行してください")
        exit_code = 1
