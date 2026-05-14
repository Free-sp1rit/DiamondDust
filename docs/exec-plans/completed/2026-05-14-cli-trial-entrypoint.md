# Execution Plan: CLI Trial Entrypoint

## Product Goal

Move DiamondDust closer to user trial readiness by making the local trial CLI easier to invoke through standard Python package entrypoints.

## Current Understanding

The current local trial can be run with `PYTHONPATH=src python3 -m diamonddust.cli local-trial ...`. That is workable for development, but trial users should have a clearer path toward `python3 -m diamonddust` and an installable `diamonddust` console script.

## Assumptions

- A minimal `pyproject.toml` is acceptable if it adds no runtime dependencies.
- The console script should point to the existing `diamonddust.cli:main`.
- `python3 -m diamonddust` should delegate to the same CLI.
- This stage should keep local trial behavior unchanged except invocation ergonomics.

## Non-goals

- No provider adapter.
- No formal vault apply/revert execution.
- No publishing.
- No UI.
- No CI.
- No production runtime dependency additions.

## Proposed Technical Approach

Add minimal package metadata in `pyproject.toml`, expose a `diamonddust` console script, and add `src/diamonddust/__main__.py` so module execution uses the same CLI. Update README and local trial guides to show the installable command while preserving the development fallback. Add tests for entrypoint metadata and module CLI help.

## Task Breakdown

- [x] Add minimal package metadata and console script.
- [x] Add `python3 -m diamonddust` module entrypoint.
- [x] Update local trial README and guides.
- [x] Add tests for entrypoint metadata and module help.
- [x] Update repo memory and milestone review.
- [x] Run focused and full validation.

## Likely Files Changed

- `pyproject.toml`
- `src/diamonddust/__main__.py`
- `README.md`
- `docs/guides/local-trial-user-feedback.md`
- `docs/guides/local-trial-extraction-json.md`
- `tests/unit/test_cli_entrypoints.py`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-14-cli-trial-entrypoint.md`
- `docs/exec-plans/active/2026-05-14-cli-trial-entrypoint.md`
- `docs/exec-plans/completed/2026-05-14-cli-trial-entrypoint.md`

## Validation Plan

- [x] entrypoint metadata tests
- [x] module CLI help test
- [x] full unit test discovery
- [x] compile check
- [x] diff whitespace check

## Completion Summary

Added minimal Python package metadata, the `diamonddust` console script mapping, `python3 -m diamonddust` support, updated local trial docs/guides, added entrypoint tests, updated repo memory, and completed milestone review. This stage added no runtime dependency, provider call, formal vault write, publication behavior, UI, or CI.

## Review Gate Impact

Post-Gate 7 usability hardening. Milestone review is appropriate because this changes project packaging/configuration and user-facing CLI invocation.

## Risks

- Packaging metadata can drift from docs if future CLI names change.
- Editable install behavior depends on the user's Python packaging tools.
- The installable CLI improves ergonomics but does not yet provide CI or real provider extraction.

## Escalation Needed

- [x] no
- [ ] yes

No escalation is needed because this task adds no runtime dependencies, provider calls, formal writes, publishing, or public domain schema changes.

## Definition of Done

- `python3 -m diamonddust --help` works with `PYTHONPATH=src`.
- `pyproject.toml` exposes `diamonddust = "diamonddust.cli:main"`.
- README and local trial guides mention the installable command and development fallback.
- Tests pass and repo memory reflects the new trial entrypoint.
