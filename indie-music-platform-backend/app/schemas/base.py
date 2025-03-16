from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        validate_assignment = True


