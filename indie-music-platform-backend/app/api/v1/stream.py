from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.stream import StreamRequest, StreamResponse, PlayEvent
from app.services import stream_service
from app.core.security import get_current_user
from app.models.user import User
from typing import Dict, Any, Optional

router = APIRouter()


@router.post("/{track_id}", response_model=StreamResponse)
async def get_stream_url(
    track_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    楽曲ストリーミングURL（署名付きURL）を取得
    """
    user_id = current_user.id if current_user else None
    return stream_service.get_stream_url(
        db=db,
        track_id=track_id,
        user_id=user_id
    )


@router.post("/{track_id}/play")
async def record_play(
    track_id: str,
    play_data: PlayEvent,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    再生カウントを記録
    """
    user_id = current_user.id if current_user else None
    stream_service.record_play(
        db=db,
        track_id=track_id,
        user_id=user_id,
        duration=play_data.duration
    )
    return {"status": "success"}


