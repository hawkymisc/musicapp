from sqlalchemy.orm import Session
from app.models.user import User
from fastapi import HTTPException, UploadFile
from app.services.storage import upload_file_to_s3
from starlette.status import HTTP_404_NOT_FOUND
import os
import uuid


def get_user_profile(db: Session, user_id: str) -> User:
    """
    ユーザープロフィールを取得
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )
    return user


async def upload_profile_image(file: UploadFile, user_id: str) -> str:
    """
    プロフィール画像をアップロード
    """
    # ファイル形式チェック
    allowed_extensions = [".jpg", ".jpeg", ".png"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="サポートされていないファイル形式です。JPGまたはPNG形式のみ対応しています。"
        )
    
    # ファイル名の生成
    unique_filename = f"profiles/{user_id}/{uuid.uuid4()}{file_ext}"
    
    # S3へアップロード
    url = await upload_file_to_s3(file, unique_filename)
    return url


