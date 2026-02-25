from fastapi import APIRouter, Depends

from app.schemas.agent import AgentQuery, AgentResponse
from app.services.agent_service import AgentService
from app.dependencies import get_agent_service

router = APIRouter()


@router.post("/query", response_model=AgentResponse)
async def agent_query(
    request: AgentQuery,
    agent_service: AgentService = Depends(get_agent_service),
):
    return await agent_service.run(request.query)
