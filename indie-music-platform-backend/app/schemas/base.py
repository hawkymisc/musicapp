from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )


