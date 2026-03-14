from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserResponse
from app.services import auth
from app.database import get_db
from app.schemas.token import Token
from app.models.token import RefreshToken
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

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
    # refresh_token = auth.create_refresh_token(user.id)

    refresh_token_raw = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(refresh_token_raw.encode()).hexdigest()
    expire_date = datetime.now(timezone.utc) + timedelta(days=30)

    db_refresh_token = RefreshToken(
        token_hash=token_hash,
        user_id=user.id,
        expires_at=expire_date
    )
    db.add(db_refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_raw, 
        "token_type": "bearer"
    }

@router.post("/refresh_tokens", response_model=Token, status_code=200)
def refresh_access_token(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    new_access_token = auth.refresh_tokens(db, refresh_token=refresh_token)

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    auth.logout(db, refresh_token=refresh_token)

    return None