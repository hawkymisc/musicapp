from pydantic import BaseModel
from datetime import datetime
from app.schemas.base import BaseSchema


class StreamRequest(BaseSchema):
    track_id: str


class StreamResponse(BaseSchema):
    url: str  # 署名付きURL
    expires_at: datetime


class PlayEvent(BaseSchema):
    track_id: str
    duration: int  # 実際に再生された秒数
