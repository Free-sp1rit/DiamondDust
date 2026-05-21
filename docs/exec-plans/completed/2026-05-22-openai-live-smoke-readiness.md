# Execution Plan: OpenAI Live Smoke Readiness Package

## Product Goal

Make the first OpenAI live-smoke decision path explicit, reviewable, and
provider-free before any API key value read, prompt/source/schema
externalization, network call, or live provider execution is allowed.

## Current Understanding

The OpenAI adapter is implemented up to pre-live-smoke readiness. The remaining
product-owner decisions before a real call are default model, API key value
reading, real provider and network calls, prompt/source/schema externalization,
manual live-smoke approval, and cost limit.

Existing provider readiness reports cover broad integration decisions, but they
do not yet have a narrow OpenAI live-smoke readiness report that distinguishes
environment variable name approval from key-value reading approval and separates
prompt, source, and schema externalization.

## Assumptions

- The first live-smoke target remains OpenAI.
- The only live-smoke task in scope is `extract_units`.
- Readiness commands must remain diagnostic only.
- Readiness commands must not read API key values, call providers, make network
  requests, or persist artifacts.

## Non-goals

- Do not choose a default model.
- Do not read API key values.
- Do not make network calls or call OpenAI.
- Do not run live smoke.
- Do not externalize prompt/source/schema content.
- Do not persist raw provider request or response bodies.
- Do not record patch acceptance, formal apply, or publish.

## Proposed Technical Approach

Extend the provider decision set with explicit booleans for API key value
reading, source body externalization, schema externalization, one manual live
smoke, and recurring live smoke. Keep missing fields backward-compatible by
defaulting them to `false`.

Add a provider-free OpenAI live-smoke readiness assessment and Markdown renderer
that builds on the existing provider integration readiness gate, then adds
OpenAI-specific and live-smoke-specific blockers. Expose it through a new CLI
command that accepts the same inline or JSON decision inputs.

## Task Breakdown

- [x] Update provider decision data with explicit live-smoke fields.
- [x] Add OpenAI live-smoke readiness assessment and renderer.
- [x] Add CLI command for provider-free live-smoke readiness.
- [x] Add unit and CLI tests for blocked/ready/no-secret behavior.
- [x] Update context docs and milestone review.
- [x] Run validation.

## Likely Files Changed

- `src/diamonddust/application/provider_integration_readiness.py`
- `src/diamonddust/application/__init__.py`
- `src/diamonddust/cli.py`
- `tests/unit/test_provider_integration_readiness.py`
- `tests/unit/test_cli_entrypoints.py`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-22-openai-live-smoke-readiness.md`

## Validation Plan

- [x] focused provider readiness tests
- [x] focused CLI tests
- [x] full unit test suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan

## Review Gate Impact

Post-Gate 7 provider readiness milestone. This touches auth/network/prompt
decision gates but does not execute provider calls.

## Risks

- A readiness report could be mistaken for approval, so it must explicitly say
  it records no approval and performs no call.
- Adding decision fields changes the diagnostic JSON template shape, so tests
  must confirm default parsing remains blocked and backward-compatible.

## Escalation Needed

Does this require user approval?

- [x] no: implementation is provider-free and only clarifies readiness gates.
- [ ] yes

## Definition of Done

- OpenAI live-smoke readiness can be rendered from inline flags or decisions
  JSON without reading API key values.
- The report blocks until all live-smoke-specific approvals are explicit.
- Existing provider-free tests and local trial smoke still pass.
