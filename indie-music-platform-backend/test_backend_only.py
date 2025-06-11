#!/usr/bin/env python3
"""
段階的統合テスト - バックエンドのみ
"""
import sys
import os
import logging
import subprocess
import time
import requests

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_backend_only():
    """バックエンドサーバーのみのテスト"""
    logger.info("=== バックエンド単体テスト ===")
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    python_path = os.path.join(backend_dir, '.venv', 'bin', 'python')
    
    if not os.path.exists(python_path):
        logger.error(f"Python実行ファイルが見つかりません: {python_path}")
        return False
    
    # サーバー起動コマンド
    cmd = [
        python_path,
        '-m', 'uvicorn',
        'app.main:app',
        '--host', '127.0.0.1',
        '--port', '8001',
        '--log-level', 'info'
    ]
    
    logger.info(f"サーバー起動コマンド: {' '.join(cmd)}")
    
    try:
        # サーバーをバックグラウンドで起動
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 起動待機
        logger.info("サーバー起動を待機中...")
        time.sleep(8)
        
        # サーバーが起動しているかチェック
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            logger.error("サーバー起動に失敗しました")
            logger.error(f"出力: {stdout}")
            logger.error(f"エラー: {stderr}")
            return False
        
        logger.info("✓ サーバーが起動しました")
        
        # API接続テスト
        test_urls = [
            ("ヘルスチェック", "http://127.0.0.1:8001/health"),
            ("ルートエンドポイント", "http://127.0.0.1:8001/"),
            ("APIドキュメント", "http://127.0.0.1:8001/docs"),
        ]
        
        for test_name, url in test_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    logger.info(f"✓ {test_name}: {response.status_code}")
                else:
                    logger.warning(f"⚠️ {test_name}: {response.status_code}")
            except Exception as e:
                logger.error(f"✗ {test_name}: 接続エラー - {e}")
        
        # CORS設定テスト
        try:
            headers = {'Origin': 'http://localhost:5173'}
            response = requests.get("http://127.0.0.1:8001/health", headers=headers, timeout=5)
            cors_header = response.headers.get('Access-Control-Allow-Origin', '')
            if cors_header:
                logger.info(f"✓ CORS設定確認: {cors_header}")
            else:
                logger.warning("⚠️ CORS設定が見つかりません")
        except Exception as e:
            logger.error(f"✗ CORS確認エラー: {e}")
        
        logger.info("\\n" + "="*50)
        logger.info("🎉 バックエンドテスト完了！")
        logger.info("サーバーアクセス: http://localhost:8001")
        logger.info("API ドキュメント: http://localhost:8001/docs")
        logger.info("\\n10秒後にサーバーを停止します...")
        logger.info("="*50)
        
        # 10秒待機
        time.sleep(10)
        
        # サーバー停止
        logger.info("サーバーを停止しています...")
        process.terminate()
        process.wait()
        logger.info("✓ サーバーを停止しました")
        
        return True
        
    except Exception as e:
        logger.error(f"テストエラー: {e}")
        try:
            process.terminate()
            process.wait()
        except:
            pass
        return False

if __name__ == "__main__":
    success = test_backend_only()
    if success:
        logger.info("✅ バックエンド単体テスト成功")
    else:
        logger.error("❌ バックエンド単体テスト失敗")
    sys.exit(0 if success else 1)
