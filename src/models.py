from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime
import uuid

class Event(BaseModel):
    topic: str = Field(..., example="system.logs")
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    source: str = Field(..., example="publisher-1")
    payload: Dict[str, Any] = Field(..., example={"message": "User login success"})
