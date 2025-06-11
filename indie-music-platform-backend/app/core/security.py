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
import logging

# ロガー設定
logger = logging.getLogger(__name__)

# Firebaseの初期化を遅延させる
firebase_app = None

# セキュリティスキーマ
security = HTTPBearer()

def init_firebase():
    global firebase_app
    if firebase_app is not None:
        return

    # テスト中やFirebase設定が存在しない場合は初期化しない
    if os.environ.get('TESTING') == 'True':
        logger.info("テストモードのため、Firebase初期化をスキップします")
        # テストモードでもfirebase_appにダミー値を設定しておく
        firebase_app = "mock_firebase_app"
        return
    
    try:
        cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
        if cred_path and os.path.exists(cred_path):
            logger.info(f"Firebaseを初期化します: {cred_path}")
            cred = credentials.Certificate(cred_path)
            firebase_app = firebase_admin.initialize_app(cred)
            logger.info("Firebase初期化が完了しました")
        else:
            logger.warning(f"Firebase認証情報が見つかりません: {cred_path}")
            # 認証情報がない場合もダミー値を設定しておく
            firebase_app = "dummy_firebase_app"
    except Exception as e:
        logger.error(f"Firebase初期化エラー: {e}")
        # エラー発生時もダミー値を設定しておく
        firebase_app = "error_firebase_app"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Firebase認証トークンを検証してユーザーを取得する
    """
    try:
        # Firebaseの初期化を確認
        init_firebase()
        
        # Bearerトークンを検証
        token = credentials.credentials
        
        # テストモードの場合は、特別なトークン処理
        if os.environ.get('TESTING') == 'True':
            # モックToken処理
            if token == "artist_token":
                firebase_uid = "firebaseuid_artist"
            elif token == "listener_token":
                firebase_uid = "firebaseuid_listener"
            else:
                firebase_uid = None
        else:
            # 実際のFirebase検証
            try:
                decoded_token = auth.verify_id_token(token)
                firebase_uid = decoded_token.get("uid")
            except Exception as e:
                logger.error(f"トークン検証エラー: {e}")
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="無効なトークンです"
                )
        
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
        logger.error(f"認証エラー: {e}")
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
