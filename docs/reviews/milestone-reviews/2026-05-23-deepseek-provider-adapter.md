# Milestone Review: DeepSeek Provider Adapter

## Scope Reviewed

- DeepSeek OpenAI-compatible adapter boundary.
- DeepSeek CLI payload preview, dry-run, and fail-closed extract path.
- DeepSeek fake/mock request, response, usage, error, and safety tests.
- Provider-free CI/default behavior.

## Product Goal Alignment

This milestone adds DeepSeek as a second concrete provider option for the
`extract_units` task while preserving DiamondDust's typed validation and
review-first artifact boundaries.

## Architecture Boundary Compliance

- The OpenAI SDK import used for DeepSeek compatibility is isolated to
  `src/diamonddust/ai/adapters/deepseek.py`.
- Domain core, application orchestration, storage adapters, formal vault code,
  and artifact contracts do not import DeepSeek/OpenAI SDK types.
- The DeepSeek adapter returns provider-neutral `ProviderResult` envelopes.
- Application orchestration remains responsible for source binding and typed
  extraction validation.
- Storage adapters remain responsible for `_ai_runs` and
  `_ai_suggestions/extractions` persistence when called by the CLI path.

## Cohesion Assessment

The change is cohesive around one provider adapter and its CLI/test surface.
It does not alter formal vault behavior, patch acceptance, publication, or
provider tasks beyond `extract_units`.

## Coupling Assessment

Provider-specific coupling is limited to the DeepSeek adapter and DeepSeek CLI
commands. The adapter reuses the existing OpenAI SDK dependency only because the
official DeepSeek API documents OpenAI SDK-compatible access.

## Data and Schema Safety

DeepSeek JSON Output mode is mapped to `response_format={"type":
"json_object"}`. Since this is weaker than provider-side strict JSON Schema,
DiamondDust typed runtime validation remains the acceptance boundary before any
provider output becomes domain data.

Raw provider request and response bodies are not persisted. Patch generation,
patch acceptance, formal apply, and publication remain disabled.

## AI Output Boundary

Provider output must pass source binding and typed extraction validation before
it becomes a validated extraction artifact. Failed provider responses produce a
failed run result and must not create candidate notes or patches.

## Tests and Evaluation

- Focused DeepSeek adapter and CLI tests: 37 tests passed.
- Full unit test suite: 259 tests passed.
- Compile check: `python3 -m compileall src tests` passed.
- Diff check: `git diff --check` passed.
- Local trial fixture smoke: passed with 12 provider-free artifacts,
  `provider_called: false`, and `formal_write_performed: false`.
- Architecture boundary scan: 0 violations.

## Dependency and Portability Impact

No new dependency was added. The existing `openai` SDK dependency is reused
behind the AI adapter boundary. If DeepSeek's OpenAI-compatible behavior
diverges, replacement remains isolated to the DeepSeek adapter.

## Risks

- DeepSeek JSON Output can return malformed or empty JSON content; the adapter
  maps this to fail-closed `malformed_response`.
- The first DeepSeek live call may require prompt tuning because DeepSeek JSON
  mode is prompt-guided rather than strict-schema enforced.
- The CLI supports future real execution flags; operators must not treat that
  as blanket approval for real user essays or recurring provider runs.

## Required Changes Before Continuing

- Do not run a DeepSeek live call until the product owner explicitly approves
  model, cost limit, API key value reading, real network call, and source
  externalization scope for that run.

## Optional Improvements

- Add a DeepSeek-specific readiness report if the provider becomes a durable
  alternative to OpenAI.
- Add sanitized validation error persistence for live-smoke run logs before
  repeated provider experiments.

## Escalation Requests

None for this implementation milestone. No new dependency was added and no real
provider call was executed.

## Review Decision

- [x] pass with follow-up
- [ ] pass
- [ ] blocked
