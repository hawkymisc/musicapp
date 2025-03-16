from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum
from datetime import datetime
from app.schemas.base import BaseSchema


class UserRole(str, Enum):
    ARTIST = "artist"
    LISTENER = "listener"
    ADMIN = "admin"


class UserBase(BaseSchema):
    email: EmailStr
    display_name: str
    profile_image: Optional[str] = None
    user_role: UserRole = UserRole.LISTENER


class UserCreate(UserBase):
    firebase_uid: str


class UserUpdate(BaseSchema):
    display_name: Optional[str] = None
    profile_image: Optional[str] = None


class UserInDB(UserBase):
    id: str
    firebase_uid: str
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime


class User(UserInDB):
    pass


class UserProfile(BaseSchema):
    id: str
    display_name: str
    profile_image: Optional[str] = None
    user_role: UserRole
    is_verified: bool
    created_at: datetime


