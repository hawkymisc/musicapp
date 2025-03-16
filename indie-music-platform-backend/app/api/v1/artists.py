from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserProfile
from app.services import artist_service
from app.core.security import get_current_artist
from app.models.user import User
from typing import Dict, Any, List
from datetime import date

router = APIRouter()


@router.get("/revenue", response_model=Dict[str, Any])
async def get_artist_revenue(
    start_date: date = None,
    end_date: date = None,
    current_user: User = Depends(get_current_artist),
    db: Session = Depends(get_db)
) -> Any:
    """
    アーティスト収益情報を取得
    """
    return artist_service.get_artist_revenue(
        db=db,
        artist_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/stats", response_model=Dict[str, Any])
async def get_artist_stats(
    start_date: date = None,
    end_date: date = None,
    current_user: User = Depends(get_current_artist),
    db: Session = Depends(get_db)
) -> Any:
    """
    アーティスト統計情報を取得
    """
    return artist_service.get_artist_stats(
        db=db,
        artist_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )


