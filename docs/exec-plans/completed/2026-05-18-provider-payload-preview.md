# Execution Plan: Provider Payload Preview

## Product Goal

Give the product owner a local, provider-free way to inspect the exact provider-neutral execution payload that future concrete provider adapters would receive for `extract_units`.

## Current Understanding

DiamondDust can already ingest Markdown, build a provider-neutral `extract_units` request, render a provider-neutral prompt package with output schema metadata/content, and build a provider-neutral execution payload from a `ProviderExecutionRequest`. The missing usability step is a CLI command that renders that payload for local review before any real provider integration is approved.

## Assumptions

- The preview command may print prompt text, source body text, and output schema content to stdout because the user explicitly invokes it for local review.
- The preview command must not persist prompt/schema/raw provider output artifacts.
- The preview command must not read API key values, call a provider, add SDK dependencies, or approve real provider integration.

## Non-goals

- No real provider integration.
- No provider SDK request mapping.
- No API key reads.
- No network calls.
- No prompt/raw provider output persistence.
- No KnowledgePatch construction from provider output.
- No formal apply, patch acceptance, publication, or provider-backed blog drafting.

## Proposed Technical Approach

Add a `diamonddust provider-payload-preview` CLI command that reads one Markdown essay, builds the existing provider-neutral request and rendered prompt, wraps them in `ProviderExecutionRequest`, builds the existing `ProviderExecutionPayload`, and prints a sorted JSON mapping to stdout.

The command will reuse the existing ingestion, request builder, prompt renderer, and payload builder. It will remain a CLI review surface only; the AI and application boundary types stay provider-neutral and side-effect free.

## Task Breakdown

- [x] Add CLI parser and handler for `provider-payload-preview`.
- [x] Add unit tests that verify parseable payload JSON, safety flags, schema metadata, and no secret leakage.
- [x] Document the command as local review input only.
- [x] Update AI pipeline contract with preview command boundaries.
- [x] Update repo memory and milestone review.
- [x] Run focused and full validation.

## Likely Files Changed

- `src/diamonddust/cli.py`
- `tests/unit/test_cli_entrypoints.py`
- `README.md`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-18-provider-payload-preview.md`
- `docs/exec-plans/active/2026-05-18-provider-payload-preview.md`

## Validation Plan

- [x] focused CLI and provider payload unit tests
- [x] full unit test suite
- [x] compile check
- [x] whitespace diff check
- [x] local trial fixture smoke
- [x] architecture violation scan

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This touches provider adapter boundary review because it exposes prompt/schema payload review, but does not approve or implement real provider calls.

## Risks

- The preview JSON includes prompt text and essay body text, so docs must clearly say it is printed for local review only and not persisted by default.
- A preview command could be mistaken for provider execution unless safety flags and docs remain explicit.
- Future provider-specific SDK payload mapping may still need a separate design and escalation.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this command does not add dependencies, read keys, call networks, persist prompt/raw provider output, or change formal vault behavior.

## Definition of Done

- `provider-payload-preview` prints a provider-neutral payload JSON for one Markdown essay.
- Output includes the existing safety flags showing real provider calls, tool calls, and raw output persistence are disabled.
- Tests prove the command does not leak API key environment variable values.
- Docs and memory state preserve the boundary that this is review input only.
- Full validation passes.
