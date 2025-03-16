from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid
from datetime import datetime


class PlayHistory(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user.id"), nullable=True, index=True)  # 匿名再生もあり得る
    track_id = Column(String, ForeignKey("track.id"), nullable=False, index=True)
    played_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    play_duration = Column(Integer, nullable=True)  # 実際に再生された秒数（途中終了の場合）
    
    # リレーションシップ
    track = relationship("Track")
    user = relationship("User")
