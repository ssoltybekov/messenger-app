from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    author: str = Field(..., min_length=1, description="Имя отправителя")
    text: str = Field(..., min_length=1, description="Текст сообщения")
    timestamp: Optional[datetime] = Field(None, description="Время отправки")

class SummaryRequest(BaseModel):
    messages: List[ChatMessage] = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="Список сообщений для анализа"
    )
    target_lang: str = Field(
        "en", 
        pattern=r"^[a-z]{2}$", 
        description="Язык, на котором нужно выдать саммари (ISO код)"
    )

class SummaryResponse(BaseModel):
    summary_text: str = Field(..., description="Краткая выжимка чата")
    processed_count: int = Field(..., description="Сколько сообщений было обработано")
    language: str = Field(..., description="Язык итогового текста")