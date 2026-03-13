from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import Table
from sqlalchemy.orm import relationship

chat_members = Table(
    "chat_members",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("chat_id", ForeignKey("chats.id"))
)

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)  
    is_group = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    members = relationship("User", secondary="chat_members", back_populates="chats")
    messages = relationship("Message", back_populates="chat")
