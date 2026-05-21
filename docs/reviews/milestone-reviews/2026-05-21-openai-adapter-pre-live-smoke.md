# Milestone Review: OpenAI Adapter Pre-Live-Smoke

## Scope Reviewed

OpenAI adapter boundary implementation for the approved pre-live-smoke stage:
dependency metadata, adapter-local SDK boundary, request/response/usage/error
mapping, sanitized CLI payload preview, provider-free dry-run, fail-closed
future real-run guard, fake/mock SDK tests, secret redaction tests, no-real-call
default tests, and CI provider-free behavior.

## Product Goal Alignment

The stage prepares DiamondDust for an owner-controlled OpenAI `extract_units`
live smoke without approving or performing the live smoke. The implementation
keeps default model selection, API key value reading, prompt/source/schema
externalization, network calls, real provider calls, raw output persistence,
patch acceptance, formal apply, and publication out of scope.

## Architecture Boundary Compliance

The concrete OpenAI SDK import is isolated to
`src/diamonddust/ai/adapters/openai.py`. Domain core, application
orchestration, storage adapters, formal vault code, and artifact contracts do
not import OpenAI SDK types. The adapter returns provider-neutral
`ProviderResult` envelopes and does not persist artifacts or construct
`KnowledgeUnit`, `Relation`, or `KnowledgePatch` objects.

## Cohesion Assessment

The adapter module owns OpenAI-specific request mapping, response extraction,
usage mapping, error normalization, and secret-safe message sanitization. CLI
commands own human-triggered preview/dry-run/guard behavior. Existing
application and storage layers remain provider-neutral.

## Coupling Assessment

The new production dependency is isolated behind the AI adapter package. Tests
use fake response/client objects and pure mapping helpers, so CI does not need
API key secrets and does not call the provider.

## Data and Schema Safety

Structured-output request mapping uses the rendered prompt's existing
`extract_units` schema package. Sanitized preview emits hashes and identifiers,
not raw prompt/source/schema bodies. Raw provider request and response bodies
are not persisted.

## AI Output Boundary

The adapter does not turn provider output into domain data. Successful output is
only mapped into `ProviderResponse`; application source binding and typed
extraction validation remain the required gates before any output can affect
patch generation.

## Tests and Evaluation

- 231 unit tests passed.
- `python3 -m compileall src tests` passed.
- `git diff --check` passed.
- `PYTHONPATH=src python3 -m diamonddust local-trial-fixture` passed and
  reported `formal_write_performed: false` and `provider_called: false`.
- Architecture scan reported `violations: 0`.

## Dependency and Portability Impact

`openai>=1.0.0` is now a production dependency selected by the product owner.
CI wheel installation now installs project dependencies so `pip check` can
remain meaningful. Default CI remains provider-free and does not require
`DIAMONDDUST_OPENAI_API_KEY`.

## Risks

- The future live path still requires model, key-reading, prompt/source/schema
  externalization, network-call, live-smoke, and cost-limit approvals.
- The OpenAI Responses structured-output payload shape should be verified
  against the installed SDK before live smoke.
- The current architecture scan only checks domain-core forbidden imports, so
  adapter-local SDK isolation is additionally guarded by unit tests.

## Required Changes Before Continuing

- None for the pre-live-smoke implementation boundary.

## Optional Improvements

- Add a separate owner-approved live-smoke plan once the remaining decisions are
  explicit.
- Add a provider-specific SDK compatibility check after dependency installation
  is confirmed in remote CI.

## Escalation Requests

- None for this stage.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked

