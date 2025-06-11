from sqlalchemy.orm import Session
from app.models.track import Track
from app.models.user import User
from app.schemas.track import TrackCreate, TrackUpdate, TrackListItem
from fastapi import HTTPException, UploadFile
from app.services.storage import upload_file_to_s3
from sqlalchemy import desc, asc, or_
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from typing import List, Optional
import uuid
import os
from datetime import datetime


def get_tracks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    genre: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_desc: bool = True
) -> List[TrackListItem]:
    """
    楽曲一覧を取得
    """
    query = db.query(
        Track.id.label("track_id"),  # 列エイリアスを修正
        Track.title.label("track_title"),
        Track.artist_id.label("track_artist_id"),
        User.display_name.label("artist_name"),
        Track.cover_art_url.label("track_cover_art_url"),
        Track.duration.label("track_duration"),
        Track.price.label("track_price"),
        Track.genre.label("track_genre"),
        Track.release_date.label("track_release_date"),
        Track.play_count.label("track_play_count")
    ).join(User, Track.artist_id == User.id)\
    .filter(Track.is_public == True)
    
    # ジャンルフィルター
    if genre:
        query = query.filter(Track.genre == genre)
    
    # 検索フィルター
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Track.title.ilike(search_term),
                User.display_name.ilike(search_term)
            )
        )
    
    # ソート
    if sort_by:
        if sort_by == "title":
            sort_col = Track.title
        elif sort_by == "artist":
            sort_col = User.display_name
        elif sort_by == "price":
            sort_col = Track.price
        elif sort_by == "release_date":
            sort_col = Track.release_date
        elif sort_by == "play_count":
            sort_col = Track.play_count
        else:
            sort_col = Track.created_at
        
        if sort_desc:
            query = query.order_by(desc(sort_col))
        else:
            query = query.order_by(asc(sort_col))
    
    # ページネーション
    query = query.offset(skip).limit(limit)
    
    # 結果を辞書形式で取得
    rows = query.all()
    results = []
    for row in rows:
        # rowの属性を使って辞書を作成（スキーマに合わせて）
        result_dict = {
            "id": row.track_id,
            "title": row.track_title,
            "artist_id": row.track_artist_id,
            "artist_name": row.artist_name,
            "cover_art_url": row.track_cover_art_url,
            "duration": row.track_duration,
            "price": float(row.track_price) if row.track_price else None,
            "genre": row.track_genre,
            "release_date": row.track_release_date if row.track_release_date else None,
            "play_count": row.track_play_count
        }
        results.append(result_dict)
    return results


def get_track(db: Session, track_id: str):
    """
    楽曲詳細を取得
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="楽曲が見つかりません"
        )
    
    # 非公開楽曲はアーティスト本人のみ閲覧可能
    # (この実装は簡略化されています - 本番では権限チェックを追加)
    if not track.is_public:
        # ここでは簡略化のため、正確な権限チェックは省略
        pass
    
    return track


def create_track(db: Session, track_data: TrackCreate, artist_id: str) -> Track:
    """
    新規楽曲を登録
    """
    track = Track(
        artist_id=artist_id,
        title=track_data.title,
        description=track_data.description,
        genre=track_data.genre,
        cover_art_url=track_data.cover_art_url,
        audio_file_url=track_data.audio_file_url,
        duration=track_data.duration,
        price=track_data.price,
        release_date=track_data.release_date,
        is_public=track_data.is_public,
        play_count=0
    )
    
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


def update_track(db: Session, track_id: str, track_data: TrackUpdate) -> Track:
    """
    楽曲情報を更新
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="楽曲が見つかりません"
        )
    
    # 更新可能なフィールドのみを更新
    if track_data.title is not None:
        track.title = track_data.title
    if track_data.description is not None:
        track.description = track_data.description
    if track_data.genre is not None:
        track.genre = track_data.genre
    if track_data.cover_art_url is not None:
        track.cover_art_url = track_data.cover_art_url
    if track_data.price is not None:
        track.price = track_data.price
    if track_data.is_public is not None:
        track.is_public = track_data.is_public
    
    db.commit()
    db.refresh(track)
    return track


def delete_track(db: Session, track_id: str) -> None:
    """
    楽曲を削除
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="楽曲が見つかりません"
        )
    
    db.delete(track)
    db.commit()


def upload_cover_art(file: UploadFile, user_id: str) -> str:
    """
    カバーアート画像をアップロード
    """
    # ファイル形式チェック
    allowed_extensions = [".jpg", ".jpeg", ".png"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="サポートされていないファイル形式です。JPGまたはPNG形式のみ対応しています。"
        )
    
    # ファイル名の生成
    unique_filename = f"covers/{user_id}/{uuid.uuid4()}{file_ext}"
    
    # S3へアップロード
    url = upload_file_to_s3(file, unique_filename)
    return url


def upload_audio_file(file: UploadFile, user_id: str) -> str:
    """
    音声ファイルをアップロード
    """
    # ファイル形式チェック
    allowed_extensions = [".mp3", ".wav", ".flac", ".aac", ".m4a"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="サポートされていないファイル形式です。MP3, WAV, FLAC, AAC, M4A形式のみ対応しています。"
        )
    
    # ファイル名の生成
    unique_filename = f"tracks/{user_id}/{uuid.uuid4()}{file_ext}"
    
    # S3へアップロード
    url = upload_file_to_s3(file, unique_filename)
    return url


def get_artist_tracks(db: Session, artist_id: str, skip: int = 0, limit: int = 100) -> List[TrackListItem]:
    """
    アーティストの楽曲一覧を取得
    """
    query = db.query(
        Track.id.label("track_id"),
        Track.title.label("track_title"),
        Track.artist_id.label("track_artist_id"),
        User.display_name.label("artist_name"),
        Track.cover_art_url.label("track_cover_art_url"),
        Track.duration.label("track_duration"),
        Track.price.label("track_price"),
        Track.genre.label("track_genre"),
        Track.release_date.label("track_release_date"),
        Track.play_count.label("track_play_count")
    ).join(User, Track.artist_id == User.id)\
    .filter(Track.artist_id == artist_id, Track.is_public == True)\
    .order_by(desc(Track.release_date))\
    .offset(skip).limit(limit)
    
    results = [dict(row) for row in query.all()]
    return results


def search_tracks(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[TrackListItem]:
    """
    楽曲を検索
    """
    search_term = f"%{query}%"
    query = db.query(
        Track.id.label("track_id"),
        Track.title.label("track_title"),
        Track.artist_id.label("track_artist_id"),
        User.display_name.label("artist_name"),
        Track.cover_art_url.label("track_cover_art_url"),
        Track.duration.label("track_duration"),
        Track.price.label("track_price"),
        Track.genre.label("track_genre"),
        Track.release_date.label("track_release_date"),
        Track.play_count.label("track_play_count")
    ).join(User, Track.artist_id == User.id)\
    .filter(
        Track.is_public == True,
        or_(
            Track.title.ilike(search_term),
            User.display_name.ilike(search_term),
            Track.genre.ilike(search_term)
        )
    )\
    .order_by(desc(Track.play_count))\
    .offset(skip).limit(limit)
    
    results = [dict(row) for row in query.all()]
    return results


