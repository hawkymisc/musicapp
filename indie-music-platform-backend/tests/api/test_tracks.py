import pytest
from fastapi import status
import json


def test_list_tracks(client, db, test_track):
    """
    楽曲一覧取得テスト
    """
    response = client.get("/api/v1/tracks/")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data) >= 1
    assert any(track["id"] == test_track.id for track in data)


def test_get_track(client, db, test_track):
    """
    楽曲詳細取得テスト
    """
    response = client.get(f"/api/v1/tracks/{test_track.id}")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == test_track.id
    assert data["title"] == test_track.title
    assert data["artist"]["id"] == test_track.artist_id


def test_create_track_artist(client, db, test_artist, mock_firebase_auth):
    """
    アーティストによる楽曲作成テスト
    """
    track_data = {
        "title": "New Track",
        "description": "Brand new track",
        "genre": "Pop",
        "cover_art_url": "https://example.com/new_cover.jpg",
        "audio_file_url": "https://example.com/new_audio.mp3",
        "duration": 240,
        "price": 300,
        "release_date": "2025-03-01",
        "is_public": True
    }
    
    # アーティストとして認証
    headers = {"Authorization": f"Bearer artist_token"}
    
    response = client.post(
        "/api/v1/tracks/",
        headers=headers,
        json=track_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["title"] == track_data["title"]
    assert data["artist_id"] == test_artist.id


def test_update_track(client, db, test_track, test_artist, mock_firebase_auth):
    """
    楽曲更新テスト
    """
    update_data = {
        "title": "Updated Track Title",
        "price": 400
    }
    
    # アーティストとして認証
    headers = {"Authorization": f"Bearer artist_token"}
    
    response = client.put(
        f"/api/v1/tracks/{test_track.id}",
        headers=headers,
        json=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["price"] == update_data["price"]
    # 更新していない項目は元の値が維持される
    assert data["genre"] == test_track.genre


def test_delete_track(client, db, test_track, test_artist, mock_firebase_auth):
    """
    楽曲削除テスト
    """
    # アーティストとして認証
    headers = {"Authorization": f"Bearer artist_token"}
    
    response = client.delete(
        f"/api/v1/tracks/{test_track.id}",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    # 削除されたことを確認
    response = client.get(f"/api/v1/tracks/{test_track.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


