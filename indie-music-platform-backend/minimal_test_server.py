
"""
最小限のFastAPIサーバー
"""
import os
import sys
import logging
import traceback

# ロガーの設定
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI
    import uvicorn
    
    # 最小限のFastAPIアプリケーション
    app = FastAPI(title="最小限のテストサーバー")
    
    @app.get("/")
    async def root():
        return {"message": "Hello, World!"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    # サーバー起動
    if __name__ == "__main__":
        print("最小限のサーバーを起動します...")
        uvicorn.run(app, host="127.0.0.1", port=8000)
        
except Exception as e:
    print(f"エラーが発生しました: {e}")
    traceback.print_exc()
    sys.exit(1)
