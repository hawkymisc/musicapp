#!/usr/bin/env python3
"""
実際のアプリケーションでのサーバー起動テスト
"""
import sys
import os
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("=== 実際のアプリケーションサーバー起動テスト ===")
    
    # プロジェクトルートをsys.pathに追加
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        # メインアプリケーションインポート
        logger.info("メインアプリケーションをインポートします...")
        from app.main import app
        logger.info("✓ メインアプリケーションインポート成功")
        
        # Uvicornインポート
        import uvicorn
        logger.info(f"✓ Uvicorn {uvicorn.__version__} インポート成功")
        
        # サーバー設定
        logger.info("サーバー設定を作成します...")
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
        logger.info("✓ サーバー設定作成成功")
        
        # サーバーオブジェクト作成
        logger.info("サーバーオブジェクトを作成します...")
        server = uvicorn.Server(config)
        logger.info("✓ サーバーオブジェクト作成成功")
        
        logger.info("準備完了: サーバーを手動で起動する準備ができました")
        logger.info("実際の起動は手動で行ってください: uvicorn app.main:app --host 127.0.0.1 --port 8000")
        
        return True
        
    except Exception as e:
        logger.error(f"エラー: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✓ 実際のアプリケーションテスト成功")
        logger.info("次のステップ: 手動でサーバーを起動してください")
    else:
        logger.error("✗ 実際のアプリケーションテスト失敗")
        sys.exit(1)
