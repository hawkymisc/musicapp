import pytest
from app.services import track_service
from app.schemas.track import TrackCreate, TrackUpdate
from datetime import date


def test_get_tracks(db, test_track):
    """
    楽曲一覧取得サービステスト
    """
    tracks = track_service.get_tracks(db)
    assert len(tracks) >= 1
    assert any(track["track_id"] == test_track.id for track in tracks)


def test_get_track(db, test_track):
    """
    楽曲詳細取得サービステスト
    """
    track = track_service.get_track(db, test_track.id)
    assert track.id == test_track.id
    assert track.title == test_track.title
    assert track.artist_id == test_track.artist_id


def test_create_track(db, test_artist):
    """
    楽曲作成サービステスト
    """
    track_data = TrackCreate(
        title="Service Test Track",
        description="Created by service test",
        genre="Jazz",
        cover_art_url="https://example.com/service_cover.jpg",
        audio_file_url="https://example.com/service_audio.mp3",
        duration=300,
        price=600,
        release_date=date.today(),
        is_public=True
    )
    
    track = track_service.create_track(db, track_data, test_artist.id)
    
    assert track.title == track_data.title
    assert track.artist_id == test_artist.id
    assert track.price == track_data.price


def test_update_track(db, test_track):
    """
    楽曲更新サービステスト
    """
    update_data = TrackUpdate(
        title="Updated Service Track",
        price=750
    )
    
    updated_track = track_service.update_track(db, test_track.id, update_data)
    
    assert updated_track.title == update_data.title
    assert updated_track.price == update_data.price
    assert updated_track.genre == test_track.genre  # 更新していないフィールドは変更なし


def test_delete_track(db, test_track):
    """
    楽曲削除サービステスト
    """
    track_service.delete_track(db, test_track.id)
    
    # 削除されたことを確認
    with pytest.raises(Exception):
        track_service.get_track(db, test_track.id)
