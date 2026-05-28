# Execution Plan: Artifact Time UTC+8

## Product Goal

Make newly generated DiamondDust artifact timestamps match the product owner's
UTC+8 expectation so trial users see local-time artifacts instead of UTC `Z`
timestamps.

## Current Understanding

Automatic artifact timestamps are currently produced by CLI defaults and the
trial client using UTC. Persisted artifact renderers accept explicit
`created_at` strings, so this stage should change automatic time generation
without rewriting historical fixtures or typed artifact schemas.

## Assumptions

- Existing historical fixtures and tests with explicit `...Z` timestamps remain
  valid examples of supplied timestamps.
- New automatic artifact timestamps should use ISO 8601 with `+08:00`.
- Auto-generated trial-client run ids should also use a UTC+8 timestamp slug to
  avoid visible 8-hour confusion.

## Non-goals

- Do not migrate historical artifacts.
- Do not change domain schema fields.
- Do not change provider calls, prompt content, patch acceptance, formal apply,
  or publication behavior.
- Do not solve the next core feature design issue in this stage.

## Proposed Technical Approach

Add a single `diamonddust.artifact_time` helper module. Use it from CLI default
`created_at` generation and trial-client feedback/run-id generation. Keep
manual `--created-at` values respected as-is.

## Task Breakdown

- [x] Add UTC+8 artifact time helper.
- [x] Replace automatic UTC timestamp generation in CLI and trial client.
- [x] Add focused tests for timestamp formatting and generated run ids.
- [x] Update docs/context notes.
- [x] Run validation.

## Likely Files Changed

- `src/diamonddust/artifact_time.py`
- `src/diamonddust/cli.py`
- `src/diamonddust/interface/trial_client.py`
- `tests/unit/test_artifact_time.py`
- `tests/unit/test_trial_client.py`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `docs/context/decisions.md`
- `docs/context/project-state.md`

## Validation Plan

- [x] focused artifact time tests
- [x] focused trial client tests
- [x] full unit suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke

## Review Gate Impact

This changes generated artifact metadata semantics, so a short milestone review
is required.

## Risks

- Downstream tools that assumed `Z` may need to tolerate `+08:00`.
- Run id sorting remains safe because the UTC+8 slug keeps compact
  `YYYYMMDDTHHMMSS` order.

## Escalation Needed

Does this require user approval?

- [x] yes: the product owner requested artifact time use UTC+8.

## Definition of Done

- New automatic artifact timestamps are UTC+8 ISO strings.
- Trial-client generated run ids use UTC+8 timestamp slugs.
- Existing explicit timestamp inputs remain accepted.
- Tests pass.
