# Milestone Review: Candidate Markdown Export

## Scope Reviewed

Candidate Markdown export implementation on branch `feat/candidate-markdown-export`.

Reviewed scope:

- `src/diamonddust/storage/__init__.py`
- `src/diamonddust/storage/candidate_markdown.py`
- `tests/unit/test_candidate_markdown_export.py`
- `docs/exec-plans/completed/2026-05-11-candidate-markdown-export.md`

## Product Goal Alignment

Aligned. The implementation adds reviewable candidate Markdown note output from a validated `KnowledgePatch`, filling an MVP output gap without enabling formal vault mutation.

The workflow now supports:

- rendering `CREATE_NOTE` patch operations into candidate Markdown files;
- carrying source refs, relations, unit metadata, and patch metadata into candidate frontmatter;
- writing candidate files and a manifest under `_ai_suggestions/candidate-notes/<patch_id>/`;
- keeping formal target paths visible for review without writing formal files.

## Architecture Boundary Compliance

Compliant.

- Candidate Markdown export lives in the storage adapter layer.
- Domain schemas remain unchanged.
- The exporter uses application patch safety validation rather than duplicating patch rules.
- No provider SDK, UI framework, external service, Obsidian, Notion, MCP, SQLite, or vector dependency was introduced.
- Formal vault apply/revert remains outside this milestone.

## Cohesion Assessment

Good. The module is focused on one responsibility: convert a safe patch into candidate Markdown artifacts and write them only to the AI suggestions area.

## Coupling Assessment

Acceptable. Coupling is limited to existing domain patch/unit/relation/source schemas and the existing patch review safety validator. The storage adapter does not change domain logic.

## Data and Schema Safety

Compliant for this milestone.

- Patch review safety is checked before rendering.
- Unsafe patch IDs are rejected before path construction.
- Exported paths are relative and checked for traversal.
- Files are written under `_ai_suggestions/candidate-notes/<patch_id>/`.
- Formal target paths are represented as metadata but are not written.
- Relation-only patches fail safely because they have no candidate note files to render.

No public domain schema version change was introduced.

## AI Output Boundary

Compliant. The exporter only renders already-validated patch content into AI working artifacts. It does not let LLM output directly overwrite formal notes and does not mark content as accepted or evergreen.

## Tests and Evaluation

Validation run:

- `PYTHONPATH=src python3 -m unittest discover -s tests`: 59 tests passed.
- `python3 -m compileall src tests`: passed.
- `git diff --check`: passed.

Coverage added:

- candidate Markdown rendering from a patch
- patch relation inclusion in rendered candidate notes
- write behavior constrained to `_ai_suggestions`
- no formal target file creation
- unsafe patch ID rejection
- relation-only patch rejection
- AI suggestions target path rejection through patch safety validation

## Dependency and Portability Impact

No production or development dependency was added. The Markdown/frontmatter rendering uses only Python standard-library code.

## Risks

- The frontmatter renderer is intentionally minimal and may need a real serializer if candidate metadata becomes more complex.
- Candidate Markdown format may change when review UI or formal apply/revert is implemented.
- Duplicate target path and existing vault conflict checks are still future work.

## Required Changes Before Continuing

None.

## Optional Improvements

- Persist the raw `KnowledgePatch` alongside candidate notes.
- Add formal vault duplicate ID/path checks before apply/revert.
- Add review report rendering that links patch diff, candidate notes, and rollback instructions.
- Replace minimal frontmatter rendering with a dependency only if fixture evidence justifies it.

## Escalation Requests

None.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked

Candidate Markdown export may be treated as complete for the current post-Gate 7 hardening stage. Follow-ups are not blockers for patch persistence planning.
