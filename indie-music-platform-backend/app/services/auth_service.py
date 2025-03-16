from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND


def get_user_by_firebase_uid(db: Session, firebase_uid: str) -> User:
    """
    Firebase UIDでユーザーを取得
    """
    return db.query(User).filter(User.firebase_uid == firebase_uid).first()


def get_user_by_email(db: Session, email: str) -> User:
    """
    メールアドレスでユーザーを取得
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> User:
    """
    IDでユーザーを取得
    """
    return db.query(User).filter(User.id == user_id).first()


def register_user(db: Session, user_data: UserCreate) -> User:
    """
    新規ユーザーを登録
    """
    # メールアドレスの重複チェック
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています"
        )
    
    # Firebase UIDの重複チェック
    existing_uid = get_user_by_firebase_uid(db, user_data.firebase_uid)
    if existing_uid:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="このアカウントは既に登録されています"
        )
    
    # ユーザーデータの作成
    user = User(
        email=user_data.email,
        firebase_uid=user_data.firebase_uid,
        display_name=user_data.display_name,
        profile_image=user_data.profile_image,
        user_role=user_data.user_role,
        is_verified=True  # MVP段階では検証済みとする
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: str, user_data: UserUpdate) -> User:
    """
    ユーザー情報を更新
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )
    
    # 更新可能なフィールドのみを更新
    if user_data.display_name is not None:
        user.display_name = user_data.display_name
    if user_data.profile_image is not None:
        user.profile_image = user_data.profile_image
    
    db.commit()
    db.refresh(user)
    return user


