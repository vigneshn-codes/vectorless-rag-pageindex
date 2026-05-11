import os
from typing import List
import logging

from backend.parsers.base import BaseParser, ParsedPage
from backend.parsers.pdf import PDFParser
from backend.parsers.csv_excel import CSVExcelParser
from backend.parsers.docx import DOCXParser
from backend.parsers.json_txt import JSONTXTParser
from backend.parsers.html import HTMLParser

logger = logging.getLogger(__name__)

_PARSERS: List[BaseParser] = [
    PDFParser(),
    CSVExcelParser(),
    DOCXParser(),
    JSONTXTParser(),
    HTMLParser(),
]

_EXTENSION_MAP: dict[str, BaseParser] = {}
for _parser in _PARSERS:
    for _ext in _parser.supported_extensions:
        _EXTENSION_MAP[_ext.lower()] = _parser


def get_file_extension(filename: str) -> str:
    """Return lowercase file extension including the dot, e.g. '.pdf'"""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def route_file(file_bytes: bytes, filename: str) -> List[ParsedPage]:
    """
    Route a file to the appropriate parser based on its extension.
    Returns a list of ParsedPage objects.
    Raises ValueError if the file type is not supported.
    """
    ext = get_file_extension(filename)
    parser = _EXTENSION_MAP.get(ext)

    if parser is None:
        raise ValueError(
            f"Unsupported file type: '{ext}'. "
            f"Supported types: {sorted(_EXTENSION_MAP.keys())}"
        )

    logger.info(f"Routing {filename} (ext={ext}) to {parser.__class__.__name__}")
    return parser.parse(file_bytes, filename)


def supported_extensions() -> List[str]:
    """Return all supported file extensions."""
    return sorted(_EXTENSION_MAP.keys())
