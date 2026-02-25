from fastapi import APIRouter

from app.api.v1.endpoints import search, files, ingest, ask, summarize, agent, activity, ws

api_router = APIRouter()

api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(ask.router, prefix="/ask", tags=["ask"])
api_router.include_router(summarize.router, prefix="/summarize", tags=["summarize"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(activity.router, prefix="/activity", tags=["activity"])
api_router.include_router(ws.router, prefix="/ws", tags=["websocket"])
