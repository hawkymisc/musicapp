#!/usr/bin/env python
"""
シンプルなAPIテスト用サーバー

モジュールキャッシュを無効化し、APIルーターの問題を解決するための
シンプルな起動スクリプトです。
"""
import os
import sys
import uvicorn
import importlib
import logging
from fastapi import FastAPI

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_server_simple.log')
    ]
)
logger = logging.getLogger("test_server_simple")

# テスト環境設定
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'

# テスト用アプリケーション
app = FastAPI()

# テストエンドポイント
@app.get("/test-simple")
def test_simple():
    """シンプルなテストエンドポイント"""
    return {"message": "シンプルなテストエンドポイントが動作しています"}

# APIルーターをインポートして追加
try:
    # モジュールキャッシュがある場合はリロード
    if 'app.api.router' in sys.modules:
        importlib.reload(sys.modules['app.api.router'])
    else:
        from app.api import router
        
    # ルーターを取得
    api_router = router.api_router
    
    # ルーターの情報を出力
    logger.info(f"APIルーターの状態: {api_router}")
    logger.info(f"登録されているルート数: {len(api_router.routes)}")
    
    # ルート情報を詳細に出力
    for route in api_router.routes:
        path = getattr(route, "path", "unknown")
        methods = getattr(route, "methods", ["GET"])
        endpoint = getattr(route, "endpoint", None)
        logger.info(f"ルート: {path}, メソッド: {methods}, エンドポイント: {endpoint}")
    
    # ルーターをアプリケーションにマウント
    app.include_router(api_router, prefix="/api")
    logger.info("APIルーターをアプリケーションにマウントしました")
except Exception as e:
    logger.error(f"APIルーターのインポートに失敗しました: {e}", exc_info=True)

# サーバー起動
if __name__ == "__main__":
    logger.info("テストサーバーを起動します...")
    
    print("💻 テストサーバーが http://127.0.0.1:8001 で起動しました")
    print("Ctrl+Cで終了します")
    
    # 通常とは異なるポートを使用（8000ではなく8001）
    uvicorn.run(app, host="127.0.0.1", port=8001)
