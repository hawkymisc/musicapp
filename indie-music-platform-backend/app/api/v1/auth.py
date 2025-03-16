from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, User as UserSchema, UserUpdate
from app.services import auth_service
from app.core.security import get_current_user
from typing import Dict, Any

router = APIRouter()


@router.post("/register", response_model=UserSchema)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    新規ユーザー登録
    """
    return auth_service.register_user(db=db, user_data=user_data)


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: UserSchema = Depends(get_current_user)
) -> Any:
    """
    現在のユーザー情報を取得
    """
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_user_info(
    user_update: UserUpdate,
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    ユーザー情報を更新
    """
    return auth_service.update_user(
        db=db, 
        user_id=current_user.id, 
        user_data=user_update
    )


