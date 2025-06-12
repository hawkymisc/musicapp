"""
簡易APIテスト - 動作確認用
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_docs():
    """API ドキュメントアクセステスト"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_root_endpoint():
    """ルートエンドポイントテスト"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    # 元のレスポンス構造に合わせて修正
    assert data["name"] == "インディーズミュージックアプリAPI"

def test_openapi_spec():
    """OpenAPI仕様書テスト"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi_spec = response.json()
    assert "openapi" in openapi_spec
    assert "info" in openapi_spec
    assert "paths" in openapi_spec

if __name__ == "__main__":
    pytest.main([__file__, "-v"])