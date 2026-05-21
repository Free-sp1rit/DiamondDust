# Execution Plan: First OpenAI Adapter Implementation, Pre-Live-Smoke Ready

## Product Goal

Implement the OpenAI provider adapter boundary up to a provider-free,
pre-live-smoke ready state so the product owner can later inject an API key and
separately approve a controlled live smoke run.

## Current Understanding

The product owner approved and this stage implemented OpenAI adapter code,
dependency file changes, CI dependency installation behavior, provider
request/response/error mapping, structured output handling, CLI payload preview,
dry-run behavior, real-run safety valves, fake/mock SDK tests, secret redaction
tests, no-real-call-by-default tests, and provider-free CI protections.

This stage does not approve API key value reads, real provider calls, network
calls, live smoke, actual prompt/source/schema externalization to a provider,
raw provider output persistence, patch acceptance, formal apply, publication,
or default model selection. Request mapping code and sanitized payload preview
are approved as provider-free implementation work.

## Assumptions

- The first provider is `openai`.
- The selected SDK dependency is `openai`.
- The only provider-backed task in scope is `extract_units`.
- A future live run must require an explicit model argument; no default live
  model may be hardcoded.
- The adapter can be tested with fake or mocked SDK clients without API key
  values or network calls.

## Non-goals

- Do not read API key values.
- Do not make network calls or call OpenAI.
- Do not run live smoke.
- Do not choose or hardcode a default live-call model.
- Do not persist raw provider request or response bodies.
- Do not externalize prompt/source/schema content to a provider.
- Do not instantiate a real OpenAI client in preview, dry-run, tests,
  readiness, or CI.
- Do not generate patches, write candidate notes, formal apply, record patch
  acceptance, or publish.
- Do not add provider tasks beyond `extract_units`.

## Proposed Technical Approach

Add an OpenAI-specific adapter module behind the existing provider-neutral
`ProviderExecutionClient` protocol. Keep OpenAI SDK imports isolated to the AI
adapter package and map all SDK-specific exceptions/responses into
`ProviderResult`, `ProviderResponse`, `ProviderError`, and `ProviderErrorType`.

The adapter should be constructed with explicit runtime configuration and a
mockable SDK client boundary. In this pre-live-smoke stage, CLI preview and
dry-run paths must build and display sanitized provider-facing shapes without
reading API key values or making network calls. Any real-run entrypoint must
fail closed before key reading or network execution because real provider calls
and live smoke are not approved. Real OpenAI client construction must remain
gated behind future live-smoke approval.

## Files To Modify

