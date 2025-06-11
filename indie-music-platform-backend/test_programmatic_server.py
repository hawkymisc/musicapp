#!/usr/bin/env python3
"""
プログラム内でサーバーを実際に起動するテスト
"""
import sys
import os
import logging
import asyncio
import signal
import time

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("=== プログラム内サーバー起動テスト ===")
    
    # プロジェクトルートをsys.pathに追加
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        # 必要なモジュールをインポート
        import uvicorn
        from app.main import app
        
        logger.info("モジュールインポート成功")
        
        # サーバー設定
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info",
            access_log=True
        )
        
        # サーバーオブジェクト作成
        server = uvicorn.Server(config)
        
        logger.info("サーバーを5秒間起動します...")
        
        # 5秒後に停止するためのシグナルハンドラ
        def stop_server():
            logger.info("5秒経過しました。サーバーを停止します...")
            server.should_exit = True
        
        # 5秒後に停止
        import threading
        timer = threading.Timer(5.0, stop_server)
        timer.start()
        
        # サーバー起動
        logger.info("サーバーを起動中...")
        server.run()
        
        logger.info("サーバーが正常に停止しました")
        return True
        
    except Exception as e:
        logger.error(f"サーバー起動エラー: {e}", exc_info=True)
        return False

async def async_main():
    """非同期版のメイン関数"""
    logger.info("=== 非同期サーバー起動テスト ===")
    
    # プロジェクトルートをsys.pathに追加
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        import uvicorn
        from app.main import app
        
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        
        logger.info("非同期サーバーを3秒間起動します...")
        
        # 3秒後に停止
        async def serve_with_timeout():
            task = asyncio.create_task(server.serve())
            await asyncio.sleep(3)
            server.should_exit = True
            await task
        
        await serve_with_timeout()
        logger.info("非同期サーバーが正常に停止しました")
        return True
        
    except Exception as e:
        logger.error(f"非同期サーバー起動エラー: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("同期版テスト:")
    success1 = main()
    
    logger.info("\n非同期版テスト:")
    success2 = asyncio.run(async_main())
    
    if success1 or success2:
        logger.info("✓ 少なくとも1つの方法でサーバー起動に成功しました")
    else:
        logger.error("✗ どちらの方法でもサーバー起動に失敗しました")
        sys.exit(1)
