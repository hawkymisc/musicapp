from sqlalchemy.orm import Session
from app.models.purchase import Purchase, PurchaseStatus, PaymentMethod
from app.models.track import Track
from app.schemas.purchase import PurchaseCreate
from app.services.payment import process_payment
from app.services.storage import generate_presigned_url
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from typing import List
import uuid


def create_purchase(db: Session, purchase_data: PurchaseCreate, user_id: str) -> Purchase:
    """
    楽曲購入を処理
    """
    # 楽曲の存在確認
    track = db.query(Track).filter(Track.id == purchase_data.track_id).first()
    if not track:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="楽曲が見つかりません"
        )
    
    # 自分の楽曲は購入できないようにする
    if track.artist_id == user_id:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="自分の楽曲は購入できません"
        )
    
    # 既に購入済みかチェック
    existing_purchase = db.query(Purchase).filter(
        Purchase.user_id == user_id,
        Purchase.track_id == purchase_data.track_id,
        Purchase.status == PurchaseStatus.COMPLETED
    ).first()
    
    if existing_purchase:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="この楽曲は既に購入済みです"
        )
    
    # 支払い処理
    payment_result = process_payment(
        amount=purchase_data.amount,
        payment_token=purchase_data.payment_token,
        description=f"Purchase: {track.title}"
    )
    
    # 購入レコードの作成
    purchase = Purchase(
        user_id=user_id,
        track_id=purchase_data.track_id,
        amount=purchase_data.amount,
        payment_method=purchase_data.payment_method,
        transaction_id=payment_result["transaction_id"],
        status=PurchaseStatus.COMPLETED
    )
    
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase


def get_user_purchases(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Purchase]:
    """
    ユーザーの購入履歴を取得
    """
    return db.query(Purchase)\
        .filter(
            Purchase.user_id == user_id,
            Purchase.status == PurchaseStatus.COMPLETED
        )\
        .order_by(Purchase.purchase_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_purchase(db: Session, purchase_id: str, user_id: str) -> Purchase:
    """
    購入詳細を取得
    """
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="購入記録が見つかりません"
        )
    
    # 権限チェック
    if purchase.user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="この購入記録にアクセスする権限がありません"
        )
    
    return purchase


def get_download_url(db: Session, track_id: str, user_id: str) -> str:
    """
    購入済み楽曲のダウンロードURL（署名付きURL）を取得
    """
    # 購入確認
    purchase = db.query(Purchase).filter(
        Purchase.user_id == user_id,
        Purchase.track_id == track_id,
        Purchase.status == PurchaseStatus.COMPLETED
    ).first()
    
    if not purchase:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="この楽曲を購入していません"
        )
    
    # 楽曲情報取得
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="楽曲が見つかりません"
        )
    
    # オブジェクト名の抽出（URLからキーを取り出す）
    object_key = track.audio_file_url.split(f"{BUCKET_NAME}.s3.amazonaws.com/")[1]
    
    # 署名付きURL生成（24時間有効）
    signed_url = generate_presigned_url(object_key, expiration=86400)
    return signed_url
