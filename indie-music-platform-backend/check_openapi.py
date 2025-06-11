#!/usr/bin/env python
"""
OpenAPIエンドポイント確認スクリプト

FastAPIアプリケーションのOpenAPIドキュメントを取得し、登録されているエンドポイントを解析します。
"""
import requests
import json
import subprocess
import time
import sys

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

def get_openapi_schema():
    """OpenAPIスキーマを取得"""
    try:
        response = requests.get("http://127.0.0.1:8000/openapi.json")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"OpenAPIスキーマの取得に失敗しました。ステータスコード: {response.status_code}")
            return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def analyze_paths(schema):
    """APIパスを解析して表示"""
    if not schema or 'paths' not in schema:
        print("有効なOpenAPIスキーマが取得できませんでした")
        return
    
    print("\n登録されているエンドポイント:")
    
    # パスごとにメソッドと説明を表示
    paths = schema['paths']
    for path, methods in sorted(paths.items()):
        print(f"\n- {path}")
        for method, details in methods.items():
            summary = details.get('summary', 'No description')
            print(f"  - {method.upper()}: {summary}")
    
    print("\n合計: {0}個のエンドポイント".format(len(paths)))

def main():
    """メイン処理"""
    process = start_server()
    
    try:
        # OpenAPIスキーマを取得して解析
        schema = get_openapi_schema()
        if schema:
            analyze_paths(schema)
        
        # 試験的にクエリを送信
        print("\nいくつかのエンドポイントをテスト:")
        
        # テストエンドポイント
        print("\n1. テストエンドポイント:")
        response = requests.get("http://127.0.0.1:8000/api/v1/test")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text if response.status_code < 400 else 'Error'}")
        
        # 楽曲一覧エンドポイント
        print("\n2. 楽曲一覧エンドポイント:")
        response = requests.get("http://127.0.0.1:8000/api/v1/tracks")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200] + '...' if response.status_code < 400 and len(response.text) > 200 else response.text if response.status_code < 400 else 'Error'}")
        
    finally:
        stop_server(process)

if __name__ == "__main__":
    main()
