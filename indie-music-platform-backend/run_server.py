"""
デバッグ用のサーバー起動スクリプト
"""
import uvicorn
import logging
import traceback
import sys

# ロガー設定
logging.basicConfig(level=logging.DEBUG)

try:
    # アプリケーションの初期化をトレース
    from app.main import app
    print("アプリケーションがロードされました")
    
    # サーバー起動
    if __name__ == "__main__":
        print("開発サーバーを起動しています...")
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, log_level="debug")
except Exception as e:
    print(f"エラーが発生しました: {e}")
    traceback.print_exc()
    sys.exit(1)
