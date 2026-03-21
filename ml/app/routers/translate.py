import asyncio
from fastapi import APIRouter, HTTPException
from app.schemas.translate import TranslationRequest, TranslationResponse
from app.services.translation import (
    translate_text, 
    detect_language, 
    ModelNotFoundError, 
    TranslationError
)

router = APIRouter(
    prefix="/translate",
    tags=["ML"]
)

@router.post("/")
async def translate(request: TranslationRequest):
    source = request.source_lang
    if not source:
        source = detect_language(request.text)

    if source == request.target_lang:
        return TranslationResponse(
            translated_text=request.text,
            source_lang=source,
            target_lang=request.target_lang
        )
    
    try:
        loop = asyncio.get_running_loop()
        translated = await loop.run_in_executor(
            None, 
            translate_text, 
            request.text, 
            source, 
            request.target_lang
        )

        return TranslationResponse(
            translated_text=translated,
            source_lang=source,
            target_lang=request.target_lang
        )

    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except TranslationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    