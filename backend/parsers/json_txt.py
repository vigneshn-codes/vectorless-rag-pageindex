import json
from typing import List
import logging

from backend.parsers.base import BaseParser, ParsedPage

logger = logging.getLogger(__name__)

TARGET_CHUNK_CHARS = 800


def _split_text_into_chunks(text: str, target_size: int = TARGET_CHUNK_CHARS) -> List[str]:
    """Split text by paragraphs and merge into chunks of approximately target_size chars."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    if not paragraphs:
        # Fall back to line splitting
        paragraphs = [line.strip() for line in text.split("\n") if line.strip()]

    if not paragraphs:
        return [text.strip()] if text.strip() else []

    chunks = []
    current_chunk: List[str] = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len > target_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_len = para_len
        else:
            current_chunk.append(para)
            current_len += para_len

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


class JSONTXTParser(BaseParser):
    """Parses JSON, TXT, and Markdown files."""

    @property
    def supported_extensions(self) -> List[str]:
        return [".json", ".txt", ".md", ".markdown"]

    def parse(self, file_bytes: bytes, filename: str) -> List[ParsedPage]:
        ext = "." + filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        pages: List[ParsedPage] = []

        try:
            raw_text = file_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            logger.error(f"Failed to decode {filename}: {e}")
            return []

        if ext == ".json":
            try:
                data = json.loads(raw_text)
                pretty = json.dumps(data, indent=2, ensure_ascii=False)
                chunks = _split_text_into_chunks(pretty, target_size=TARGET_CHUNK_CHARS)
            except json.JSONDecodeError:
                # Not valid JSON — treat as plain text
                chunks = _split_text_into_chunks(raw_text)
        else:
            # TXT, MD, Markdown
            chunks = _split_text_into_chunks(raw_text)

        for idx, chunk in enumerate(chunks):
            if chunk.strip():
                pages.append(
                    ParsedPage(
                        page_number=None,
                        content=chunk,
                        metadata={"chunk_index": idx},
                    )
                )

        return pages
