from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.chat import ChatResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatCreate
from app.models.user import User
from app.services.auth import get_current_user
from app.models.chat import Chat

router = APIRouter(
    prefix="/chats",
    tags=["chats"]
)

@router.get("/", response_model=list[ChatResponse])
def get_chats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chats = db.query(Chat).filter(Chat.members.contains(current_user)).all()
    return chats

@router.post("/", response_model=ChatResponse)
def create_chat(chat_data: ChatCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_chat = Chat(name=chat_data.name, is_group=chat_data.is_group, is_public=chat_data.is_public)
    new_chat.members.append(current_user)

    if chat_data.is_group and chat_data.participant_ids:
        other_members = db.query(User).filter(User.id.in_(chat_data.participant_ids), User.id != current_user.id ).all()
        new_chat.members.extend(other_members)

    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    return new_chat

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    if current_user not in chat.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not a member of this chat"
        )
    
    return chat
    

@router.delete("/{chat_id}", response_model=ChatResponse)
def delete_chat(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    if current_user not in chat.members:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(chat)
    db.commit()

    return chat