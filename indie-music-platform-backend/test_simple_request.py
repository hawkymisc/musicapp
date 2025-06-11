#!/usr/bin/env python
"""
シンプルなAPIリクエストテスト
"""
import requests
import json
import subprocess
import time
import sys

def main():
    # サーバーを起動
    process = subprocess.Popen(['python', 'test_startup.py'],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
    
    # サーバーの起動を待つ
    print("サーバーを起動中...")
    time.sleep(3)
    
    try:
        # ルートエンドポイントをテスト
        print("\nルートエンドポイントをテスト:")
        response = requests.get("http://127.0.0.1:8000/")
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス: {response.text}")
        
        # ヘルスチェックエンドポイントをテスト
        print("\nヘルスチェックエンドポイントをテスト:")
        response = requests.get("http://127.0.0.1:8000/health")
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス: {response.text}")
        
        # APIテストエンドポイントをテスト
        print("\nAPIテストエンドポイントをテスト:")
        response = requests.get("http://127.0.0.1:8000/api/v1/test")
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス: {response.text}")
        
        # URLパスを調査（HTMLページを取得）
        print("\nOpenAPI Docsエンドポイントをテスト:")
        response = requests.get("http://127.0.0.1:8000/docs")
        print(f"ステータスコード: {response.status_code}")
        if response.status_code == 200:
            print("Swagger UIが利用可能です")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    finally:
        # サーバーを停止
        print("\nサーバーを停止します...")
        process.terminate()
        process.wait()
        print("サーバーが停止しました")

if __name__ == "__main__":
    main()
