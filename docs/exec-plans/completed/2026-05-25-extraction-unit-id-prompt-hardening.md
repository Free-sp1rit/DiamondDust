# Execution Plan: Extraction Unit ID Prompt Hardening

## Product Goal

Improve DeepSeek fixture smoke reliability after provider calls succeeded but
typed validation failed first because a generated `unit_candidates` item omitted
the required `id` field, then because a required enum field was not emitted as a
JSON string.

## Current Understanding

DiamondDust already requires every `KnowledgeUnit` candidate to include a
non-empty `id` and typed string enum fields. DeepSeek JSON Output mode is
prompt-guided rather than strict JSON Schema enforcement, so the provider can
still return incomplete candidate objects or non-string enum values. The right
fix is to make the prompt/schema guidance more explicit and improve validation
diagnostics while preserving fail-closed typed validation.

## Assumptions

- Candidate unit ids are provider-proposed review ids, not formal vault ids.
- The application should not silently invent missing provider candidate ids.
- A request-derived id prefix can help models produce stable, reviewable ids.
- Explicit enum-string instructions can reduce JSON-mode provider drift.

## Non-goals

- Do not auto-fill missing `unit_candidates[].id` values.
- Do not weaken `KnowledgeUnit` validation.
- Do not change formal vault behavior, patch acceptance, formal apply, or
  publication.
- Do not persist raw provider request/response bodies.
- Do not add provider-side tools, retries, fallback, or new provider tasks.

## Proposed Technical Approach

Add explicit unit-id instructions to the provider-neutral prompt renderer,
including a deterministic request-derived `unit_id_prefix`. Add a schema
description for `knowledge_unit.id` to make the embedded schema more helpful to
prompt-guided JSON-mode providers. Add explicit enum-as-string instructions for
unit, source ref, and relation enum fields. Improve validation error messages with
`unit_candidates[index]` context so future provider smoke failures identify the
offending candidate.

## Task Breakdown

- [x] Add prompt instructions and user prompt metadata for `unit_id_prefix`.
- [x] Add schema description for `knowledge_unit.id`.
- [x] Add prompt instructions that enum-valued fields must be JSON strings.
- [x] Add indexed validation errors for invalid unit and relation candidates.
- [x] Add regression tests.
- [x] Update docs/context and milestone review.
- [x] Run focused tests, full tests, compile check, diff check, local trial
      smoke, and one controlled DeepSeek fixture smoke if provider key is
      available.

## Likely Files Changed

- `src/diamonddust/ai/prompt.py`
- `src/diamonddust/ai/extraction_schema.py`
- `src/diamonddust/ai/extraction.py`
- `tests/unit/test_prompt_renderer.py`
- `tests/unit/test_extraction_output_schema.py`
- `tests/unit/test_ai_extraction.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-25-extraction-unit-id-prompt-hardening.md`
- `docs/exec-plans/completed/2026-05-25-extraction-unit-id-prompt-hardening.md`

## Validation Plan

- [x] focused prompt/schema/extraction tests
- [x] full unit test suite
- [x] compile check
- [x] whitespace diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan
- [x] controlled DeepSeek fixture smoke, if key is available

## Review Gate Impact

Post-Gate 7 provider prompt/schema hardening after real-provider trial feedback.
Milestone review is required because this affects AI output contract guidance
and validation diagnostics.

## Risks

- Prompt-only guidance may still be insufficient for weaker JSON-mode models.
- A stricter id convention may need later tuning after more provider output
  samples.
- The live smoke consumes a small amount of provider quota when run.
- Controlled DeepSeek fixture smokes still failed typed validation after this
  hardening, most recently because `unit_candidates` was not emitted as a JSON
  array.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

The product owner already asked to complete this follow-up. The implementation
adds no dependency, does not broaden provider permissions, and does not change
formal write behavior.

## Definition of Done

- Prompt includes explicit non-empty unit id requirements, id prefix, and enum
  string requirements.
- Schema guidance documents the required unit id.
- Validation failures identify the candidate index.
- Provider-free tests pass.
- If a controlled DeepSeek fixture smoke is run, it remains hash/metadata-only
  with no formal write, patch acceptance, or publication.
