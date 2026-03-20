from contextlib import asynccontextmanager
from fastapi import FastAPI
import whisper
from app.routers import summarize, transcribe, translate
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.whisper = whisper.load_model("base")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(summarize.router)
app.include_router(transcribe.router)
app.include_router(translate.router)