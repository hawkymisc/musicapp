from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.track import TrackCreate, Track as TrackSchema, TrackUpdate, TrackWithArtist, TrackListItem
from app.services import track_service
from app.core.security import get_current_user, get_current_artist
from app.api.dependencies.auth import validate_track_ownership
from app.models.user import User
from typing import Dict, Any, List, Optional
from datetime import date

router = APIRouter()


@router.get("/", response_model=List[TrackListItem])
async def list_tracks(
    skip: int = 0,
    limit: int = 100,
    genre: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_desc: bool = True,
    db: Session = Depends(get_db)
) -> Any:
    """
    楽曲一覧を取得
    """
    return track_service.get_tracks(
        db=db,
        skip=skip,
        limit=limit,
        genre=genre,
        search=search,
        sort_by=sort_by,
        sort_desc=sort_desc
    )


@router.post("/", response_model=TrackSchema)
async def create_track(
    track_data: TrackCreate,
    current_user: User = Depends(get_current_artist),
    db: Session = Depends(get_db)
) -> Any:
    """
    新規楽曲を登録（アーティストのみ）
    """
    return track_service.create_track(
        db=db,
        track_data=track_data,
        artist_id=current_user.id
    )


@router.get("/{track_id}", response_model=TrackWithArtist)
async def get_track(
    track_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    楽曲詳細を取得
    """
    return track_service.get_track(db=db, track_id=track_id)


@router.put("/{track_id}", response_model=TrackSchema)
async def update_track(
    track_id: str,
    track_data: TrackUpdate,
    track: TrackSchema = Depends(validate_track_ownership),
    db: Session = Depends(get_db)
) -> Any:
    """
    楽曲情報を更新（所有アーティストのみ）
    """
    return track_service.update_track(
        db=db,
        track_id=track_id,
        track_data=track_data
    )


@router.delete("/{track_id}")
async def delete_track(
    track_id: str,
    track: TrackSchema = Depends(validate_track_ownership),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    楽曲を削除（所有アーティストのみ）
    """
    track_service.delete_track(db=db, track_id=track_id)
    return {"status": "success", "message": "楽曲が削除されました"}


@router.post("/upload/cover")
async def upload_cover_art(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_artist)
) -> Dict[str, str]:
    """
    カバーアート画像をアップロード（アーティストのみ）
    """
    url = track_service.upload_cover_art(file=file, user_id=current_user.id)
    return {"url": url}


@router.post("/upload/audio")
async def upload_audio_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_artist)
) -> Dict[str, str]:
    """
    音声ファイルをアップロード（アーティストのみ）
    """
    url = track_service.upload_audio_file(file=file, user_id=current_user.id)
    return {"url": url}


@router.get("/artist/{artist_id}", response_model=List[TrackListItem])
async def get_artist_tracks(
    artist_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    アーティストの楽曲一覧を取得
    """
    return track_service.get_artist_tracks(
        db=db,
        artist_id=artist_id,
        skip=skip,
        limit=limit
    )


@router.get("/search", response_model=List[TrackListItem])
async def search_tracks(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    楽曲を検索
    """
    return track_service.search_tracks(
        db=db,
        query=query,
        skip=skip,
        limit=limit
    )


