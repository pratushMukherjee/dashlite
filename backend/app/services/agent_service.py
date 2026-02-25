import time
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.query_log import QueryLog
from app.models.activity import ActivityEvent
from app.services.search_service import SearchService
from app.services.llm_client import LLMClient
from app.schemas.agent import AgentResponse, AgentStep

PLANNING_PROMPT = """You are a planning agent. Given the user's query, decompose it into 2-4 sequential steps using these available tools:

Available tools:
- search: Search indexed documents for specific information
- summarize: Summarize content from search results
- compare: Compare information from two different search results
- extract: Extract specific data points from search results
- analyze: Analyze patterns or trends across search results

Query: {query}

Respond in JSON format:
{{
  "reasoning": "Brief explanation of your approach",
  "steps": [
    {{"tool": "tool_name", "input": "what to search/analyze", "description": "Human-readable step description"}}
  ]
}}

Important: Each step should use one of the listed tools. The "input" field should describe what to search for or what to do."""

SYNTHESIS_PROMPT = """You are DashLite, an AI assistant. Based on the following multi-step analysis, provide a comprehensive answer to the user's query.

Original query: {query}

Step results:
{step_results}

Provide a clear, well-structured answer using markdown formatting. Reference specific findings from each step."""


class AgentService:
    """
    Multi-step agent inspired by Dropbox Dash's planning + execution model.
    Decomposes complex queries into sub-tasks, executes them, and synthesizes results.
    """

    def __init__(
        self,
        search_service: SearchService,
        llm_client: LLMClient,
        db: AsyncSession,
    ):
        self.search_service = search_service
        self.llm_client = llm_client
        self.db = db

    async def run(self, query: str) -> AgentResponse:
        total_start = time.time()
        steps = []

        # Phase 1: PLANNING
        plan_start = time.time()
        plan = await self._create_plan(query)
        plan_ms = int((time.time() - plan_start) * 1000)

        steps.append(AgentStep(
            step_type="plan",
            tool=None,
            description=f"Created execution plan: {plan.get('reasoning', 'Planning query decomposition')}",
            detail=json.dumps(plan.get("steps", []), indent=2),
            duration_ms=plan_ms,
        ))

        # Phase 2: EXECUTION
        context_accumulator = []
        planned_steps = plan.get("steps", [])

        for planned_step in planned_steps:
            step_start = time.time()
            tool = planned_step.get("tool", "search")
            step_input = planned_step.get("input", query)
            description = planned_step.get("description", f"Executing {tool}")

            result = await self._execute_step(tool, step_input, context_accumulator)
            context_accumulator.append({"tool": tool, "input": step_input, "result": result})

            step_ms = int((time.time() - step_start) * 1000)
            steps.append(AgentStep(
                step_type="execute",
                tool=tool,
                description=description,
                detail=result[:500],
                duration_ms=step_ms,
            ))

        # Phase 3: SYNTHESIS
        synth_start = time.time()
        final_answer = await self._synthesize(query, context_accumulator)
        synth_ms = int((time.time() - synth_start) * 1000)

        steps.append(AgentStep(
            step_type="synthesize",
            tool=None,
            description="Synthesized final answer from all steps",
            detail=f"Combined {len(context_accumulator)} step results",
            duration_ms=synth_ms,
        ))

        total_ms = int((time.time() - total_start) * 1000)

        # Log
        log = QueryLog(query_text=query, query_type="agent", result_count=len(steps), latency_ms=total_ms)
        self.db.add(log)
        activity = ActivityEvent(
            event_type="query_agent",
            detail=json.dumps({"query": query[:100], "steps": len(steps)}),
        )
        self.db.add(activity)
        await self.db.commit()

        return AgentResponse(query=query, steps=steps, answer=final_answer, latency_ms=total_ms)

    async def _create_plan(self, query: str) -> dict:
        prompt = PLANNING_PROMPT.format(query=query)
        response = self.llm_client.generate(prompt, json_mode=True, max_tokens=512)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "reasoning": "Fallback: performing direct search",
                "steps": [{"tool": "search", "input": query, "description": f"Search for: {query}"}],
            }

    async def _execute_step(self, tool: str, step_input: str, prior_context: list) -> str:
        if tool == "search":
            search_response = await self.search_service.hybrid_search(step_input, limit=5)
            if not search_response.results:
                return "No results found."
            return "\n\n".join(
                f"[{r.file_name}] {r.text}" for r in search_response.results
            )

        elif tool in ("summarize", "analyze", "extract"):
            # Use search results + LLM to summarize/analyze/extract
            search_response = await self.search_service.hybrid_search(step_input, limit=5)
            if not search_response.results:
                return "No relevant content found to analyze."

            content = "\n\n".join(f"[{r.file_name}] {r.text}" for r in search_response.results)
            action_prompts = {
                "summarize": f"Summarize the following content:\n\n{content}",
                "analyze": f"Analyze the following content for patterns and insights:\n\n{content}",
                "extract": f"Extract key data points from the following content:\n\n{content}",
            }
            return self.llm_client.generate(action_prompts[tool], max_tokens=512)

        elif tool == "compare":
            # Compare using prior context
            if len(prior_context) >= 2:
                content = "\n\n---\n\n".join(
                    f"Result from step '{c['input']}':\n{c['result']}" for c in prior_context[-2:]
                )
            else:
                search_response = await self.search_service.hybrid_search(step_input, limit=5)
                content = "\n\n".join(f"[{r.file_name}] {r.text}" for r in search_response.results)

            return self.llm_client.generate(
                f"Compare and contrast the following:\n\n{content}\n\nHighlight key similarities and differences.",
                max_tokens=512,
            )

        return f"Unknown tool: {tool}"

    async def _synthesize(self, query: str, context: list) -> str:
        step_results = "\n\n".join(
            f"Step {i + 1} ({c['tool']}: {c['input']}):\n{c['result']}" for i, c in enumerate(context)
        )
        prompt = SYNTHESIS_PROMPT.format(query=query, step_results=step_results)
        return self.llm_client.generate(prompt, max_tokens=1024)
