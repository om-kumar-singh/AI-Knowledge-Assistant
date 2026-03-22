"""RAG query: retrieve local chunks, answer with local FLAN-T5."""

from fastapi import APIRouter

from models.schemas import QueryRequest, QueryResponse
from rag.retriever import retrieve
from services.llm_service import generate_answer

router = APIRouter(tags=["rag"])


@router.post("/query", response_model=QueryResponse)
async def rag_query(body: QueryRequest) -> QueryResponse:
    sources = retrieve(body.query)
    answer = generate_answer(body.query, sources)
    return QueryResponse(query=body.query, answer=answer, sources=sources)
