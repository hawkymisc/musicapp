from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from app.schemas.base import BaseSchema
from app.schemas.user import UserProfile


class TrackBase(BaseSchema):
    title: str
    description: Optional[str] = None
    genre: Optional[str] = None
    cover_art_url: Optional[str] = None
    duration: int = Field(..., gt=0)  # 0より大きい整数
    price: float = Field(..., ge=0)  # 0以上の数値
    release_date: date


class TrackCreate(TrackBase):
    audio_file_url: str
    is_public: bool = True


class TrackUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    cover_art_url: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    is_public: Optional[bool] = None


class TrackInDB(TrackBase):
    id: str
    artist_id: str
    audio_file_url: str
    is_public: bool
    play_count: int
    created_at: datetime
    updated_at: datetime


class Track(TrackInDB):
    pass


class TrackWithArtist(Track):
    artist: UserProfile


class TrackListItem(BaseSchema):
    id: str
    title: str
    artist_id: str
    artist_name: str
    cover_art_url: Optional[str] = None
    duration: int
    price: float
    genre: Optional[str] = None
    release_date: date
    play_count: int


