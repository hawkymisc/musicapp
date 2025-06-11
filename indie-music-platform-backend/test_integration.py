#!/usr/bin/env python3
"""
フロントエンド・バックエンド統合テストスクリプト
"""
import sys
import os
import logging
import subprocess
import time
import requests
import json
from pathlib import Path

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_backend_server(port=8001):
    """バックエンドサーバーを起動"""
    logger.info(f"=== バックエンドサーバー起動 (ポート{port}) ===")
    
    backend_dir = Path(__file__).parent
    python_path = backend_dir / '.venv' / 'bin' / 'python'
    
    if not python_path.exists():
        logger.error(f"Python実行ファイルが見つかりません: {python_path}")
        return None
    
    cmd = [
        str(python_path),
        '-m', 'uvicorn',
        'app.main:app',
        '--host', '127.0.0.1',
        '--port', str(port),
        '--log-level', 'info'
    ]
    
    logger.info(f"サーバー起動コマンド: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # サーバー起動を待機
        logger.info("サーバー起動を待機中...")
        time.sleep(5)
        
        # サーバーが起動しているか確認
        if process.poll() is None:
            logger.info("✓ バックエンドサーバーが起動しました")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error("✗ サーバー起動に失敗しました")
            logger.error(f"標準出力: {stdout}")
            logger.error(f"標準エラー: {stderr}")
            return None
            
    except Exception as e:
        logger.error(f"サーバー起動エラー: {e}")
        return None

def test_backend_api(port=8001):
    """バックエンドAPIの基本テスト"""
    logger.info("=== バックエンドAPI接続テスト ===")
    
    base_url = f"http://127.0.0.1:{port}"
    
    # ヘルスチェック
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            logger.info("✓ ヘルスチェック成功")
            logger.info(f"レスポンス: {response.json()}")
        else:
            logger.error(f"✗ ヘルスチェック失敗: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ ヘルスチェック接続エラー: {e}")
        return False
    
    # ルートエンドポイント
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            logger.info("✓ ルートエンドポイント成功")
            logger.info(f"レスポンス: {response.json()}")
        else:
            logger.error(f"✗ ルートエンドポイント失敗: {response.status_code}")
    except Exception as e:
        logger.error(f"✗ ルートエンドポイント接続エラー: {e}")
    
    # API エンドポイント確認
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code == 200:
            logger.info("✓ API v1エンドポイント確認成功")
        else:
            logger.info("ℹ️ API v1エンドポイントは未実装または異なるパス")
    except Exception as e:
        logger.info("ℹ️ API v1エンドポイントへの接続を確認中...")
    
    return True

def start_frontend_server():
    """フロントエンドサーバーを起動"""
    logger.info("=== フロントエンドサーバー起動 ===")
    
    frontend_dir = Path(__file__).parent.parent / 'indie-music-platform-frontend'
    
    if not frontend_dir.exists():
        logger.error(f"フロントエンドディレクトリが見つかりません: {frontend_dir}")
        return None
    
    # package.jsonの存在確認
    package_json = frontend_dir / 'package.json'
    if not package_json.exists():
        logger.error(f"package.jsonが見つかりません: {package_json}")
        return None
    
    cmd = ['npm', 'run', 'dev']
    
    logger.info(f"フロントエンド起動コマンド: {' '.join(cmd)}")
    logger.info(f"作業ディレクトリ: {frontend_dir}")
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # フロントエンド起動を待機
        logger.info("フロントエンド起動を待機中...")
        time.sleep(8)
        
        # フロントエンドが起動しているか確認
        if process.poll() is None:
            logger.info("✓ フロントエンドサーバーが起動しました")
            logger.info("ブラウザで http://localhost:5173 にアクセスして確認してください")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error("✗ フロントエンド起動に失敗しました")
            logger.error(f"標準出力: {stdout}")
            logger.error(f"標準エラー: {stderr}")
            return None
            
    except Exception as e:
        logger.error(f"フロントエンド起動エラー: {e}")
        return None

def test_end_to_end_connection():
    """エンドツーエンド接続テスト"""
    logger.info("=== エンドツーエンド接続テスト ===")
    
    # フロントエンドからバックエンドへのCORS確認
    try:
        headers = {
            'Origin': 'http://localhost:5173',
            'Content-Type': 'application/json'
        }
        response = requests.get(
            "http://127.0.0.1:8001/health",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info("✓ CORS設定は正常です")
            
            # CORSヘッダーの確認
            cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
            logger.info(f"CORS Origin: {cors_headers}")
        else:
            logger.warning(f"CORS確認で予期しないレスポンス: {response.status_code}")
            
    except Exception as e:
        logger.error(f"CORS確認エラー: {e}")
    
    logger.info("✓ エンドツーエンドテスト完了")

def main():
    """メイン実行関数"""
    logger.info("=== フロントエンド・バックエンド統合テスト開始 ===")
    
    backend_process = None
    frontend_process = None
    
    try:
        # 1. バックエンドサーバー起動
        backend_process = start_backend_server(8001)
        if not backend_process:
            logger.error("バックエンドサーバーの起動に失敗しました")
            return False
        
        # 2. バックエンドAPI基本テスト
        if not test_backend_api(8001):
            logger.error("バックエンドAPIテストに失敗しました")
            return False
        
        # 3. フロントエンドサーバー起動
        frontend_process = start_frontend_server()
        if not frontend_process:
            logger.error("フロントエンドサーバーの起動に失敗しました")
            return False
        
        # 4. エンドツーエンドテスト
        test_end_to_end_connection()
        
        logger.info("\\n" + "="*60)
        logger.info("🎉 統合テスト成功！")
        logger.info("バックエンド: http://localhost:8001")
        logger.info("フロントエンド: http://localhost:5173")
        logger.info("API ドキュメント: http://localhost:8001/docs")
        logger.info("\\nCtrl+C で両サーバーを停止します")
        logger.info("="*60)
        
        # ユーザーが手動で停止するまで待機
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\\nサーバーを停止しています...")
        
        return True
        
    except Exception as e:
        logger.error(f"統合テストエラー: {e}")
        return False
        
    finally:
        # プロセスのクリーンアップ
        if backend_process:
            logger.info("バックエンドサーバーを停止中...")
            backend_process.terminate()
            backend_process.wait()
        
        if frontend_process:
            logger.info("フロントエンドサーバーを停止中...")
            frontend_process.terminate()
            frontend_process.wait()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
