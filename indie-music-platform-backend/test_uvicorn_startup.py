#!/usr/bin/env python3
"""
Uvicornサーバー起動テストスクリプト
"""
import sys
import os
import logging
import uvicorn
import signal
import asyncio
from multiprocessing import Process
import time

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_uvicorn_import():
    """Uvicornインポートテスト"""
    logger.info("=== Uvicorn インポートテスト ===")
    try:
        import uvicorn
        logger.info(f"✓ Uvicorn バージョン: {uvicorn.__version__}")
        return True
    except Exception as e:
        logger.error(f"✗ Uvicorn インポートエラー: {e}")
        return False

def test_app_import():
    """アプリケーションインポートテスト"""
    logger.info("=== アプリケーション インポートテスト ===")
    try:
        from app.main import app
        logger.info("✓ アプリケーション インポート成功")
        return app
    except Exception as e:
        logger.error(f"✗ アプリケーション インポートエラー: {e}")
        return None

def test_uvicorn_config():
    """Uvicorn設定テスト"""
    logger.info("=== Uvicorn 設定テスト ===")
    try:
        config = uvicorn.Config(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
        logger.info("✓ Uvicorn設定作成成功")
        return config
    except Exception as e:
        logger.error(f"✗ Uvicorn設定作成エラー: {e}")
        return None

def test_simple_uvicorn_run():
    """シンプルなuvicorn.run()テスト"""
    logger.info("=== シンプルなuvicorn.run()テスト ===")
    
    try:
        # プロジェクトルートをsys.pathに追加
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # シンプルなFastAPIアプリ作成
        from fastapi import FastAPI
        simple_app = FastAPI()
        
        @simple_app.get("/")
        async def root():
            return {"message": "test"}
        
        logger.info("シンプルなアプリでuvicorn.run()を5秒間テストします...")
        
        def run_simple():
            try:
                uvicorn.run(
                    simple_app,
                    host="127.0.0.1",
                    port=8001,
                    log_level="error",
                    access_log=False
                )
            except Exception as e:
                logger.error(f"シンプルなuvicorn.run()エラー: {e}")
        
        # プロセスを作成
        server_process = Process(target=run_simple)
        server_process.start()
        
        # 5秒待機
        time.sleep(5)
        
        # プロセスを終了
        if server_process.is_alive():
            server_process.terminate()
            server_process.join(timeout=3)
            if server_process.is_alive():
                server_process.kill()
        
        logger.info("✓ シンプルなuvicorn.run()テスト完了")
        return True
        
    except Exception as e:
        logger.error(f"✗ シンプルなuvicorn.run()テストエラー: {e}", exc_info=True)
        return False

def test_main_app_uvicorn():
    """メインアプリでのuvicorn.run()テスト"""
    logger.info("=== メインアプリでのuvicorn.run()テスト ===")
    
    try:
        # プロジェクトルートをsys.pathに追加
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        logger.info("メインアプリでuvicorn.run()を5秒間テストします...")
        
        def run_main_app():
            try:
                uvicorn.run(
                    "app.main:app",
                    host="127.0.0.1",
                    port=8002,
                    reload=False,
                    log_level="error",
                    access_log=False
                )
            except Exception as e:
                logger.error(f"メインアプリuvicorn.run()エラー: {e}")
        
        # プロセスを作成
        server_process = Process(target=run_main_app)
        server_process.start()
        
        # 5秒待機
        time.sleep(5)
        
        # プロセスを終了
        if server_process.is_alive():
            server_process.terminate()
            server_process.join(timeout=3)
            if server_process.is_alive():
                server_process.kill()
        
        logger.info("✓ メインアプリuvicorn.run()テスト完了")
        return True
        
    except Exception as e:
        logger.error(f"✗ メインアプリuvicorn.run()テストエラー: {e}", exc_info=True)
        return False

def main():
    """メイン実行関数"""
    logger.info("=== Uvicornサーバー起動テスト開始 ===")
    logger.info(f"Python バージョン: {sys.version}")
    logger.info(f"作業ディレクトリ: {os.getcwd()}")
    
    # 段階的なテスト実行
    tests = [
        ("Uvicornインポート", test_uvicorn_import),
        ("アプリケーションインポート", test_app_import),
        ("Uvicorn設定", test_uvicorn_config),
        ("シンプルなuvicorn.run()", test_simple_uvicorn_run),
        ("メインアプリuvicorn.run()", test_main_app_uvicorn),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name}のテスト ---")
        try:
            if test_name in ["アプリケーションインポート", "Uvicorn設定"]:
                result = test_func()
                results[test_name] = result is not None
            else:
                result = test_func()
                results[test_name] = result
                
            if not results[test_name]:
                logger.error(f"{test_name}のテストで問題が発見されました。")
        except Exception as e:
            logger.error(f"{test_name}のテスト中に予期しないエラー: {e}", exc_info=True)
            results[test_name] = False
    
    logger.info("\n=== テスト結果サマリー ===")
    for test_name, result in results.items():
        status = "✓ 成功" if result else "✗ 失敗"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        logger.info("すべてのテストが成功しました！")
    else:
        logger.error("一部のテストで問題が発見されました。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("Uvicornテスト完了: すべて正常")
    else:
        logger.error("Uvicornテスト完了: 問題が発見されました")
        sys.exit(1)
