from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserResponse
from app.services import auth
from app.database import get_db
from app.schemas.token import Token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    new_user = auth.register_user(db=db, user_data=user_data)
    return new_user

@router.post("/login", response_model=Token, status_code=200)
def login(login_data: UserCreate, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")

    access_token = auth.create_access_token(user.id)
    refresh_token = auth.create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }
