from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from app.schemas.ask import AskRequest, AskResponse
from app.services.rag_service import RAGService
from app.dependencies import get_rag_service

router = APIRouter()


@router.post("", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    return await rag_service.ask(request.question, max_sources=request.max_sources)


@router.post("/stream")
async def ask_stream(
    request: AskRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    async def event_generator():
        async for chunk in rag_service.ask_stream(request.question, max_sources=request.max_sources):
            yield {"event": "message", "data": chunk}
        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())
