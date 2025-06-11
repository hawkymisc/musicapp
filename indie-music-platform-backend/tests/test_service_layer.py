import pytest
import uuid
from unittest.mock import patch, MagicMock
from app.services import auth_service
from app.schemas.user import UserCreate, UserRole

# テスト用のデータベースセッション
class MockSession:
    def __init__(self):
        self.objects = {}
        self.queries = []
        
    def add(self, obj):
        self.objects[obj.id] = obj
        
    def commit(self):
        pass
        
    def refresh(self, obj):
        pass
        
    def query(self, model):
        return MockQuery(self, model)
        
class MockQuery:
    def __init__(self, session, model):
        self.session = session
        self.model = model
        self.filters = []
        
    def filter(self, condition):
        self.filters.append(condition)
        return self
        
    def first(self):
        return None  # 常にNoneを返す（ユーザーが存在しない状態）

# テスト関数
def test_register_user():
    # モックセッションの作成
    mock_db = MockSession()
    
    # 登録データ
    user_data = UserCreate(
        email="test@example.com",
        firebase_uid="test_firebase_uid",
        display_name="Test User",
        user_role=UserRole.LISTENER
    )
    
    # ユーザー登録
    user = auth_service.register_user(db=mock_db, user_data=user_data)
    
    # 検証
    assert user.email == user_data.email
    assert user.firebase_uid == user_data.firebase_uid
    assert user.display_name == user_data.display_name
    assert user.user_role == user_data.user_role
    assert user.is_verified == True  # MVPフェーズでは自動的に検証済み
