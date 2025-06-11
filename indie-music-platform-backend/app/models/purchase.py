from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid
from enum import Enum as PyEnum
from datetime import datetime


class PaymentMethod(PyEnum):
    CREDIT_CARD = "CREDIT_CARD"
    PAYPAL = "PAYPAL"
    APPLE_PAY = "APPLE_PAY"
    GOOGLE_PAY = "GOOGLE_PAY"


class PurchaseStatus(PyEnum):
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"
    REFUNDED = "refunded"


class Purchase(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user.id"), nullable=False, index=True)
    track_id = Column(String, ForeignKey("track.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    purchase_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    transaction_id = Column(String, nullable=False, unique=True)
    status = Column(Enum(PurchaseStatus), default=PurchaseStatus.PENDING, nullable=False)
    
    # リレーションシップ
    user = relationship("User", back_populates="purchases")
    track = relationship("Track", back_populates="purchases")


