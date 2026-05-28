# Execution Plan: SourceContext Extraction Contract

## Product Goal

Make real-note extraction output more useful for future RAG and knowledge-base
workflows by separating source/article-level context from reusable knowledge
units.

## Current Understanding

Real trial output shows that providers tend to put whole-note summaries,
background, and scope into ordinary unit candidates because the current
`extract_units` contract has no source-level context field. That makes units
look structurally valid while being weak for retrieval, reuse, relation
building, and human review.

The product owner accepted introducing `source_context` as a top-level
source/article-level artifact beside `unit_candidates` and
`relation_candidates`. Ordinary units should stop carrying whole-note summary
responsibility but must still include enough local context to be independently
reviewable.

## Assumptions

- `source_context` is AI extraction output metadata, not a formal knowledge
  graph node.
- `source_context` may be rendered in trial artifacts and clients, but it must
  not become a `KnowledgeUnit`.
- Existing `0.1.0` extraction artifacts and fixtures should remain readable.
- New provider prompt/schema output can move to an extraction schema version
  that requires `source_context`.
- `raw_essay` remains a domain type for compatibility but should not be
  generated as an ordinary provider unit in the new output contract.

## Non-goals

- Do not add new unit types such as `procedure` or `configuration_decision` in
  this stage.
- Do not change formal vault write behavior.
- Do not generate or apply patches from provider output.
- Do not call providers or run live smoke as part of this implementation.
- Do not migrate old generated artifacts in place.

## Proposed Technical Approach

Add a provider-neutral `SourceContext` dataclass in the AI extraction boundary,
including `source_input_id`, constrained `source_shape`, `knowledge_domains`,
`background`, `main_content`, `scope`, and `source_refs`. Update the current
JSON Schema to require top-level `source_context` and bump the extraction
output schema version for new provider outputs while keeping legacy validation
for existing `0.1.0` artifacts.

Prompt instructions should explicitly require `source_context`, prohibit
whole-note summary units, and prohibit new provider outputs from using
`raw_essay` as a normal unit. Artifact persistence should store the
`source_context`, `raw_essay_unit_count`, and
`knowledge_unit_count_excluding_raw_essay`. The trial client should display
source context separately from units and should use the non-raw knowledge count
where available.

## Task Breakdown

- [x] Add `SourceContext` runtime shape and validation.
- [x] Update extraction JSON Schema and prompt instructions.
- [x] Bind request-owned source identity into top-level `source_context` where
      safe before validation.
- [x] Store source context and raw/non-raw counts in validated extraction
      artifacts.
- [x] Render source context in the trial client and keep legacy artifacts
      readable.
- [x] Update tests, project docs, and milestone review.
- [x] Run validation checks.

## Likely Files Changed

- `src/diamonddust/ai/extraction.py`
- `src/diamonddust/ai/extraction_schema.py`
- `src/diamonddust/ai/prompt.py`
- `src/diamonddust/ai/__init__.py`
- `src/diamonddust/application/provider_extraction.py`
- `src/diamonddust/storage/extraction_artifact.py`
- `src/diamonddust/interface/trial_client.py`
- `frontend/trial-client/src/App.tsx`
- `frontend/trial-client/src/App.css`
- focused unit tests under `tests/unit/`
- project context and contract docs

## Validation Plan

- [x] focused extraction validation tests
- [x] focused prompt renderer tests
- [x] focused provider orchestration tests
- [x] focused extraction artifact tests
- [x] focused trial client tests
- [x] frontend build, if React source changes
- [x] full unit test suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan

## Review Gate Impact

This changes the provider-neutral AI extraction output contract and
user-facing trial artifact shape, so a milestone review is required.

## Risks

- Bumping the schema version may expose provider prompt or test assumptions
  that still hardcode `0.1.0`.
- `source_context` could become another summary field unless prompt and review
  copy keep it separate from reusable units.
- Existing artifacts without `source_context` must remain viewable in the trial
  client.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

The product owner approved the design direction. This stage adds no dependency,
does not call a provider, does not read secrets, and does not change formal
vault mutation behavior.

## Definition of Done

- New provider-facing extraction schema requires `source_context`.
- Runtime validation accepts typed `SourceContext` for new outputs and keeps
  legacy `0.1.0` outputs compatible.
- New provider outputs cannot use `raw_essay` as a normal unit.
- Trial artifacts and the trial client show source context separately from
  ordinary units.
- Tests and milestone review document the updated boundary.
