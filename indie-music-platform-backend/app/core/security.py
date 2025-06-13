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
        
        # 本番環境でのTESTINGモード禁止
        if os.environ.get('TESTING') == 'True':
            # テスト環境でのみモック処理を許可
            # 追加のセキュリティチェック：本番環境での誤用防止
            if os.environ.get('ENVIRONMENT') == 'production':
                logger.critical("本番環境でテストモードが有効になっています。セキュリティリスクです。")
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="認証設定エラー"
                )
            
            # テスト専用トークン処理（より厳格な検証）
            if token == "mock_token_artist":
                firebase_uid = "firebaseuid_artist"
            elif token == "mock_token_listener":
                firebase_uid = "firebaseuid_listener"
            elif token.startswith("mock_token_") and len(token) > 11:
                # テスト用のトークンパターン（最小長チェック）
                firebase_uid = token.replace("mock_token_", "")
                # firebase_uidの形式検証
                if not firebase_uid or len(firebase_uid) < 3:
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="無効なテストトークン形式"
                    )
            else:
                logger.warning(f"不正なテストトークン試行: {token[:10]}...")
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="無効なテストトークンです"
                )
        else:
            # 実際のFirebase検証（本番モード）
            if not token or len(token) < 10:  # 最小トークン長チェック
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="無効なトークン形式"
                )
            
            try:
                # Firebase トークン検証
                decoded_token = auth.verify_id_token(token)
                firebase_uid = decoded_token.get("uid")
                
                # Firebase UIDの検証
                if not firebase_uid or len(firebase_uid) < 10:
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="無効なユーザーID"
                    )
                
                # トークンの有効期限チェック（Firebaseが自動で行うが念のため）
                token_exp = decoded_token.get("exp", 0)
                import time
                if token_exp < time.time():
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="トークンの有効期限が切れています"
                    )
                    
            except auth.InvalidIdTokenError as e:
                logger.warning(f"Firebase トークン検証失敗: {str(e)}")
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="無効なトークンです"
                )
            except auth.ExpiredIdTokenError:
                logger.warning("期限切れトークンでのアクセス試行")
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="トークンの有効期限が切れています"
                )
            except Exception as e:
                logger.error(f"Firebase認証エラー: {str(e)}")
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="認証に失敗しました"
                )
        
        # DBからユーザー情報を取得
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            logger.warning(f"存在しないユーザーでのアクセス試行: {firebase_uid}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="ユーザーが見つかりません"
            )
        
        # ユーザーアクティブ状態の基本チェック
        if hasattr(user, 'is_active') and not user.is_active:
            logger.warning(f"非アクティブユーザーでのアクセス試行: {user.id}")
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="アカウントが無効です"
            )
            
        return user
        
    except HTTPException:
        # HTTPExceptionはそのまま再発生
        raise
    except Exception as e:
        # 本番環境では詳細エラー情報を隠す
        logger.error(f"認証処理中の予期しないエラー: {str(e)}")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="認証に失敗しました"
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
