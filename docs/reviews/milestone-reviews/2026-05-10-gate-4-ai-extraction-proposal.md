# Milestone Review: Gate 4 AI Extraction Proposal

## Scope Reviewed

Gate 4 AI extraction proposal implementation on branch `feat/ai-extraction-proposal`.

Reviewed scope:

- `src/diamonddust/ai/__init__.py`
- `src/diamonddust/ai/extraction.py`
- `tests/unit/test_ai_extraction.py`
- `docs/exec-plans/active/2026-05-10-gate-4-ai-extraction-proposal.md`

## Product Goal Alignment

Aligned. The implementation introduces the first AI output boundary needed for the MVP: structured extraction output can become typed candidate units and relations only after validation.

Gate 4 pass conditions are covered:

- LLM-like output must be structured.
- Output passes schema validation before becoming internal data.
- Invalid output fails safely.
- Run log fields are recorded for pass and fail outcomes.

## Architecture Boundary Compliance

Compliant.

- Provider-neutral AI boundary code lives under `src/diamonddust/ai/`.
- Domain schemas remain in the domain core.
- No provider SDK, external service, UI framework, storage engine, Obsidian, Notion, or MCP dependency was introduced.
- The AI module consumes domain schema constructors but does not add provider behavior to domain code.

## Cohesion Assessment

Good. The module has one responsibility: validate extraction task output and produce either a typed `ExtractionProposal` or a failed validation result with a run log.

## Coupling Assessment

Acceptable. Coupling is limited to standard-library hashing/JSON handling and domain schema validation. The module is not coupled to future prompt execution, retry behavior, provider routing, patch generation, or vault writes.

## Data and Schema Safety

Compliant for Gate 4.

- Free-form output is rejected and does not become a proposal.
- Candidate units and relations are created through typed domain schema constructors.
- Unit candidates must preserve source references to the source input.
- Run logs include task, provider, model, prompt version, schema version, input hash, output hash, cost, latency, and validation status.
- Raw AI output is not stored in the run log mapping.

## AI Output Boundary

Compliant. The implementation validates structured output and fails closed on malformed output. It does not write suggestions, reports, patches, or formal knowledge files.

## Tests and Evaluation

Validation run:

- `PYTHONPATH=src python3 -m unittest discover -s tests`: 27 tests passed.
- `python3 -m compileall src tests`: passed.
- `git diff --check`: passed.

Coverage added:

- valid structured output becomes typed proposal
- run log serialization excludes raw output
- free-form output fails safely
- invalid domain candidate fails safely
- missing source refs fails safely
- output hashing is deterministic for structured output
- prompt version metadata is required
- wrong task metadata fails safely

## Dependency and Portability Impact

No production or development dependency was added. The implementation uses only Python standard-library modules.

## Risks

- The module validates already-structured output but does not call an actual provider.
- Run logs are typed and serializable but not durably written to `_ai_runs/` yet.
- Extraction quality cannot be measured until real prompts, adapters, and golden fixtures exist.

## Required Changes Before Continuing

None.

## Optional Improvements

- Add durable run log storage under AI working directories when storage behavior is introduced.
- Add provider adapter interfaces and prompt templates in a future task.
- Add golden fixture evaluation once MVP sample essays are selected.

## Escalation Requests

None.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked

Gate 4 AI Extraction Proposal may be treated as complete for the current MVP skeleton. Follow-ups are not blockers for Gate 5 planning.
