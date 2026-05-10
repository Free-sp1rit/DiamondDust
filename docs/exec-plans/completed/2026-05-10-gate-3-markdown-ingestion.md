# Execution Plan: Gate 3 Markdown Ingestion

## Product Goal

Implement the minimal Markdown ingestion boundary needed for Gate 3: read Markdown essays without mutation, parse frontmatter when present, create source references, and compute content hashes.

## Current Understanding

Gate 2 introduced typed domain schemas and validation. Gate 3 should add a storage/ingestion adapter that turns a Markdown essay file into typed ingestion metadata while preserving the original essay and keeping formal vault writes out of scope.

## Assumptions

- Gate 3 can be satisfied with standard-library code and does not require a production Markdown or YAML dependency.
- Frontmatter support can start as a deliberate flat subset: simple key/value scalars and string lists.
- The adapter may create `SourceRef` values from the domain core, but the domain core must not import storage code.
- Reading raw essays must be side-effect free.

## Non-goals

- Extracting `KnowledgeUnit` candidates.
- Calling an LLM or adding AI provider behavior.
- Writing to formal vault files, suggestions, reports, SQLite, vector indexes, or Git.
- Supporting full YAML, rich Markdown AST parsing, or Obsidian/Notion-specific syntax.
- Implementing patch generation or patch acceptance.

## Proposed Technical Approach

Add a small Markdown storage adapter under `src/diamonddust/storage/` that:

- reads UTF-8 Markdown files from disk;
- rejects non-Markdown paths;
- parses optional opening frontmatter blocks using a narrow, explicit parser;
- returns an immutable ingestion result containing source id, path, raw content, body content, frontmatter, hashes, and a domain `SourceRef`;
- computes deterministic SHA-256 hashes for raw content and body content;
- never writes to the source path.

## Task Breakdown

- [x] Create the storage adapter package and Markdown ingestion module.
- [x] Add tests for file reading, frontmatter parsing, source refs, hashes, and safe failure.
- [x] Run unit tests, compile checks, and diff whitespace checks.
- [x] Complete milestone review before marking Gate 3 passed.
- [ ] Update repo memory and move this plan to completed when finished.

## Likely Files Changed

- `src/diamonddust/storage/__init__.py`
- `src/diamonddust/storage/markdown.py`
- `tests/unit/test_markdown_ingestion.py`
- `docs/exec-plans/active/2026-05-10-gate-3-markdown-ingestion.md`
- `docs/exec-plans/completed/2026-05-10-gate-3-markdown-ingestion.md`
- `docs/reviews/milestone-reviews/2026-05-10-gate-3-markdown-ingestion.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`

## Validation Plan

- [x] Unit tests for Markdown read behavior.
- [x] Unit tests for frontmatter parsing.
- [x] Unit tests for source ref generation.
- [x] Unit tests for content hash stability.
- [x] Unit tests for malformed input failure.
- [x] Compile check.
- [x] Diff whitespace check.
- [x] Manual review of architecture and AI output boundaries.

## Review Gate Impact

This directly targets Gate 3: Markdown Ingestion.

Gate 3 may be marked passed only if:

- Markdown essay files can be read;
- frontmatter can be parsed;
- source refs can be created;
- content hashes can be computed;
- original essay files are not overwritten;
- source ref preservation blockers are absent.

## Risks

- The minimal frontmatter parser is intentionally not a full YAML implementation.
- Future fixture/golden tests may require richer parsing behavior.
- The source id strategy must remain stable enough for MVP ingestion but may need migration notes if changed later.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because this plan avoids new production dependencies, external services, formal write behavior, public schema changes, and permission changes.

## Definition of Done

- Gate 3 implementation exists in a storage adapter.
- Tests cover success and failure cases.
- Validation passes locally.
- Milestone review records a pass or pass-with-follow-up decision.
- Repo memory is updated with the new gate state, decisions, risks, and follow-ups.

## Completion Summary

Original goal: implement the minimal Markdown ingestion boundary for Gate 3.

Final implementation:

- Added a standard-library Markdown storage adapter.
- Added immutable ingestion metadata with source id, source path, raw content, body content, frontmatter, hashes, line spans, and a domain `SourceRef`.
- Added a deliberate flat frontmatter parser for key/value scalars and string lists.
- Added tests for success paths, hash stability, path safety, source preservation, and malformed input.

Files changed:

- `src/diamonddust/storage/__init__.py`
- `src/diamonddust/storage/markdown.py`
- `tests/unit/test_markdown_ingestion.py`
- `docs/reviews/milestone-reviews/2026-05-10-gate-3-markdown-ingestion.md`
- repo memory docs under `docs/context/`

Public interfaces changed:

- New `diamonddust.storage.markdown` module.
- New `read_markdown_essay`, `ingest_markdown_text`, and `compute_content_hash` functions.
- New `IngestedMarkdownEssay` and `MarkdownIngestionError` types.

Important decisions:

- No production or development dependency was added.
- Frontmatter parsing remains a constrained subset until fixture evidence justifies a full parser.

Known risks:

- Real-world essays may need richer YAML/Markdown parsing.
- Generated source ids may need migration notes if the strategy changes later.

Follow-up tasks:

- Select MVP golden Markdown essays.
- Reconsider parser dependencies after fixture testing.
- Begin Gate 4 AI Extraction Proposal planning.

Validation results:

- `PYTHONPATH=src python3 -m unittest discover -s tests`: 19 tests passed.
- `python3 -m compileall src tests`: passed.
- `git diff --check`: passed.
