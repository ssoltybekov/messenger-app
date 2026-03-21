import asyncio
from fastapi import APIRouter, HTTPException
from app.schemas.summarize import SummaryRequest, SummaryResponse
from app.services.summarize import summarize_messages

router = APIRouter(
    prefix="/summarize",
    tags=["ML"]
)

@router.post("/", response_model=SummaryResponse)
async def summarize(request: SummaryRequest):
    try:
        loop = asyncio.get_running_loop()
        summarized = await loop.run_in_executor(
            None,
            summarize_messages, 
            request.messages, 
            request.target_lang
        )

        return SummaryResponse(
            summary_text=summarized,
            processed_count=len(request.messages),
            language=request.target_lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")