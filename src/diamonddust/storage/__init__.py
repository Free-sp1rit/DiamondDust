"""Storage adapter boundaries for DiamondDust."""

from diamonddust.storage.markdown import (
    FrontmatterValue,
    IngestedMarkdownEssay,
    MarkdownIngestionError,
    compute_content_hash,
    ingest_markdown_text,
    read_markdown_essay,
)

__all__ = [
    "FrontmatterValue",
    "IngestedMarkdownEssay",
    "MarkdownIngestionError",
    "compute_content_hash",
    "ingest_markdown_text",
    "read_markdown_essay",
]
