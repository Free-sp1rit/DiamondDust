# Execution Plan: Provider Source Context Binding Hardening

## Product Goal

Improve real-provider `extract_units` trial reliability without weakening source
review safety, after DeepSeek returned structured JSON that reached the provider
but failed validation because the top-level `source_input_id` did not match the
request context.

## Current Understanding

The provider call path is working, but real provider output can treat
`source_input_id` as generated text even though DiamondDust already knows the
source identity from the request. The application layer should remain the
authority for request source identity while typed validation still requires unit
source references to preserve the correct source.

## Assumptions

- `source_input_id` at the top level is lineage context owned by the
  application request.
- Unit `source_refs` are the safety-critical source evidence that must still
  match the request-bound source id.
- Prompt wording can reduce provider mistakes, but runtime validation remains
  authoritative.

## Non-goals

- Do not persist raw provider request or response bodies.
- Do not formal apply, record patch acceptance, or publish.
- Do not add provider-side tools, retries, fallback, or new provider tasks.
- Do not weaken validation for source references.

## Proposed Technical Approach

Strengthen the provider-neutral prompt instructions to require exact
`source_input_id` and `source_ref_json.source_id` preservation. In the
application provider handoff, bind only the top-level `source_input_id` from the
request before typed extraction validation. Do not rewrite unit source
references; if provider-generated candidates point at the wrong source, typed
validation must continue to fail closed.

## Task Breakdown

- [x] Update prompt instructions for exact source identity preservation.
- [x] Bind top-level provider output `source_input_id` from request context
      before validation.
- [x] Add regression tests for top-level binding and wrong source references.
- [x] Update docs/context and milestone review.
- [x] Run focused tests, full tests, compile check, diff check, and local trial
      smoke.

## Likely Files Changed

- `src/diamonddust/ai/prompt.py`
- `src/diamonddust/application/provider_extraction.py`
- `tests/unit/test_prompt_renderer.py`
- `tests/unit/test_provider_boundary.py`
- `tests/unit/test_provider_extraction_orchestrator.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-25-provider-source-context-binding.md`
- `docs/exec-plans/completed/2026-05-25-provider-source-context-binding.md`

## Validation Plan

- [x] focused prompt/provider boundary/orchestrator tests
- [x] full unit test suite
- [x] compile check
- [x] whitespace diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan

## Review Gate Impact

Provider extraction boundary hardening after real-provider trial feedback. This
changes application-layer source binding behavior, so milestone review is
required.

## Risks

- Binding top-level lineage could obscure provider mistakes if raw output hashes
  are not separately inspected.
- Prompt wording may still be insufficient for weaker JSON-mode providers.
- Future tasks beyond `extract_units` may need different source binding rules.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because the change tightens source-reference safety,
adds no dependency, performs no provider call by itself, does not read keys, and
does not change formal vault behavior.

## Definition of Done

- Top-level provider output source id is bound from request context.
- Wrong unit source refs still fail closed.
- Prompt instructions clearly state exact source identity requirements.
- Tests and milestone review record the updated boundary.
