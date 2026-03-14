from fastapi import WebSocket
from typing import Dict
from sqlalchemy.orm import Session
from app.models.chat import Chat

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_to_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    async def send_to_chat(self, chat_id: int, message: dict, db: Session):
        chat = db.query(Chat).filter(Chat.id == chat_id).first()

        if chat:
            for user in chat.members:
                await self.send_to_user(user.id, message)