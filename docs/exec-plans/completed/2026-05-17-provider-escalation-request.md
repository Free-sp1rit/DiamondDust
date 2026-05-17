# Execution Plan: Provider Integration Escalation Request Draft

## Product Goal

Make the first real-provider approval package reviewable by generating a deterministic escalation request draft from the existing provider readiness decision set, without selecting a provider or enabling real provider integration.

## Current Understanding

DiamondDust now has a provider readiness gate, Markdown readiness report rendering, and a diagnostic CLI command. The next safe step is to create a concise escalation request draft that uses the readiness state as input and follows the project escalation template. This should help the product owner approve or deny high-impact provider decisions explicitly.

## Assumptions

- The first real provider task remains limited to `extract_units`.
- The escalation request draft is review input only.
- The draft does not record user approval.
- The draft must not read API key environment variable values.

## Non-goals

- No real provider integration.
- No provider selection.
- No default model selection.
- No provider SDK dependency.
- No API key value read.
- No network call.
- No prompt package persistence.
- No raw provider output persistence.
- No formal apply, patch acceptance, publication, or provider-side tool execution.
- No persisted approval artifact.

## Proposed Technical Approach

Add an application-level `render_provider_integration_escalation_request_markdown` function that accepts a typed readiness report and returns Markdown using the escalation request shape. Add a `provider-escalation-request` CLI command that reuses the provider readiness decision arguments, assesses readiness, and prints the escalation request draft to stdout.

## Task Breakdown

- [x] Add escalation request renderer for provider readiness reports.
- [x] Reuse provider readiness CLI decision argument parsing.
- [x] Add `provider-escalation-request` CLI command.
- [x] Add tests for blocked draft, decision rendering, invalid input, and no secret disclosure.
- [x] Update docs and repo memory.
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
- `docs/reviews/milestone-reviews/2026-05-17-provider-escalation-request.md`

## Validation Plan

- [x] unit tests
- [x] regression tests
- [x] compile check
- [x] diff check
- [x] architecture scan
- [x] local trial fixture smoke
- [x] provider escalation CLI smoke
- [x] manual review

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This improves first-provider escalation workflow without approving real provider integration.

## Risks

- The escalation draft could be mistaken for user approval if boundaries are unclear.
- The requested decision list may need expansion after the first provider is chosen.
- CLI decision flags remain an input surface, not a durable approval record.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this phase adds no provider SDK, API key read, network call, real cost behavior, prompt persistence, raw output persistence, formal apply, patch acceptance, or publication.

## Definition of Done

- Provider escalation request drafts can be rendered deterministically.
- CLI can print the draft without reading secrets or calling providers.
- Tests cover blocked/ready rendering, invalid input, and no secret disclosure.
- Docs, repo memory, and milestone review are updated.
- Validation passes and the task branch is ready for PR.
