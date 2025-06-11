from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid
from enum import Enum as PyEnum
from app.schemas.user import UserRole


class User(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    firebase_uid = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    profile_image = Column(String, nullable=True)
    user_role = Column(Enum(UserRole), nullable=False, default=UserRole.LISTENER)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # リレーションシップ
    tracks = relationship("Track", back_populates="artist")
    purchases = relationship("Purchase", back_populates="user")


