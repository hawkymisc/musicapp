
"""
テスト用のサーバー起動スクリプト
"""
import os
import sys
import logging
import traceback

# テスト環境設定
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'

# ロガーの設定
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import uvicorn
    from app.main import app
    
    print("アプリケーションのインポートに成功しました")
    
    # サーバー起動
    if __name__ == "__main__":
        print("テスト用サーバーを起動します...")
        uvicorn.run(app, host="127.0.0.1", port=8000)
        
except Exception as e:
    print(f"エラーが発生しました: {e}")
    traceback.print_exc()
    sys.exit(1)
