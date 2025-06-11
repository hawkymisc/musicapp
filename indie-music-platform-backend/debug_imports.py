"""
インポートのデバッグ
"""
import sys
import traceback

try:
    print("Step 1: 基本インポート")
    import fastapi
    import uvicorn
    import sqlalchemy
    import pydantic
    print("基本インポート成功")
    
    print("Step 2: 設定インポート")
    from app.core.config import settings
    print(f"設定インポート成功: DATABASE_URL={settings.DATABASE_URL}")
    
    print("Step 3: データベース接続設定")
    from app.db.session import get_db, create_tables
    print("データベース接続設定インポート成功")
    
    print("Step 4: モデルインポート")
    from app.models.user import User, UserRole
    from app.models.track import Track
    print("モデルインポート成功")
    
    print("Step 5: アプリケーションインポート")
    from app.main import app
    print("アプリケーションインポート成功")
    
    print("すべてのインポートが成功しました！")
except Exception as e:
    print(f"エラーが発生しました: {e}")
    traceback.print_exc()
