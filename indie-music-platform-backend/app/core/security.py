import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import UserRole
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.db.session import get_db
from sqlalchemy.orm import Session
from typing import Optional
import os
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

# Firebaseの初期化
cred = credentials.Certificate(os.environ.get("FIREBASE_CREDENTIALS_PATH"))
firebase_app = firebase_admin.initialize_app(cred)

# セキュリティスキーマ
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Firebase認証トークンを検証してユーザーを取得する
    """
    try:
        # Bearerトークンを検証
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        firebase_uid = decoded_token.get("uid")
        
        # DBからユーザー情報を取得
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="ユーザーが見つかりません"
            )
        return user
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです"
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"認証エラー: {str(e)}"
        )


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    現在のアクティブユーザーを取得する
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="アカウントが未確認です"
        )
    return current_user


def get_current_artist(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    現在のアーティストユーザーを取得する
    """
    if current_user.user_role != UserRole.ARTIST and current_user.user_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="アーティスト権限が必要です"
        )
    return current_user


def get_current_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    現在の管理者ユーザーを取得する
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です"
        )
    return current_user


