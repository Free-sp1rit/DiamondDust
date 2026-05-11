"""Storage adapter boundaries for DiamondDust."""

from diamonddust.storage.candidate_markdown import (
    AI_CANDIDATE_NOTES_DIR,
    CandidateMarkdownError,
    CandidateMarkdownExport,
    CandidateMarkdownFile,
    CandidateMarkdownManifest,
    render_candidate_markdown,
    write_candidate_markdown_export,
)
from diamonddust.storage.markdown import (
    FrontmatterValue,
    IngestedMarkdownEssay,
    MarkdownIngestionError,
    compute_content_hash,
    ingest_markdown_text,
    read_markdown_essay,
)

__all__ = [
    "AI_CANDIDATE_NOTES_DIR",
    "CandidateMarkdownError",
    "CandidateMarkdownExport",
    "CandidateMarkdownFile",
    "CandidateMarkdownManifest",
    "FrontmatterValue",
    "IngestedMarkdownEssay",
    "MarkdownIngestionError",
    "compute_content_hash",
    "ingest_markdown_text",
    "read_markdown_essay",
    "render_candidate_markdown",
    "write_candidate_markdown_export",
]
