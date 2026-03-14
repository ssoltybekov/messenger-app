from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatCreate(BaseModel):
    name: Optional[str] = None
    is_group: bool = False
    is_public: bool = False
    participant_ids: list[int] = []

class ChatResponse(ChatCreate):
    id: int
    created_at: datetime