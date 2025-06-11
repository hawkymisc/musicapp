from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from app.schemas.base import BaseSchema
from app.schemas.track import Track
from app.schemas.user import User


class PaymentMethod(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    PAYPAL = "PAYPAL" 
    APPLE_PAY = "APPLE_PAY"
    GOOGLE_PAY = "GOOGLE_PAY"


class PurchaseStatus(str, Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"
    REFUNDED = "refunded"


class PurchaseBase(BaseSchema):
    track_id: str
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod


class PurchaseCreate(PurchaseBase):
    payment_token: str  # Stripe等から取得したトークン


class PurchaseInDB(PurchaseBase):
    id: str
    user_id: str
    purchase_date: datetime
    transaction_id: str
    status: PurchaseStatus
    created_at: datetime
    updated_at: datetime


class Purchase(PurchaseInDB):
    pass


class PurchaseWithDetails(Purchase):
    track: Track
    

