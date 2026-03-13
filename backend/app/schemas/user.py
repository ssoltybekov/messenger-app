from pydantic import BaseModel, field_validator
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    phone: str
    password: str

    @field_validator("password")
    @classmethod
    def password_strenght(cls, value):
        if len(value) < 8:
            raise ValueError("Minumum 8 symbols")
        return value
    
    @field_validator("username")
    @classmethod
    def username_min(cls, value):
        if len(value) < 3:
            raise ValueError("Minumum 3 symbols")
        return value

class UserLogin(BaseModel):
    phone: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    phone: str
    created_at: datetime
    last_seen: datetime | None = None
    
    class Config:
        from_attributes = True