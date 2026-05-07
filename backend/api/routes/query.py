import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.core.retriever import retrieve_chunks
from backend.core.reranker import rerank_chunks
from backend.core.llm import generate_answer
from backend.schemas.query import QueryRequest, QueryResponse

logger = logging.getLogger(__name__)

router = APIRouter()

FTS_CANDIDATES = 10  # Retrieve this many before re-ranking


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    RAG pipeline: FTS retrieval → re-ranking → LLM answer generation.
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Step 1: FTS retrieval
    retrieved = await retrieve_chunks(
        session=db,
        question=question,
        limit=FTS_CANDIDATES,
    )

    if not retrieved:
        return QueryResponse(
            answer=(
                "I could not find any relevant documents to answer your question. "
                "Please upload some documents first."
            ),
            sources=[],
            model="none",
            usage={},
        )

    # Step 2: Re-rank
    top_chunks = await rerank_chunks(
        chunks=retrieved,
        question=question,
        top_k=request.top_k,
    )

    # Step 3: LLM answer
    result = await generate_answer(chunks=top_chunks, question=question)

    return QueryResponse(
        answer=result["answer"],
        sources=top_chunks,
        model=result["model"],
        usage=result["usage"],
    )
