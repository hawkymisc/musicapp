from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, Date, Text, Numeric
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid


class Track(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id = Column(String, ForeignKey("user.id"), nullable=False)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    genre = Column(String, nullable=True, index=True)
    cover_art_url = Column(String, nullable=True)
    audio_file_url = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # 秒単位
    price = Column(Numeric(10, 2), nullable=False)
    release_date = Column(Date, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    play_count = Column(Integer, default=0, nullable=False)
    
    # リレーションシップ
    artist = relationship("User", back_populates="tracks")
    purchases = relationship("Purchase", back_populates="track")


