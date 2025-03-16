from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr
import uuid
from typing import Any


@as_declarative()
class Base:
    id: Any
    __name__: str
    
    # 自動的にテーブル名を生成
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # 共通カラム
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


