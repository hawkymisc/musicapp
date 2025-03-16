from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserProfile
from app.schemas.track import TrackListItem
from app.services import user_service, track_service
from app.core.security import get_current_user
from typing import Dict, Any, List
from app.models.user import User

router = APIRouter()


@router.get("/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    ユーザープロフィールを取得
    """
    return user_service.get_user_profile(db=db, user_id=user_id)


@router.post("/upload/profile-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    プロフィール画像をアップロード
    """
    url = user_service.upload_profile_image(file=file, user_id=current_user.id)
    return {"url": url}


