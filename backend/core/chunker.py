from typing import List, Optional
from backend.parsers.base import ParsedPage


TARGET_WORDS_MIN = 500
TARGET_WORDS_MAX = 1000
TARGET_CHARS_JSON = 800


class Chunk:
    """Represents a text chunk ready for DB insertion."""

    def __init__(
        self,
        page_number: Optional[int],
        chunk_index: int,
        content: str,
        metadata: dict,
    ):
        self.page_number = page_number
        self.chunk_index = chunk_index
        self.content = content
        self.metadata = metadata


def pages_to_chunks(pages: List[ParsedPage], file_type: str) -> List[Chunk]:
    """
    Convert parsed pages into DB-ready chunks.

    Strategy:
    - PDF: each page is already a natural chunk boundary — use as-is.
    - CSV/Excel: pages already represent row-groups from the parser.
    - DOCX/HTML/JSON/TXT/MD: pages already represent text chunks from the parser.
      We additionally ensure each chunk is within word-count limits by splitting large ones.
    """
    chunks: List[Chunk] = []
    chunk_index = 0

    for page in pages:
        if not page.content.strip():
            continue

        word_count = len(page.content.split())

        if file_type == "pdf":
            # PDF pages are natural boundaries — keep whole
            chunks.append(
                Chunk(
                    page_number=page.page_number,
                    chunk_index=chunk_index,
                    content=page.content,
                    metadata=page.metadata,
                )
            )
            chunk_index += 1

        elif word_count <= TARGET_WORDS_MAX:
            # Small enough — keep as-is
            chunks.append(
                Chunk(
                    page_number=page.page_number,
                    chunk_index=chunk_index,
                    content=page.content,
                    metadata=page.metadata,
                )
            )
            chunk_index += 1

        else:
            # Split large chunk by paragraph
            sub_chunks = _split_by_words(page.content, TARGET_WORDS_MAX)
            for sub in sub_chunks:
                if sub.strip():
                    chunks.append(
                        Chunk(
                            page_number=page.page_number,
                            chunk_index=chunk_index,
                            content=sub,
                            metadata={**page.metadata, "split": True},
                        )
                    )
                    chunk_index += 1

    return chunks


def _split_by_words(text: str, max_words: int) -> List[str]:
    """
    Split text into chunks of at most max_words words,
    trying to break at paragraph boundaries.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    result = []
    current_paras: List[str] = []
    current_words = 0

    for para in paragraphs:
        para_words = len(para.split())
        if current_words + para_words > max_words and current_paras:
            result.append("\n\n".join(current_paras))
            current_paras = [para]
            current_words = para_words
        else:
            current_paras.append(para)
            current_words += para_words

    if current_paras:
        result.append("\n\n".join(current_paras))

    return result
