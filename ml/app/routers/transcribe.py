import os
import shutil
from fastapi import APIRouter, UploadFile, File, Request
from tempfile import NamedTemporaryFile
import asyncio

router = APIRouter(
    prefix="/audio",
    tags=["ML"]
)

@router.post("/transcribe")
async def transcribe_audio(request: Request, file: UploadFile = File(...)):
    model = request.app.state.whisper

    with NamedTemporaryFile(delete=False, suffix=".tmp") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            model.transcribe,
            temp_path
        )

        return {
            "filename": file.filename,
            "text": result["text"]
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
