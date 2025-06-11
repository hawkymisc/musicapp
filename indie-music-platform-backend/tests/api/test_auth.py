import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
from app.schemas.user import UserRole


def test_register_user(client, db):
    """
    ユーザー登録テスト
    """
    user_data = {
        "email": "newuser@example.com",
        "firebase_uid": "firebaseuid_new",
        "display_name": "New User",
        "user_role": UserRole.LISTENER.value
    }
    
    response = client.post(
        "/api/v1/auth/register",
        json=user_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["display_name"] == user_data["display_name"]
    assert data["user_role"] == user_data["user_role"]


def test_get_current_user(client, db, test_listener, mock_firebase_auth):
    """
    現在のユーザー情報取得テスト
    """
    # リスナーとして認証
    headers = {"Authorization": "Bearer listener_token"}
    
    response = client.get(
        "/api/v1/auth/me",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == test_listener.id
    assert data["email"] == test_listener.email
    assert data["display_name"] == test_listener.display_name


def test_update_user(client, db, test_listener, mock_firebase_auth):
    """
    ユーザー情報更新テスト
    """
    update_data = {
        "display_name": "Updated Listener Name",
        "profile_image": "https://example.com/new_profile.jpg"
    }
    
    # リスナーとして認証
    headers = {"Authorization": "Bearer listener_token"}
    
    response = client.put(
        "/api/v1/auth/me",
        headers=headers,
        json=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["display_name"] == update_data["display_name"]
    assert data["profile_image"] == update_data["profile_image"]