- `pyproject.toml`
- `.github/workflows/ci.yml`
- `src/diamonddust/ai/adapters/__init__.py`
- `src/diamonddust/ai/adapters/openai.py`
- `src/diamonddust/cli.py`
- `tests/unit/test_openai_adapter_mapping.py`
- `tests/unit/test_openai_adapter_errors.py`
- `tests/unit/test_openai_adapter_safety.py`
- `tests/unit/test_cli_entrypoints.py`
- `tests/unit/test_ci_workflow.py`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/reviews/milestone-reviews/<date>-openai-adapter-pre-live-smoke.md`

## Dependency File Changes

- Add `openai` to `pyproject.toml` project dependencies.
- Do not add any other provider SDK.
- Do not add a lockfile unless the project adopts lockfile policy separately.
- CI should continue installing the wheel normally and must not require API key
  secrets.

## Adapter Module Shape

- `src/diamonddust/ai/adapters/openai.py`
- Proposed public surface:
  - `OpenAIAdapterConfig`
  - `OpenAIExecutionClient`
  - `OpenAIAdapterError`
  - helper functions for request mapping, response extraction, usage mapping,
    error normalization, and secret-safe message sanitization
- Input:
  - `ProviderExecutionRequest`
- Internal mapping:
  - build `ProviderExecutionPayload`
  - map messages and output schema into the OpenAI SDK request shape
  - set provider-side tools disabled
  - set timeout to `30`
  - set retries to `0`
- Output:
  - `ProviderResult` with `ProviderResponse` on structured success
  - `ProviderResult` with `ProviderError` on all mapped failures
- Safety:
  - refuse execution unless `real_provider_calls_enabled` is true
  - do not read environment variables in the adapter during this stage
  - do not instantiate a real OpenAI client in preview, dry-run, tests,
    readiness, or CI
  - gate any future real OpenAI client construction behind live-smoke approval
  - accept only injected/mockable SDK client objects in tests
  - never return SDK-specific types outside the adapter module

## CLI Safety Commands / Flags

Extend CLI in a provider-free way:

- Keep existing `provider-payload-preview` provider-free.
- Add or extend an OpenAI-specific preview command that prints sanitized
  provider request mapping without API key value reads or network calls.
- Add dry-run behavior that verifies configuration shape and safety gates,
  returns `provider_called: false`, and refuses key reads.
- Add a future real-run command or flag shape behind a fail-closed safety valve.
  In this stage it must stop before API key value reading or network execution
  because live smoke is not approved.

Required flag semantics:

- model argument must be explicit for any future real-run path.
- API key env var name may be accepted as a name only.
- no command may print API key values.
- no command may print raw provider response bodies.

## Tests

- Unit tests for request mapping from `ProviderExecutionPayload` to OpenAI SDK
  request shape using fake SDK objects.
- Unit tests for response mapping into `ProviderResult`.
- Unit tests for every `ProviderErrorType` mapping.
- Secret redaction tests proving key-like values are not printed or persisted.
- Safety tests proving adapter refuses execution when
  `real_provider_calls_enabled` is false.
- Tests proving preview and dry-run commands do not read env vars, API key
  values, or make network calls.
- Tests proving provider-specific SDK types do not leak into domain,
  application, storage, formal vault, or artifact contracts.
- `tests/unit/test_ci_workflow.py` should be changed only where CI policy is
  directly testable; otherwise provider-free default behavior should be covered
  by CLI/provider safety tests.
- Existing source binding and typed validation tests must keep passing.

## CI Behavior

- Default CI must remain provider-free.
- CI must not require `DIAMONDDUST_OPENAI_API_KEY`.
- CI must not read API key values.
- CI must not call OpenAI or any provider.
- CI should run fake/mock adapter tests, CLI preview/dry-run tests, unit tests,
  compile checks, whitespace checks, and local trial fixture smoke.
- Live smoke must not run in ordinary PR or push CI.

## Explicit Non-Approvals

- `default_model`: not approved.
- API key value reading: not approved.
- Real provider calls: not approved.
- Real network calls: not approved.
- Live smoke: not approved.
- Recurring live smoke: not approved.
- Prompt/source/schema externalization: not approved.
- Raw provider request/response persistence: not approved.
- Full raw output retention: not approved.
- Patch acceptance: not approved.
- Formal apply: not approved.
- Publication: not approved.
- Provider tasks beyond `extract_units`: not approved.

## Rollback Plan

- Remove `src/diamonddust/ai/adapters/openai.py` and adapter package exports.
- Remove OpenAI adapter tests.
- Revert CLI OpenAI preview/dry-run/safety-valve additions.
- Remove `openai` from `pyproject.toml`.
- Re-run full unit tests, compile check, diff check, local trial fixture smoke,
  and architecture scan.
- Confirm no generated artifacts, formal vault files, or raw provider outputs
  were written.

## Task Breakdown

- [x] Update dependency metadata with the OpenAI SDK.
- [x] Add OpenAI adapter module and keep SDK imports adapter-local.
- [x] Implement provider request mapping with structured-output configuration.
- [x] Implement response, usage, and error mapping into provider-neutral
  envelopes.
- [x] Add fail-closed safety checks before key reads or network execution.
- [x] Add provider-free CLI preview/dry-run/safety-valve behavior.
- [x] Add fake/mock SDK unit tests and secret redaction tests.
- [x] Add CI/provider-free regression checks.
- [x] Run validation and milestone review.

## Validation Plan

- [x] focused OpenAI adapter mapping tests
- [x] focused OpenAI adapter error tests
- [x] focused OpenAI adapter safety tests
- [x] focused CLI tests
- [x] full unit test suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan
- [x] milestone review

## Review Gate Impact

Post-Gate 7 provider integration milestone. This introduces a production
dependency and concrete provider adapter code, so milestone review is required
before the stage is marked complete.

## Risks

- The OpenAI SDK may implicitly read environment variables if adapter
  construction is not controlled.
- SDK object types could leak outside the adapter module.
- CLI real-run flags could be mistaken for live-smoke approval.
- Provider structured-output helpers may vary by model, and the default model
  remains pending.
- Dependency installation may expose packaging or CI issues.

## Escalation Needed

Does this require user approval?

- [x] no: implementation stayed inside the approved pre-live-smoke boundary.
- [ ] yes: this plan must be explicitly approved before code implementation starts.

Already approved for this stage:

- dependency file changes and dependency installation
- OpenAI official SDK as the selected provider SDK
- actual adapter implementation up to pre-live-smoke ready
- fake/mock tests and provider-free CI

Still requiring separate approval:

- default model
- API key value reading
- real provider calls and network calls
- live smoke
- prompt/source/schema externalization
- raw provider output persistence
- cost limit for future live run

## Definition of Done

- The product owner approved this plan before implementation.
- Code implementation started only after approval.
- The adapter is importable and testable with fake/mock
  SDK clients.
- Default CI remains provider-free and secret-free.
- The adapter cannot call OpenAI unless future live-smoke approval unlocks key
  reading and real network execution.
