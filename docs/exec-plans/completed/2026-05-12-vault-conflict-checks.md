# Execution Plan: Formal Vault Conflict Checks

## Product Goal

Add the first read-only safety preflight for future formal vault apply/revert behavior by detecting path and unit ID conflicts before any formal write can be attempted.

## Current Understanding

DiamondDust can already generate validated `KnowledgePatch` objects and persist review packages in AI working directories. Formal vault mutation is still intentionally absent. The next safe prerequisite is a storage adapter that can inspect a patch against an existing Markdown vault and report conflicts without writing or modifying formal files.

## Assumptions

- Conflict checking can live in the storage adapter layer because it inspects Markdown vault files.
- This task should reuse existing patch review safety validation before inspecting patch operations.
- A minimal frontmatter `id:` reader is sufficient for conflict detection until richer Markdown/YAML parsing is justified.

## Non-goals

- No formal vault apply behavior.
- No revert behavior.
- No Git commit, branch, or rollback automation for vault contents.
- No provider calls.
- No public domain schema change.
- No production dependency changes.

## Proposed Technical Approach

Add a storage module that:

1. validates a `KnowledgePatch` with existing patch review safety checks;
2. gathers `create_note` target paths and unit IDs from the patch;
3. scans formal vault Markdown directories for existing files and frontmatter IDs;
4. returns a typed conflict report with `formal_write_safe` false when conflicts exist.

The scanner must ignore AI working directories and must not create, modify, or delete vault files.

## Task Breakdown

- [x] Add formal vault conflict dataclasses and scanner.
- [x] Export the scanner from the storage package.
- [x] Add unit tests for clean vaults, existing path conflicts, existing ID conflicts, duplicate patch targets, ignored AI directories, and read-only behavior.
- [x] Update data/schema docs and repo memory.
- [x] Run focused and full validation.
- [x] Complete milestone review.

## Likely Files Changed

- `src/diamonddust/storage/formal_vault.py`
- `src/diamonddust/storage/__init__.py`
- `tests/unit/test_formal_vault_conflict_checks.py`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `README.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-12-vault-conflict-checks.md`
- `docs/exec-plans/active/2026-05-12-vault-conflict-checks.md`
- `docs/exec-plans/completed/2026-05-12-vault-conflict-checks.md`

## Validation Plan

- [x] unit tests for conflict scanner behavior
- [x] full unit test discovery
- [x] compile check
- [x] diff whitespace check
- [x] manual review for formal write boundary wording

Validation performed:

- `PYTHONPATH=src python3 -m unittest tests.unit.test_formal_vault_conflict_checks`
- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `python3 -m compileall src tests`
- `git diff --check`

## Review Gate Impact

Post-Gate 7 hardening and Gate 5 follow-up. This introduces a storage safety preflight for future formal vault apply behavior but does not implement formal writes. Milestone review is required because it touches formal write safety and storage adapter behavior.

## Risks

- Minimal frontmatter ID parsing may miss complex YAML forms.
- Path/ID conflicts are necessary but not sufficient for future formal apply safety.
- The scanner should not be mistaken for user acceptance or write authorization.

## Escalation Needed

- [x] no
- [ ] yes

No escalation is needed because this task is read-only, avoids provider calls, avoids formal vault mutation, avoids production dependencies, and does not change public domain schema.

## Definition of Done

- A patch can be checked against a vault root for target path and unit ID conflicts.
- AI working directories are ignored by the scanner.
- Tests prove the scanner does not mutate vault files.
- Docs and repo memory record that this is a preflight only, not formal apply/revert.

## Completion Summary

Implemented read-only formal vault conflict checks, storage exports, tests, data/schema docs, repo memory updates, and milestone review. The implementation does not write formal vault files and does not authorize patch application.
