import json
import logging
from typing import List

from openai import AsyncOpenAI

from backend.config import settings
from backend.schemas.query import SourceChunk

logger = logging.getLogger(__name__)

RERANK_PROMPT_TEMPLATE = """You are a relevance ranking assistant. Given a question and a list of text chunks,
return the indices of the top {top_k} most relevant chunks in order of relevance (most relevant first).

Question: {question}

Chunks:
{chunks}

Respond with ONLY a JSON array of integer indices (0-based), e.g. [2, 0, 4, 1, 3].
Return exactly {top_k} indices (or fewer if there are fewer chunks). Do not include any explanation."""


async def rerank_chunks(
    chunks: List[SourceChunk],
    question: str,
    top_k: int = 5,
) -> List[SourceChunk]:
    """
    Re-rank retrieved chunks using OpenAI.
    Falls back to original order if the API call fails or returns invalid JSON.
    Returns the top_k most relevant chunks.
    """
    if not chunks:
        return []

    if len(chunks) <= top_k:
        return chunks

    if not settings.OPENAI_API_KEY:
        logger.warning("No OpenAI API key set. Skipping re-ranking.")
        return chunks[:top_k]

    numbered_chunks = "\n\n".join(
        f"[{i}] {chunk.snippet}" for i, chunk in enumerate(chunks)
    )

    prompt = RERANK_PROMPT_TEMPLATE.format(
        question=question,
        chunks=numbered_chunks,
        top_k=min(top_k, len(chunks)),
    )

    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=100,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        indices = json.loads(raw)

        if not isinstance(indices, list):
            raise ValueError("Re-ranker did not return a list")

        # Validate and deduplicate indices
        seen = set()
        valid_indices = []
        for idx in indices:
            if isinstance(idx, int) and 0 <= idx < len(chunks) and idx not in seen:
                valid_indices.append(idx)
                seen.add(idx)
            if len(valid_indices) >= top_k:
                break

        if not valid_indices:
            raise ValueError("No valid indices returned by re-ranker")

        reranked = [chunks[i] for i in valid_indices]
        logger.info(f"Re-ranked {len(chunks)} chunks to top {len(reranked)}")
        return reranked

    except Exception as e:
        logger.warning(f"Re-ranking failed, falling back to original order: {e}")
        return chunks[:top_k]
