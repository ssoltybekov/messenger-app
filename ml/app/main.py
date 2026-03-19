from contextlib import asynccontextmanager
from fastapi import FastAPI
import whisper
from app.routers import summarize, transcribe, translate

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.whisper = whisper.load_model("base")
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(summarize.router)
app.include_router(transcribe.router)
app.include_router(translate.router)