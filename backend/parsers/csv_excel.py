import io
from typing import List
import logging

from backend.parsers.base import BaseParser, ParsedPage

logger = logging.getLogger(__name__)

ROWS_PER_CHUNK = 50


class CSVExcelParser(BaseParser):
    """Parses CSV and Excel files using pandas. Groups rows into chunks of ROWS_PER_CHUNK."""

    @property
    def supported_extensions(self) -> List[str]:
        return [".csv", ".xlsx", ".xls"]

    def parse(self, file_bytes: bytes, filename: str) -> List[ParsedPage]:
        try:
            import pandas as pd
        except ImportError:
            logger.error("pandas is not installed.")
            return []

        pages: List[ParsedPage] = []
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

        try:
            buf = io.BytesIO(file_bytes)
            if ext == "csv":
                df = pd.read_csv(buf, dtype=str)
            else:
                df = pd.read_excel(buf, dtype=str)
        except Exception as e:
            logger.error(f"Failed to read {filename}: {e}")
            return []

        df = df.fillna("")
        columns = list(df.columns)
        total_rows = len(df)

        if total_rows == 0:
            return []

        chunk_num = 0
        for start in range(0, total_rows, ROWS_PER_CHUNK):
            chunk_num += 1
            end = min(start + ROWS_PER_CHUNK, total_rows)
            subset = df.iloc[start:end]

            lines = []
            for _, row in subset.iterrows():
                parts = [f"{col}: {row[col]}" for col in columns if str(row[col]).strip()]
                lines.append(" | ".join(parts))

            content = "\n".join(lines)
            if content.strip():
                pages.append(
                    ParsedPage(
                        page_number=None,
                        content=content,
                        metadata={
                            "chunk_num": chunk_num,
                            "row_start": start + 1,
                            "row_end": end,
                            "columns": columns,
                        },
                    )
                )

        return pages
