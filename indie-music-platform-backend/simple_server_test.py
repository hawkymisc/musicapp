#!/usr/bin/env python3
"""
シンプルなサーバー起動テスト
"""
import sys
import os
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """メイン実行関数"""
    logger.info("=== シンプルなサーバー起動テスト ===")
    
    # プロジェクトルートをsys.pathに追加
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        # アプリケーションをインポート
        logger.info("アプリケーションをインポートしています...")
        from app.main import app
        logger.info("✓ アプリケーション インポート成功")
        
        # Uvicornでサーバーを起動
        logger.info("Uvicornサーバーを起動しています...")
        logger.info("サーバーを停止するには Ctrl+C を押してください")
        
        import uvicorn
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("サーバーが正常に停止されました")
    except Exception as e:
        logger.error(f"サーバー起動エラー: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
