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
    url = purchase_service.get_download_url(
        db=db,
        track_id=track_id,
        user_id=current_user.id
    )
    return {"download_url": url}


