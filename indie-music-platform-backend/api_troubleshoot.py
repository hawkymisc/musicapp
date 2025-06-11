#!/usr/bin/env python
"""
インディーズミュージックプラットフォーム APIトラブルシューティング

このスクリプトは、APIエンドポイントの問題を診断するためのものです。
"""
import requests
import subprocess
import time
import sys

def test_endpoints():
    """各種エンドポイントをテスト"""
    # テスト対象のエンドポイント
    endpoints = [
        # 既知の動作しているエンドポイント
        {"url": "http://127.0.0.1:8000/", "method": "GET", "desc": "ルートエンドポイント"},
        {"url": "http://127.0.0.1:8000/health", "method": "GET", "desc": "ヘルスチェック"},
        
        # 直接追加したテストエンドポイント
        {"url": "http://127.0.0.1:8000/direct-test", "method": "GET", "desc": "直接のテストエンドポイント"},
        
        # APIルーター経由のエンドポイント（問題のあるもの）
        {"url": "http://127.0.0.1:8000/api/v1/test", "method": "GET", "desc": "APIテストエンドポイント"},
        
        # 異なるパスパターン（トラブルシューティング用）
        {"url": "http://127.0.0.1:8000/api/api/v1/test", "method": "GET", "desc": "二重プレフィックステスト"},
        {"url": "http://127.0.0.1:8000/test", "method": "GET", "desc": "プレフィックスなしテスト"},
        {"url": "http://127.0.0.1:8000/v1/test", "method": "GET", "desc": "半分のプレフィックステスト"},
        
        # 実際のAPIエンドポイント
        {"url": "http://127.0.0.1:8000/api/v1/tracks", "method": "GET", "desc": "楽曲一覧"},
        {"url": "http://127.0.0.1:8000/api/v1/auth/me", "method": "GET", "desc": "現在のユーザー"}
    ]
    
    results = {}
    
    # サーバー起動
    print("バックエンドサーバーを起動しています...")
    process = subprocess.Popen(['python', 'test_startup.py'],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
    
    # サーバーの起動を待つ
    time.sleep(3)
    print("サーバーが起動しました")
    
    try:
        print("\n=== エンドポイントテスト結果 ===\n")
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
            results[url] = {"status": status, "result": result, "desc": desc}
        
        # 分析
        print("\n=== 問題分析 ===\n")
        
        # ルートとヘルスチェックの状態を確認
        if results.get("http://127.0.0.1:8000/", {}).get("status", 500) < 400 and \
           results.get("http://127.0.0.1:8000/health", {}).get("status", 500) < 400:
            print("✅ ベースのエンドポイントは正常に動作しています")
        else:
            print("❌ ベースのエンドポイントに問題があります - サーバー自体が正しく動作していない可能性があります")
        
        # 直接追加したテストエンドポイントの確認
        if results.get("http://127.0.0.1:8000/direct-test", {}).get("status", 500) < 400:
            print("✅ 直接追加したテストエンドポイントは正常に動作しています")
        else:
            print("❌ 直接追加したテストエンドポイントに問題があります - app.main.pyの修正が反映されていない可能性があります")
        
        # APIテストエンドポイントの確認
        api_test_status = results.get("http://127.0.0.1:8000/api/v1/test", {}).get("status", 500)
        if api_test_status < 400:
            print("✅ APIテストエンドポイントは正常に動作しています")
        else:
            print("❌ APIテストエンドポイントに問題があります（ステータス: {}）".format(api_test_status))
            
            # パスが間違っている可能性を確認
            alternative_paths = [
                "http://127.0.0.1:8000/api/api/v1/test",
                "http://127.0.0.1:8000/test",
                "http://127.0.0.1:8000/v1/test"
            ]
            correct_path = None
            for path in alternative_paths:
                if results.get(path, {}).get("status", 500) < 400:
                    correct_path = path
                    break
            
            if correct_path:
                print(f"✅ 代替パス {correct_path} は動作しています - ルーターのプレフィックス設定を確認してください")
            else:
                print("❌ すべての代替パスも失敗しています - APIルーターの実装に問題がある可能性があります")
        
        # 実際のAPIエンドポイントの確認
        tracks_status = results.get("http://127.0.0.1:8000/api/v1/tracks", {}).get("status", 500)
        if tracks_status < 400:
            print("✅ 楽曲一覧エンドポイントは正常に動作しています")
        else:
            print("❌ 楽曲一覧エンドポイントに問題があります（ステータス: {}）".format(tracks_status))
            print("  - データベース接続や楽曲サービスの実装を確認してください")
        
        # 認証が必要なエンドポイントの確認
        auth_status = results.get("http://127.0.0.1:8000/api/v1/auth/me", {}).get("status", 500)
        if auth_status == 401:
            print("⚠️ 認証エンドポイントは401エラーを返しています - 認証トークンがないため、これは正常です")
        elif auth_status < 400:
            print("⚠️ 認証エンドポイントは正常に動作していますが、認証なしでアクセスできています - セキュリティ設定を確認してください")
        else:
            print("❌ 認証エンドポイントに問題があります（ステータス: {}）".format(auth_status))
        
        # 次のステップの提案
        print("\n=== 提案される次のステップ ===\n")
        
        if api_test_status >= 400:
            print("1. APIルーターの設定を確認してください")
            print("   - app/api/router.pyのプレフィックス設定")
            print("   - app/main.pyでのルーターマウント方法")
        
        if tracks_status >= 400 and tracks_status != 404:
            print("2. サーバーのログをチェックして、楽曲エンドポイントの具体的なエラーを特定してください")
            print("   - 依存関係や初期化の問題が考えられます")
        
        if auth_status >= 400 and auth_status != 401:
            print("3. 認証関連のコードを確認してください")
            print("   - Firebase設定やモックの問題が考えられます")
        
    finally:
        # サーバーを停止
        print("\nサーバーを停止しています...")
        process.terminate()
        process.wait()
        print("サーバーが停止しました")
        
if __name__ == "__main__":
    test_endpoints()
