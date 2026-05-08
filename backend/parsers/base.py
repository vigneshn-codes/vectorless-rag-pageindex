from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class ParsedPage:
    """Represents a single parsed page or logical section from a document."""

    def __init__(
        self,
        page_number: Optional[int],
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.page_number = page_number
        self.content = content.strip()
        self.metadata = metadata or {}


class BaseParser(ABC):
    """Abstract base class for all document parsers."""

    @abstractmethod
    def parse(self, file_bytes: bytes, filename: str) -> List[ParsedPage]:
        """
        Parse raw file bytes and return a list of ParsedPage objects.
        Each ParsedPage has page_number (None if not applicable), content, and metadata.
        Implementations should skip empty or failed pages rather than raising exceptions.
        """
        ...

    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of lowercase file extensions this parser handles (e.g. ['.pdf'])."""
        ...
