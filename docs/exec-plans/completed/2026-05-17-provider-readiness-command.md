# Execution Plan: Provider Readiness CLI Command

## Product Goal

Make the provider integration readiness report inspectable from the DiamondDust CLI so the product owner can prepare first-provider escalation decisions without adding a provider SDK, reading API keys, or making network calls.

## Current Understanding

The application layer can assess provider integration readiness and render a deterministic Markdown report. The next safe step is to expose that report through a read-only CLI command. This improves usability for planning and escalation while keeping real provider integration out of scope.

## Assumptions

- The first real provider task remains limited to `extract_units`.
- The command is a reporting tool, not an approval recorder.
- The command may accept decision values and boolean approval flags as CLI arguments.
- The command must not read API key environment variable values.

## Non-goals

- No real provider integration.
- No provider SDK dependency.
- No API key value read.
- No network call.
- No prompt package persistence.
- No raw provider output persistence.
- No formal apply, patch acceptance, publication, or provider-side tool execution.
- No persisted readiness artifact.

## Proposed Technical Approach

Add a `provider-readiness-report` CLI command that builds a `ProviderIntegrationDecisionSet` from optional CLI arguments, assesses readiness, and prints the existing Markdown readiness report to stdout. The command should return success when rendering succeeds, even if the report status is `blocked`, because blocked readiness is a valid diagnostic outcome.

## Task Breakdown

- [x] Add CLI parser for provider readiness decisions.
- [x] Build a decision set without reading secrets or environment values.
- [x] Render the readiness Markdown report to stdout.
- [x] Add CLI tests for help, blocked default output, ready output, and secret non-disclosure.
- [x] Update docs and repo memory.
- [x] Run validation and prepare PR.

## Likely Files Changed

- `src/diamonddust/cli.py`
- `tests/unit/test_cli_entrypoints.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-17-provider-readiness-command.md`

## Validation Plan

- [x] unit tests
- [x] regression tests
- [x] compile check
- [x] diff check
- [x] architecture scan
- [x] local trial fixture smoke
- [x] manual review

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This improves first-provider escalation workflow without approving real provider integration.

## Risks

- CLI approval flags could be misread as durable product-owner approval unless the report boundaries remain explicit.
- The argument surface may need revision after the first provider is chosen.
- A blocked report returning exit code 0 may not serve future CI gating without an explicit follow-up option.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this phase adds no provider SDK, API key read, network call, real cost behavior, prompt persistence, raw output persistence, formal apply, patch acceptance, or publication.

## Definition of Done

- `diamonddust provider-readiness-report` prints a deterministic readiness report.
- The default command reports blocked readiness without failing command execution.
- Tests prove API key environment values are not rendered.
- Docs, repo memory, and milestone review are updated.
- Validation passes and the task branch is ready for PR.
