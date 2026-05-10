# Execution Plan: Gate 4 AI Extraction Proposal

## Product Goal

Implement the minimal provider-neutral AI extraction proposal boundary so structured LLM-like output can become typed candidate units and relations only after validation, while invalid output fails safely and records a run log.

## Current Understanding

Gate 2 provides typed domain schemas. Gate 3 provides read-only Markdown ingestion and source references. Gate 4 should introduce the first AI pipeline boundary without calling a real provider, adding provider SDKs, or allowing free-form AI output to become internal data.

## Assumptions

- Gate 4 can be satisfied with standard-library code and no production dependencies.
- The current scope validates already-structured model output; actual prompt execution and provider adapters belong to later work.
- Run log recording can start as an immutable typed run log returned with each validation result.
- Candidate extraction from a source essay should require candidate units to preserve at least one source reference.

## Non-goals

- Calling an LLM provider.
- Designing prompts beyond prompt version metadata.
- Retrying model calls or routing models.
- Generating `KnowledgePatch` values.
- Writing AI run logs to disk.
- Writing suggestions, reports, or formal vault notes.

## Proposed Technical Approach

Add a provider-neutral AI proposal module under `src/diamonddust/ai/` that:

- defines immutable metadata, run log, validation result, and extraction proposal types;
- validates the expected structured output shape for extraction proposals;
- converts candidate units and relations through domain schema constructors;
- rejects free-form or malformed output without returning a proposal;
- creates a run log for both pass and fail outcomes;
- computes deterministic input/output hashes for traceability.

## Task Breakdown

- [x] Create the AI package and extraction proposal module.
- [x] Add unit tests for valid structured output, safe invalid-output failure, domain validation failure, prompt version/run log fields, and source ref preservation.
- [x] Run unit tests, compile checks, and diff whitespace checks.
- [x] Complete milestone review before marking Gate 4 passed.
- [ ] Update repo memory and move this plan to completed when finished.

## Likely Files Changed

- `src/diamonddust/ai/__init__.py`
- `src/diamonddust/ai/extraction.py`
- `tests/unit/test_ai_extraction.py`
- `docs/exec-plans/active/2026-05-10-gate-4-ai-extraction-proposal.md`
- `docs/exec-plans/completed/2026-05-10-gate-4-ai-extraction-proposal.md`
- `docs/reviews/milestone-reviews/2026-05-10-gate-4-ai-extraction-proposal.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`

## Validation Plan

- [x] Unit tests for accepted structured extraction output.
- [x] Unit tests for free-form output failure.
- [x] Unit tests for invalid domain schema failure.
- [x] Unit tests for missing source reference failure.
- [x] Unit tests for run log and prompt version metadata.
- [x] Compile check.
- [x] Diff whitespace check.
- [x] Manual review of AI output boundary and provider neutrality.

## Review Gate Impact

This directly targets Gate 4: AI Extraction Proposal.

Gate 4 may be marked passed only if:

- LLM-like output is structured;
- output passes typed schema validation before becoming internal data;
- invalid output fails safely;
- run log fields are recorded;
- no free-form AI output becomes internal data;
- prompt version and run log blockers are absent.

## Risks

- The module validates structured output but does not yet execute prompts or provider calls.
- Run logs are returned as typed values but are not durably written to `_ai_runs/` yet.
- Candidate extraction quality cannot be evaluated until real fixtures and model/provider adapters exist.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because this plan avoids provider SDKs, production dependencies, external services, formal write behavior, public schema changes, and permission changes.

## Definition of Done

- Gate 4 extraction proposal boundary exists in an AI adapter-facing module.
- Tests cover valid and invalid structured outputs.
- Validation passes locally.
- Milestone review records a pass or pass-with-follow-up decision.
- Repo memory is updated with the new gate state, decisions, risks, and follow-ups.

## Completion Summary

Original goal: implement the minimal provider-neutral AI extraction proposal boundary for Gate 4.

Final implementation:

- Added a provider-neutral AI package.
- Added typed run metadata, run log, extraction proposal, and validation result objects.
- Added validation for structured extraction output into domain `KnowledgeUnit` and `Relation` candidates.
- Added fail-safe handling for free-form output, invalid schema data, missing source refs, and wrong task metadata.
- Added deterministic structured output hashing.

Files changed:

- `src/diamonddust/__init__.py`
- `src/diamonddust/ai/__init__.py`
- `src/diamonddust/ai/extraction.py`
- `tests/unit/test_ai_extraction.py`
- `docs/reviews/milestone-reviews/2026-05-10-gate-4-ai-extraction-proposal.md`
- repo memory docs under `docs/context/`

Public interfaces changed:

- New `diamonddust.ai` package.
- New `AIRunMetadata`, `AIRunLog`, `ExtractionProposal`, `ExtractionValidationResult`, `AIValidationStatus`, and `ExtractionValidationError` types.
- New `validate_extraction_output` and `compute_ai_output_hash` functions.

Important decisions:

- No provider SDK, production dependency, or external service was added.
- Gate 4 validates already-structured LLM-like output; provider execution is deferred.
- Run logs are returned as typed values and serializable mappings, but not durably written yet.

Known risks:

- Extraction quality cannot be evaluated until prompts, adapters, and fixtures exist.
- Durable run log storage still needs a future storage task.

Follow-up tasks:

- Begin Gate 5 Patch Review planning.
- Add durable `_ai_runs/` write behavior before real provider calls are introduced.
- Add golden fixture evaluation when MVP essays are selected.

Validation results:

- `PYTHONPATH=src python3 -m unittest discover -s tests`: 27 tests passed.
- `python3 -m compileall src tests`: passed.
- `git diff --check`: passed.
