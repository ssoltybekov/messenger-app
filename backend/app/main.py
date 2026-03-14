from fastapi import FastAPI
from app.routers import auth
from app.database import engine, Base
from app.models import user, chat, message, token

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Messenger API is running"}