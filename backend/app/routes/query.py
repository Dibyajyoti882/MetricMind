"""Owner: Member 1 (Team Lead) — API surface for the frontend."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent.agent import ask

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    transparency: list[dict]


@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")
    result = ask(req.question)
    return QueryResponse(**result)