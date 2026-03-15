import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.database import get_db
from app.websocket import manager
from app.models.message import Message
from app.services.auth import JWT_SECRET, JWT_ALGORITHM 

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    # await websocket.accept()

    token = websocket.query_params.get("token")
    
    try:
        if not token:
            raise JWTError
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise JWTError
    except JWTError:
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            new_msg = Message(
                content=message_data.get("content"),
                chat_id=message_data.get("chat_id"),
                sender_id=user_id
            )
            db.add(new_msg)
            db.commit()
            db.refresh(new_msg)

            payload_to_send = {
                "type": "new_message",
                "data": {
                    "id": new_msg.id,
                    "content": new_msg.content,
                    "sender_id": user_id,
                    "chat_id": new_msg.chat_id
                }
            }
            await manager.send_to_chat(new_msg.chat_id, payload_to_send, db)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WS Error: {e}")
        manager.disconnect(user_id)