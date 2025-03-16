from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.track import Track
from app.core.security import get_current_artist
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND


async def validate_track_ownership(
    track_id: str,
    current_user: User = Depends(get_current_artist),
    db: Session = Depends(get_db)
) -> Track:
    """
    楽曲の所有権を検証する
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="楽曲が見つかりません"
        )
    
    if track.artist_id != current_user.id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="この楽曲を編集する権限がありません"
        )
    
    return track
