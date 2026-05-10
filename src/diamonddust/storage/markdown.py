"""Markdown ingestion adapter for DiamondDust Gate 3."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
from types import MappingProxyType
from typing import Mapping, TypeAlias

from diamonddust.domain.schema import SourceOrigin, SourceRef

FrontmatterValue: TypeAlias = str | int | float | bool | tuple[str, ...] | None

_MARKDOWN_SUFFIXES = {".md", ".markdown"}
_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
_INT_PATTERN = re.compile(r"^[+-]?\d+$")
_FLOAT_PATTERN = re.compile(
    r"^[+-]?(?:(?:\d+\.\d*)|(?:\d*\.\d+))(?:[eE][+-]?\d+)?$"
)
_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


class MarkdownIngestionError(ValueError):
    """Raised when a Markdown essay cannot be ingested safely."""


@dataclass(frozen=True)
class IngestedMarkdownEssay:
    source_id: str
    source_path: str
    raw_content: str
    body: str
    frontmatter: Mapping[str, FrontmatterValue]
    raw_content_hash: str
    body_content_hash: str
    body_line_start: int
    body_line_end: int
    source_ref: SourceRef


def read_markdown_essay(path: str | Path, root: str | Path | None = None) -> IngestedMarkdownEssay:
    essay_path = Path(path)
    _require_markdown_path(essay_path)
    source_path = _source_path_for(essay_path, root)
    try:
        raw_content = essay_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MarkdownIngestionError(f"cannot read Markdown essay: {essay_path}") from exc

    return ingest_markdown_text(
        raw_content,
        source_path=source_path,
        source_name=essay_path.stem,
    )


def ingest_markdown_text(
    raw_content: str,
    *,
    source_path: str,
    source_name: str | None = None,
) -> IngestedMarkdownEssay:
    if not isinstance(raw_content, str):
        raise MarkdownIngestionError("raw_content must be a string")
    if not isinstance(source_path, str) or not source_path.strip():
        raise MarkdownIngestionError("source_path must be a non-empty string")

    frontmatter, body, body_line_start = _split_frontmatter(raw_content)
    raw_content_hash = compute_content_hash(raw_content)
    body_content_hash = compute_content_hash(body)
    body_line_end = _line_end(body, body_line_start)
    source_id = _source_id(frontmatter, source_name or Path(source_path).stem, raw_content_hash)
    source_ref = SourceRef(
        source_id=source_id,
        source_path=source_path,
        source_span=_source_span(body_line_start, body_line_end),
        origin=SourceOrigin.USER_TEXT,
        line_start=body_line_start,
        line_end=body_line_end,
        content_hash=body_content_hash,
        is_approximate=False,
    )

    return IngestedMarkdownEssay(
        source_id=source_id,
        source_path=source_path,
        raw_content=raw_content,
        body=body,
        frontmatter=MappingProxyType(dict(frontmatter)),
        raw_content_hash=raw_content_hash,
        body_content_hash=body_content_hash,
        body_line_start=body_line_start,
        body_line_end=body_line_end,
        source_ref=source_ref,
    )


def compute_content_hash(content: str) -> str:
    if not isinstance(content, str):
        raise MarkdownIngestionError("content must be a string")
    return "sha256:" + sha256(content.encode("utf-8")).hexdigest()


def _require_markdown_path(path: Path) -> None:
    if path.suffix.lower() not in _MARKDOWN_SUFFIXES:
        raise MarkdownIngestionError("Markdown ingestion only accepts .md or .markdown files")


def _source_path_for(path: Path, root: str | Path | None) -> str:
    if root is None:
        return path.as_posix()

    resolved_path = path.resolve()
    resolved_root = Path(root).resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError as exc:
        raise MarkdownIngestionError("Markdown essay path must be inside root") from exc


def _split_frontmatter(raw_content: str) -> tuple[dict[str, FrontmatterValue], str, int]:
    lines = raw_content.splitlines(keepends=True)
    if not lines or _strip_newline(lines[0]) != "---":
        return {}, raw_content, 1

    for index, line in enumerate(lines[1:], start=1):
        if _strip_newline(line) == "---":
            frontmatter_text = "".join(lines[1:index])
            body = "".join(lines[index + 1 :])
            return _parse_frontmatter(frontmatter_text), body, index + 2

    raise MarkdownIngestionError("frontmatter block is not closed")


def _parse_frontmatter(frontmatter_text: str) -> dict[str, FrontmatterValue]:
    result: dict[str, FrontmatterValue] = {}
    current_list_key: str | None = None

    for raw_line in frontmatter_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if line[:1].isspace():
            _append_list_item(result, current_list_key, stripped)
            continue

        key, separator, raw_value = line.partition(":")
        if separator != ":":
            raise MarkdownIngestionError(f"malformed frontmatter line: {line}")

        key = key.strip()
        if not _KEY_PATTERN.match(key):
            raise MarkdownIngestionError(f"unsupported frontmatter key: {key}")
        if key in result:
            raise MarkdownIngestionError(f"duplicate frontmatter key: {key}")

        value = raw_value.strip()
        if value:
            result[key] = _parse_scalar(value)
            current_list_key = None
        else:
            result[key] = None
            current_list_key = key

    return result


def _append_list_item(
    frontmatter: dict[str, FrontmatterValue],
    current_list_key: str | None,
    stripped_line: str,
) -> None:
    if current_list_key is None or not stripped_line.startswith("- "):
        raise MarkdownIngestionError("frontmatter only supports flat key/value pairs and lists")

    item = _parse_list_string(stripped_line[2:].strip())
    current_value = frontmatter[current_list_key]
    if current_value is None:
        frontmatter[current_list_key] = (item,)
        return
    if isinstance(current_value, tuple):
        frontmatter[current_list_key] = current_value + (item,)
        return
    raise MarkdownIngestionError("frontmatter list item cannot follow a scalar value")


def _parse_scalar(value: str) -> FrontmatterValue:
    lowered = value.lower()
    if lowered in {"null", "none", "~"}:
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _INT_PATTERN.match(value):
        return int(value)
    if _FLOAT_PATTERN.match(value):
        return float(value)
    return _strip_quotes(value)


def _parse_list_string(value: str) -> str:
    if not value:
        raise MarkdownIngestionError("frontmatter list items must be non-empty strings")
    parsed = _strip_quotes(value)
    if not parsed:
        raise MarkdownIngestionError("frontmatter list items must be non-empty strings")
    return parsed


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _strip_newline(line: str) -> str:
    return line.rstrip("\r\n")


def _line_end(body: str, body_line_start: int) -> int:
    line_count = len(body.splitlines())
    if line_count == 0:
        return body_line_start
    return body_line_start + line_count - 1


def _source_span(line_start: int, line_end: int) -> str:
    if line_start == line_end:
        return f"line {line_start}"
    return f"lines {line_start}-{line_end}"


def _source_id(
    frontmatter: Mapping[str, FrontmatterValue],
    source_name: str,
    raw_content_hash: str,
) -> str:
    frontmatter_id = frontmatter.get("id")
    if isinstance(frontmatter_id, str) and frontmatter_id.strip():
        return frontmatter_id

    slug = _slugify(source_name)
    short_hash = raw_content_hash.removeprefix("sha256:")[:12]
    return f"raw_essay_{slug}_{short_hash}"


def _slugify(value: str) -> str:
    slug = _SLUG_PATTERN.sub("_", value.lower()).strip("_")
    return slug or "untitled"
