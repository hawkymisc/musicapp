def test_simple():
    """シンプルなテスト"""
    import sys
    from unittest.mock import patch, MagicMock
    
    # Firebase初期化のモック化
    sys.modules['firebase_admin'] = MagicMock()
    sys.modules['firebase_admin.auth'] = MagicMock()
    sys.modules['firebase_admin.credentials'] = MagicMock()
    
    # アプリケーションのインポート
    from app.main import app
    from fastapi.testclient import TestClient
    
    # テストクライアントの作成
    client = TestClient(app)
    
    # ヘルスチェックエンドポイントへのリクエスト
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
