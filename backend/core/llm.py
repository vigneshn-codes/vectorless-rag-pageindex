import logging
from typing import List

from openai import AsyncOpenAI

from backend.config import settings
from backend.schemas.query import SourceChunk

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a document assistant. Answer based only on the provided context. "
    "If the answer is not in the context, say so clearly. "
    "Be concise and accurate. Cite page numbers or sources when relevant."
)


def _build_context(chunks: List[SourceChunk]) -> str:
    """Format retrieved chunks into a context block for the LLM."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        location = f"(p. {chunk.page_number})" if chunk.page_number else ""
        parts.append(
            f"[Source {i}: {chunk.filename} {location}]\n{chunk.snippet}"
        )
    return "\n\n---\n\n".join(parts)


async def generate_answer(
    chunks: List[SourceChunk],
    question: str,
) -> dict:
    """
    Call OpenAI chat completion with retrieved context chunks.
    Returns dict with keys: answer, model, usage.
    """
    if not settings.OPENAI_API_KEY:
        return {
            "answer": "No OpenAI API key configured. Please set OPENAI_API_KEY in your .env file.",
            "model": "none",
            "usage": {},
        }

    context = _build_context(chunks)
    user_message = f"Context:\n{context}\n\nQuestion: {question}"

    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=1024,
        )

        answer = response.choices[0].message.content or ""
        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return {
            "answer": answer,
            "model": response.model,
            "usage": usage,
        }

    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return {
            "answer": f"Failed to generate answer: {str(e)}",
            "model": settings.OPENAI_MODEL,
            "usage": {},
        }
