# Milestone Review: Extraction Unit ID And Enum Prompt Hardening

## Scope Reviewed

Reviewed the provider-neutral extraction prompt, generated extraction output
schema guidance, extraction validation diagnostics, tests, AI pipeline contract,
repo memory, and controlled DeepSeek fixture smoke results.

## Product Goal Alignment

The change addresses the next DeepSeek fixture smoke failure after source
context binding: generated output omitted required candidate identity and then
emitted typed fields in a non-conforming shape. The implementation improves
provider guidance and diagnostics without weakening typed validation.

## Architecture Boundary Compliance

Pass. Changes remain in the provider-neutral AI prompt/schema/validation
boundary and docs. No provider SDK import moved outside adapter modules. No
storage, formal vault, or patch-acceptance behavior was changed.

## Cohesion Assessment

Pass. Prompt wording and request-derived `unit_id_prefix` live in the prompt
renderer. Schema guidance lives in the generated output schema. Indexed
validation diagnostics live in extraction validation.

## Coupling Assessment

Pass with follow-up. The id-prefix guidance depends only on request
`source_input_id`, not provider-specific behavior. DeepSeek-specific learning is
recorded as open context rather than hard-coding DeepSeek repair behavior into
domain or storage layers.

## Data and Schema Safety

Pass. No schema version change was made because runtime acceptance remains the
same: required fields and enum/string types were already required. The schema
description and prompt guidance became clearer, while invalid provider output
still fails closed.

## AI Output Boundary

Pass. Provider output still must pass typed validation before becoming domain
data. Missing ids, non-string enum fields, and non-array `unit_candidates`
continue to fail closed. No raw provider request/response body was persisted.

## Tests and Evaluation

- `PYTHONPATH=src .venv/bin/python -m unittest tests.unit.test_prompt_renderer tests.unit.test_extraction_output_schema tests.unit.test_ai_extraction`: 20 tests passed.
- `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests`: 262 tests passed.
- `.venv/bin/python -m compileall src tests`: passed.
- `git diff --check`: passed.
- `PYTHONPATH=src .venv/bin/python -m diamonddust local-trial-fixture`: passed; provider_called false; formal_write_performed false.
- Architecture boundary scan: 0 violations.
- Controlled DeepSeek fixture smoke after id hardening reached provider request `b600e04c-fc7d-4e20-abff-36c10817a67f` and failed typed validation with `unit_candidates[0]: type must be a string`.
- Controlled DeepSeek fixture smoke after enum-string hardening reached provider request `76ca1ebc-52df-4db8-8b2a-b740488cfe35` and failed typed validation with `unit_candidates must be a list or tuple`.

## Dependency and Portability Impact

No dependency was added or changed. The existing OpenAI-compatible DeepSeek
adapter remains behind the AI adapter layer.

## Risks

- DeepSeek JSON Output mode may be too weak for the current extraction schema
  without additional normalization, a different model/API mechanism, or a
  provider with stricter structured-output support.
- Continuing prompt-only iteration could consume live-smoke quota without
  converging.
- The project still lacks a raw-output retention approval for deeper debugging;
  current run logs intentionally preserve only hashes and metadata.

## Required Changes Before Continuing

None for this hardening stage.

## Optional Improvements

- Decide whether to add a narrow, explicitly reviewed JSON-mode normalization
  layer for common shape drift before typed validation.
- Compare DeepSeek models/API modes for stricter schema adherence.
- Prefer a provider path with strict JSON Schema support for first real-note
  evaluation if DeepSeek remains non-conforming on fixtures.

## Escalation Requests

None for this implementation. A separate product-owner decision is required
before testing real notes or adding any raw provider output retention.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked
