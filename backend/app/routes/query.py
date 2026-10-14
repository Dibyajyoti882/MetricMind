"""
Routing (ROUTING_MODE in backend/.env: auto | direct | agent):
  simple question        -> direct Cube.dev query, no LLM
  "why did X drop"       -> LLM agent first; falls back to direct analysis if the LLM fails
  complex question       -> LLM agent only; clear error if the LLM is unavailable
"""
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app import analytics
from app.agent import agent as agent_mod
from app.agent.agent import LLMUnavailableError
from app.semantic_client.cube_client import SemanticLayerError

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    transparency: list[dict]
    mode: str = "agent"
    note: str | None = None
    chart: dict | None = None
    cached: bool = False


def _direct(kind, spec):
    return analytics.run_rca(spec) if kind == "rca" else analytics.run_simple(spec)


@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question must not be empty")
    if len(question) > 500:
        raise HTTPException(status_code=400, detail="question too long (max 500 chars)")

    routing = os.getenv("ROUTING_MODE", "auto").lower()
    kind, spec = analytics.classify(question)

    try:
        if routing == "direct" and kind in ("simple", "rca"):
            return QueryResponse(**_direct(kind, spec))
        if routing == "auto" and kind == "simple":
            return QueryResponse(**_direct(kind, spec))

        try:
            return QueryResponse(**agent_mod.ask(question))
        except LLMUnavailableError as e:
            if kind in ("simple", "rca"):
                out = _direct(kind, spec)
                out["mode"] = "fallback"
                out["note"] = f"LLM unavailable, used direct semantic-layer analysis. Reason: {e}"
                return QueryResponse(**out)
            raise HTTPException(
                status_code=503,
                detail=f"{e} This question needs the AI agent; try a simpler question "
                       f"(e.g. 'revenue by region in Q3') or fix the LLM key.")
    except SemanticLayerError as e:
        raise HTTPException(status_code=502, detail=f"Semantic layer problem: {e}")