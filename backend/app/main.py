from fastapi import FastAPI
from app.routers import auth
from app.database import engine, Base
from app.models import user, chat, message, token
from app.routers import chats
from app.routers import messages
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chats.router)
app.include_router(messages.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Messenger API is running"}