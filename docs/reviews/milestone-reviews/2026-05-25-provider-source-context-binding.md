# Milestone Review: Provider Source Context Binding Hardening

## Scope Reviewed

Reviewed the provider-neutral extraction prompt, application provider handoff,
source binding tests, AI pipeline contract, and durable project memory updates.

## Product Goal Alignment

The change directly addresses DeepSeek live-probe feedback: the provider call
path reached the provider, but validation failed on top-level `source_input_id`.
The fix improves retry readiness without broadening provider permissions.

## Architecture Boundary Compliance

Pass. Provider-specific code remains isolated in AI adapter modules. The source
context binding change is in the application provider handoff, where request
context and provider response validation meet. Domain core, storage adapters,
formal vault code, and CLI provider safety valves are not coupled to DeepSeek or
OpenAI SDK types.

## Cohesion Assessment

Pass. Prompt wording changes remain in the prompt renderer. Runtime source
binding remains in `provider_extraction`, beside typed validation handoff logic.
Tests cover prompt text, legacy provider boundary, and prompt-aware
orchestration.

## Coupling Assessment

Pass with follow-up. The binding helper assumes `extract_units` request payloads
carry `source_input_id`, matching current v0 scope. Future provider tasks should
define task-specific binding rules instead of reusing this behavior blindly.

## Data and Schema Safety

Pass. No public schema version changes were made. The top-level provider output
`source_input_id` is treated as request-owned lineage and is bound before typed
validation. Unit `source_refs` are not rewritten; wrong source references still
fail closed and do not produce validated extraction artifacts.

## AI Output Boundary

Pass. Provider output still must pass typed runtime validation before becoming
domain data. The adapter still does not construct `KnowledgeUnit`, `Relation`,
or `KnowledgePatch`, and no formal vault write, patch acceptance, publication,
provider-side tool use, or raw provider request/response persistence is enabled.

## Tests and Evaluation

- `PYTHONPATH=src .venv/bin/python -m unittest tests.unit.test_prompt_renderer tests.unit.test_provider_boundary tests.unit.test_provider_extraction_orchestrator`: 23 tests passed.
- `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests`: 261 tests passed.
- `.venv/bin/python -m compileall src tests`: passed.
- `git diff --check`: passed.
- `PYTHONPATH=src .venv/bin/python -m diamonddust local-trial-fixture`: passed; provider_called false; formal_write_performed false.
- Architecture boundary scan: 0 violations.

## Dependency and Portability Impact

No dependency was added or changed. No provider SDK import location changed.

## Risks

- The run-log `output_hash` reflects the validation payload after top-level
  source binding, not a persisted raw provider response body.
- JSON-mode providers may still produce invalid source refs or incomplete
  domain fields.
- Prompt wording is stronger but not a substitute for typed validation.

## Required Changes Before Continuing

None.

## Optional Improvements

- Add a future hash-only provider raw structured-output trace field if replay or
  debugging requires comparing provider output hash against validation payload
  hash.
- Re-run one controlled DeepSeek fixture smoke to confirm whether the prompt and
  binding changes are enough for a validated extraction artifact.

## Escalation Requests

None. No new dependency, key-read behavior, provider permission, storage format,
formal write, patch acceptance, or publication behavior was introduced.

## Review Decision

- [x] pass
- [ ] pass with follow-up
- [ ] blocked
