# Execution Plan: DeepSeek Provider Adapter

## Product Goal

Add a DeepSeek provider adapter path for `extract_units` so DiamondDust can
prepare for a future DeepSeek API-key trial while preserving the same
provider-boundary and review-safety rules used for OpenAI.

## Current Understanding

The product owner asked to adapt DiamondDust for DeepSeek API-key calls and
provided the official DeepSeek API documentation. DeepSeek documents an
OpenAI-compatible API shape with `base_url=https://api.deepseek.com`, Python
OpenAI SDK access, and JSON Output through Chat Completions
`response_format={"type": "json_object"}`.

This task implements the adapter and CLI safety path but does not execute a
real DeepSeek call during validation.

## Assumptions

- The first DeepSeek-backed task is limited to `extract_units`.
- DiamondDust may reuse the existing `openai` Python SDK dependency for
  DeepSeek because the official DeepSeek API documents OpenAI SDK-compatible
  access.
- The DeepSeek API key environment variable name should be
  `DIAMONDDUST_DEEPSEEK_API_KEY`.
- No default DeepSeek model is selected by code; model must be explicit.
- JSON mode is used as the provider structured-output mechanism, with
  DiamondDust typed runtime validation remaining authoritative.

## Non-goals

- Do not run a real DeepSeek API call.
- Do not read API key values during tests, preview, dry-run, readiness, or CI.
- Do not persist raw provider request or response bodies.
- Do not add provider-side tools, web search, file search, or MCP calls.
- Do not generate patches, record patch acceptance, formal apply, or publish.
- Do not select or hardcode a default live-call model.

## Proposed Technical Approach

Add a DeepSeek-specific adapter module behind the existing
`ProviderExecutionClient` protocol. The adapter maps
`ProviderExecutionRequest` into an OpenAI-SDK-compatible
`chat.completions.create` request using the DeepSeek base URL and JSON Output
mode. The adapter returns provider-neutral `ProviderResult` envelopes and maps
DeepSeek/OpenAI-compatible errors into `ProviderErrorType`.

Add provider-free CLI commands:

- `deepseek-payload-preview`
- `deepseek-dry-run`
- `deepseek-extract-units`

The extract command remains fail-closed by default and reaches API key reading
or network execution only when explicit real-run approval flags are present.

## Task Breakdown

- [x] Add DeepSeek adapter module and keep SDK imports adapter-local.
- [x] Implement request, response, usage, error, dry-run, and sanitized preview
      mapping.
- [x] Add DeepSeek CLI preview, dry-run, and fail-closed extract path.
- [x] Add fake/mock adapter tests and secret-redaction/no-real-call tests.
- [x] Update provider design/context docs for DeepSeek.
- [x] Run validation and milestone review.

## Likely Files Changed

- `src/diamonddust/ai/adapters/deepseek.py`
- `src/diamonddust/cli.py`
- `tests/unit/test_deepseek_adapter_mapping.py`
- `tests/unit/test_deepseek_adapter_errors.py`
- `tests/unit/test_deepseek_adapter_safety.py`
- `tests/unit/test_cli_entrypoints.py`
- `docs/designs/2026-05-23-deepseek-provider-adapter.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-23-deepseek-provider-adapter.md`

## Validation Plan

- [x] focused DeepSeek adapter mapping tests
- [x] focused DeepSeek adapter error tests
- [x] focused DeepSeek adapter safety tests
- [x] focused CLI tests
- [x] full unit test suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan

## Review Gate Impact

Post-Gate 7 provider integration milestone. This adds a new concrete provider
adapter and a future key-reading/network path, so milestone review is required.

## Risks

- DeepSeek JSON Output mode is weaker than provider-side JSON Schema strict
  validation; typed runtime validation must remain the acceptance boundary.
- DeepSeek response fields may differ from OpenAI SDK response helpers, so fake
  response mapping must cover both mapping-style and object-style responses.
- A DeepSeek extract command could be mistaken for approval to run arbitrary
  real-user essays; CLI output and docs must keep approvals explicit.

## Escalation Needed

Does this require user approval?

- [x] no: the product owner explicitly requested DeepSeek API-key adapter
      planning and implementation. No new dependency is added because the
      existing OpenAI SDK dependency is reused behind the AI adapter boundary.
- [ ] yes

## Definition of Done

- DeepSeek adapter is implemented behind the AI adapter boundary.
- Default DeepSeek paths do not read keys or call providers.
- CLI preview/dry-run are sanitized and provider-free.
- Any real-run path requires explicit flags and an explicit model.
- Tests prove no key reads/network calls by default.
- Milestone review records remaining approval and live-smoke risks.

## Completion Summary

- Added `src/diamonddust/ai/adapters/deepseek.py` with DeepSeek
  OpenAI-compatible Chat Completions mapping, JSON Output mode, usage/error
  mapping, sanitized preview, dry-run, and fail-closed live execution blockers.
- Added `deepseek-payload-preview`, `deepseek-dry-run`, and
  `deepseek-extract-units` CLI entry points.
- The real DeepSeek path remains blocked before key reads or network execution
  unless explicit runtime approval flags, an explicit model, official base URL,
  zero retries, cost limit approval, and prompt/source/schema externalization
  approval are present.
- Validation passed: 259 unit tests, compile check, diff check, local trial
  fixture smoke, and architecture boundary scan with 0 violations.
- No real DeepSeek call was executed, no API key value was read, and no raw
  provider request/response was persisted.
