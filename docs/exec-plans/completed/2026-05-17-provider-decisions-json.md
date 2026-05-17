# Execution Plan: Provider Decisions JSON Input

## Product Goal

Make provider readiness and escalation diagnostics easier to review by allowing CLI commands to load provider integration decision values from a JSON file, without treating that file as an approval record.

## Current Understanding

The readiness and escalation CLI commands currently accept many command-line flags. A JSON input makes the decision package easier to draft, review, and reuse while preserving the existing safety boundaries.

## Assumptions

- The JSON file is input to diagnostics only.
- The JSON file does not record approval by itself.
- The first real provider task remains limited to `extract_units`.
- CLI commands must not read API key environment variable values.

## Non-goals

- No real provider integration.
- No provider selection by default.
- No provider SDK dependency.
- No API key value read.
- No network call.
- No prompt package persistence.
- No raw provider output persistence.
- No formal apply, patch acceptance, publication, or provider-side tool execution.
- No persisted approval artifact.

## Proposed Technical Approach

Add an application-level parser that converts a strict mapping into `ProviderIntegrationDecisionSet`. It should reject unknown fields, accept JSON arrays for `allowed_tasks`, and reuse the dataclass validation. Add a `--decisions-json` option to the readiness and escalation CLI commands. When present, the command loads decisions from that file and does not merge additional CLI decision flags.

## Task Breakdown

- [x] Add strict mapping parser for provider decision sets.
- [x] Add `--decisions-json` to provider readiness and escalation CLI commands.
- [x] Add tests for valid JSON, unknown fields, invalid shape, and no secret disclosure.
- [x] Update README, AI pipeline docs, and repo memory.
- [x] Run validation and prepare PR.

## Likely Files Changed

- `src/diamonddust/application/provider_integration_readiness.py`
- `src/diamonddust/application/__init__.py`
- `src/diamonddust/cli.py`
- `tests/unit/test_provider_integration_readiness.py`
- `tests/unit/test_cli_entrypoints.py`
- `README.md`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-17-provider-decisions-json.md`

## Validation Plan

- [x] unit tests
- [x] regression tests
- [x] compile check
- [x] diff check
- [x] architecture scan
- [x] local trial fixture smoke
- [x] provider decisions JSON CLI smoke
- [x] manual review

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This improves provider approval package usability without approving real provider integration.

## Risks

- A JSON decision file could be mistaken for durable product-owner approval.
- JSON field names may become a user-facing input contract.
- Future durable approval records need a separate schema and storage owner.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this phase adds no provider SDK, API key read, network call, real cost behavior, prompt persistence, raw output persistence, formal apply, patch acceptance, or publication.

## Definition of Done

- Provider decision JSON can be parsed into typed decisions.
- Readiness and escalation CLI commands can load decisions from JSON.
- Tests prove strict field validation and no API key value disclosure.
- Docs, repo memory, and milestone review are updated.
- Validation passes and the task branch is ready for PR.
