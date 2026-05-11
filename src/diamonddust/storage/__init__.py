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
from diamonddust.storage.review_report import (
    AI_PATCH_REVIEW_REPORTS_DIR,
    PatchReviewReport,
    ReviewReportError,
    render_patch_review_report,
    write_patch_review_report,
)

__all__ = [
    "AI_CANDIDATE_NOTES_DIR",
    "AI_PATCH_REVIEW_REPORTS_DIR",
    "CandidateMarkdownError",
    "CandidateMarkdownExport",
    "CandidateMarkdownFile",
    "CandidateMarkdownManifest",
    "FrontmatterValue",
    "IngestedMarkdownEssay",
    "MarkdownIngestionError",
    "PatchReviewReport",
    "ReviewReportError",
    "compute_content_hash",
    "ingest_markdown_text",
    "read_markdown_essay",
    "render_candidate_markdown",
    "render_patch_review_report",
    "write_candidate_markdown_export",
    "write_patch_review_report",
]
