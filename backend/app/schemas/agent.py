from pydantic import BaseModel


class AgentQuery(BaseModel):
    query: str


class AgentStep(BaseModel):
    step_type: str  # plan, execute, synthesize
    tool: str | None = None
    description: str
    detail: str
    duration_ms: int


class AgentResponse(BaseModel):
    query: str
    steps: list[AgentStep]
    answer: str
    latency_ms: int
