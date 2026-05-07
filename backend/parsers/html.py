from typing import List
import logging

from backend.parsers.base import BaseParser, ParsedPage
from backend.parsers.json_txt import _split_text_into_chunks

logger = logging.getLogger(__name__)


class HTMLParser(BaseParser):
    """Parses HTML files using BeautifulSoup."""

    @property
    def supported_extensions(self) -> List[str]:
        return [".html", ".htm"]

    def parse(self, file_bytes: bytes, filename: str) -> List[ParsedPage]:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            logger.error("beautifulsoup4 is not installed.")
            return []

        pages: List[ParsedPage] = []
        try:
            raw = file_bytes.decode("utf-8", errors="replace")
            soup = BeautifulSoup(raw, "lxml")

            # Remove script and style elements
            for tag in soup(["script", "style", "noscript", "head"]):
                tag.decompose()

            # Extract text block by block to preserve structure
            text_blocks = []

            # Try to get meaningful sections
            for tag in soup.find_all(
                ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "pre", "blockquote"]
            ):
                text = tag.get_text(separator=" ", strip=True)
                if text:
                    text_blocks.append(text)

            if not text_blocks:
                # Fall back to full text extraction
                full_text = soup.get_text(separator="\n", strip=True)
                text_blocks = [full_text]

            full_text = "\n\n".join(text_blocks)
            chunks = _split_text_into_chunks(full_text)

            for idx, chunk in enumerate(chunks):
                if chunk.strip():
                    pages.append(
                        ParsedPage(
                            page_number=None,
                            content=chunk,
                            metadata={"chunk_index": idx},
                        )
                    )

        except Exception as e:
            logger.error(f"Failed to parse HTML {filename}: {e}")

        return pages
