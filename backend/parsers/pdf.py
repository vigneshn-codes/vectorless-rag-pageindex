import io
from typing import List
import logging

from backend.parsers.base import BaseParser, ParsedPage

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    """Parses PDF files using PyMuPDF. Each page becomes one ParsedPage."""

    @property
    def supported_extensions(self) -> List[str]:
        return [".pdf"]

    def parse(self, file_bytes: bytes, filename: str) -> List[ParsedPage]:
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.error("PyMuPDF is not installed. Install it with: pip install PyMuPDF")
            return []

        pages: List[ParsedPage] = []
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num in range(len(doc)):
                try:
                    page = doc[page_num]
                    text = page.get_text("text")
                    if text and text.strip():
                        pages.append(
                            ParsedPage(
                                page_number=page_num + 1,
                                content=text,
                                metadata={"source_page": page_num + 1},
                            )
                        )
                except Exception as e:
                    logger.warning(
                        f"Failed to parse page {page_num + 1} of {filename}: {e}"
                    )
                    continue
            doc.close()
        except Exception as e:
            logger.error(f"Failed to open PDF {filename}: {e}")

        return pages
