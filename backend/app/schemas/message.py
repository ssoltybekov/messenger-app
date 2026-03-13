from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    chat_id: int
    content: str

class MessageResponse(MessageCreate):
    id: int
    sender_id: int
    created_at: datetime