import json
from typing import Dict, List
from fastapi import WebSocket
from sqlalchemy.orm import Session
from redis.asyncio import Redis
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

    async def send_to_chat(self, chat_id: int, message: dict, db: Session, redis: Redis):
        cache_key = f"chat:{chat_id}:members"

        cashed_members = await redis.get(cache_key)
        if cashed_members:
            member_ids = json.loads(cached_members)
        else:
            chat = db.query(Chat).filter(Chat.id == chat_id).first()
            if not chat:
                return
            member_ids = [member.id for member in chat.members]
            await redis.set(cache_key, json.dumps(member_ids), ex=300)
        
        for user_id in member_ids:
            await self.send_to_user(user_id, message)

manager = ConnectionManager()