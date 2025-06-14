from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.core.feature_flags import is_payment_enabled, get_payment_coming_soon_message
from app.schemas.purchase import Purchase, PurchaseCreate, PurchaseWithDetails
from app.services import purchase_service

router = APIRouter()

@router.post("/", response_model=Purchase)
async def purchase_track(
    purchase_data: PurchaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    楽曲を購入
    """
    # 決済機能が無効の場合
    if not is_payment_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": get_payment_coming_soon_message(),
                "payment_enabled": False,
                "coming_soon": True
            }
        )
    
    return purchase_service.create_purchase(
        db=db,
        purchase_data=purchase_data,
        user_id=current_user.id
    )


@router.get("/", response_model=List[PurchaseWithDetails])
async def get_user_purchases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    ユーザーの購入履歴を取得
    """
    return purchase_service.get_user_purchases(
        db=db,
        user_id=current_user.id
    )


@router.get("/{purchase_id}", response_model=PurchaseWithDetails)
async def get_purchase(
    purchase_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    購入詳細を取得
    """
    return purchase_service.get_purchase(
        db=db,
        purchase_id=purchase_id,
        user_id=current_user.id
    )


@router.get("/track/{track_id}/download")
async def download_purchased_track(
    track_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    購入済み楽曲のダウンロードURL（署名付きURL）を取得
    """
    # 決済機能が無効の場合は無料ダウンロード
    if not is_payment_enabled():
        # 無料モードでは全楽曲ダウンロード可能
        from app.models.track import Track
        track = db.query(Track).filter(Track.id == track_id).first()
        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="楽曲が見つかりません"
            )
        
        # 無料ダウンロード用のURL生成
        from app.services.storage import generate_presigned_url
        object_key = track.audio_file_url.split("/")[-1]  # ファイル名を抽出
        signed_url = generate_presigned_url(object_key, expiration=86400)
        return {
            "download_url": signed_url,
            "free_download": True,
            "message": "現在は無料ダウンロード期間中です"
        }
    
    url = purchase_service.get_download_url(
        db=db,
        track_id=track_id,
        user_id=current_user.id
    )
    return {"download_url": url}