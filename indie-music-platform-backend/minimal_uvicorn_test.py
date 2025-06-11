#!/usr/bin/env python3
"""
最小限のUvicorn起動テスト
"""
import sys
import os
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("=== 最小限のUvicorn起動テスト ===")
    
    # プロジェクトルートをsys.pathに追加
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        # FastAPIアプリケーション作成
        from fastapi import FastAPI
        app = FastAPI()
        
        @app.get("/")
        async def root():
            return {"message": "Hello World"}
        
        logger.info("FastAPIアプリケーション作成成功")
        
        # Uvicornインポート
        import uvicorn
        logger.info(f"Uvicorn {uvicorn.__version__} インポート成功")
        
        # サーバー起動（ただし即座に停止）
        logger.info("uvicorn.run() を呼び出します...")
        
        # リストナーなしで設定を確認
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8000,
            log_level="critical"  # ログを最小化
        )
        
        logger.info("Uvicorn設定作成成功")
        
        # サーバーオブジェクト作成
        server = uvicorn.Server(config)
        logger.info("Uvicornサーバーオブジェクト作成成功")
        
        logger.info("テスト完了：基本的な設定は問題ありません")
        return True
        
    except Exception as e:
        logger.error(f"エラー: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✓ 最小限テスト成功")
    else:
        logger.error("✗ 最小限テスト失敗")
        sys.exit(1)
