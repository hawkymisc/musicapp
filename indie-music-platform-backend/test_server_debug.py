
"""
詳細なデバッグ情報つきサーバー起動スクリプト
"""
import os
import sys
import logging
import traceback

# テスト環境設定
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['FIREBASE_CREDENTIALS_PATH'] = './tests/mocks/firebase_credentials.json'

# ロガーの設定
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Firebase関連モジュールのモック化
print("Firebaseモジュールをモック化します...")
sys.modules['firebase_admin'] = type('MockFirebase', (), {'initialize_app': lambda x: None})
sys.modules['firebase_admin.auth'] = type('MockFirebaseAuth', (), {
    'verify_id_token': lambda token, **kwargs: {'uid': 'test_uid'} if token else None
})
sys.modules['firebase_admin.credentials'] = type('MockFirebaseCredentials', (), {
    'Certificate': lambda path: None
})

try:
    print("Step 1: 基本モジュールのインポート")
    import fastapi
    import uvicorn
    import sqlalchemy
    print("基本モジュールのインポート成功")
    
    print("Step 2: app.db.session のインポート")
    from app.db.session import get_db, create_tables
    print("app.db.session のインポート成功")
    
    print("Step 3: app.core.config のインポート")  
    from app.core.config import settings
    print(f"設定インポート成功: DATABASE_URL={settings.DATABASE_URL}")
    
    print("Step 4: app.models のインポート")
    from app.models.user import User, UserRole
    from app.models.track import Track
    print("app.models のインポート成功")
    
    print("Step 5: app.core.security のインポート")
    from app.core.security import get_current_user, get_current_active_user
    print("app.core.security のインポート成功")
    
    print("Step 6: app.api.router のインポート")
    from app.api.router import api_router
    print("app.api.router のインポート成功")
    
    print("Step 7: app.main のインポート")
    from app.main import app
    print("app.main のインポート成功")
    
    # データベース作成
    print("データベーステーブルを作成しています...")
    create_tables()
    print("データベーステーブルの作成が完了しました")
    
    # サーバー起動
    print("サーバーを起動します...")
    if __name__ == "__main__":
        uvicorn.run(app, host="127.0.0.1", port=8000)
    
except Exception as e:
    print(f"エラーが発生しました: {e}")
    traceback.print_exc()
    sys.exit(1)
