from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.message import MessageResponse, MessageCreate
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.models.message import Message
from app.models.chat import Chat

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)

@router.get("/{chat_id}", response_model=list[MessageResponse])
def get_message(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat or current_user not in chat.members:
        raise HTTPException(status_code=403, detail="Access denied to this chat")
    
    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()

@router.post("/", response_model=MessageResponse)
def create_message(message_data: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.id == message_data.chat_id).first()
    if not chat or current_user not in chat.members:
        raise HTTPException(status_code=403, detail="You can't send messages to this chat")
    
    message = Message(
        content=message_data.content,
        chat_id=message_data.chat_id,
        sender_id=current_user.id
    )

    db.add(message)
    db.commit()
    db.refresh(message)
    return message

@router.put("/{message_id}", response_model=MessageResponse)
def update_message(message_id: int, message_data: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own messages")
    
    message.content = message_data.content
    db.commit()
    db.refresh(message)
    return message

@router.delete("/{message_id}", response_model=MessageResponse)
def delete_message(message_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own messages")

    db.delete(message)
    db.commit()
    return message
