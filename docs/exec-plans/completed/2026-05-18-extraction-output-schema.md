# Execution Plan: Extraction Output JSON Schema

## Product Goal

Prepare the provider-neutral extraction boundary for real provider structured output by exposing a machine-readable schema for `extract_units` output.

## Current Understanding

The local trial and provider-free extraction path already validate structured extraction JSON through typed Python domain models. The repository has a human guide and fixture JSON, but no machine-readable schema that can be printed, reviewed, or used as future provider structured-output input.

## Assumptions

- The schema is a contract aid, not a replacement for typed runtime validation.
- Runtime validation remains authoritative before any provider output becomes domain data.
- The schema should be generated from current domain enum definitions to reduce drift.
- The schema should be printable locally without dependencies or provider calls.

## Non-goals

- Do not add a JSON Schema validation dependency.
- Do not call a real provider.
- Do not choose provider-specific structured output settings.
- Do not add SDK dependencies.
- Do not read API keys.
- Do not persist raw provider output.
- Do not record provider approval.
- Do not broaden the first real-provider task beyond `extract_units`.

## Proposed Technical Approach

Add an AI-layer schema generator that returns a JSON-serializable JSON Schema draft for `extract_units` output. Reuse domain enum definitions for allowed values. Add a CLI command that prints the schema to stdout for review and future provider planning. Keep existing typed validation as the runtime acceptance gate.

## Task Breakdown

- [x] Add generated extraction output JSON Schema.
- [x] Export the schema function through the AI package.
- [x] Add `diamonddust extraction-output-schema`.
- [x] Add tests for schema shape, enum alignment, CLI output, and docs linkage.
- [x] Update README, local trial extraction guide, AI pipeline contract, and context memory.
- [x] Run validation.
- [x] Record milestone review and complete the plan.

## Likely Files Changed

- `src/diamonddust/ai/extraction_schema.py`
- `src/diamonddust/ai/__init__.py`
- `src/diamonddust/cli.py`
- `tests/unit/test_extraction_output_schema.py`
- `tests/unit/test_cli_entrypoints.py`
- `tests/unit/test_local_trial_extraction_json_docs.py`
- `README.md`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/guides/local-trial-extraction-json.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-18-extraction-output-schema.md`

## Validation Plan

- [x] focused schema/CLI/docs tests
- [x] full unittest discovery
- [x] compile check
- [x] diff whitespace check
- [x] local trial fixture smoke
- [x] architecture scan
- [x] manual CLI schema smoke

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. It clarifies the `extract_units` output contract for future provider integration without approving real provider calls.

## Risks

- Schema semantics could drift from typed validation if not tested against domain enums.
- JSON Schema cannot express every runtime rule, especially cross-field checks like source refs matching `source_input_id`.
- Future provider-specific structured output mechanisms may require a narrower or transformed schema.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because this task adds no dependency, provider SDK, network call, API key read, raw output persistence, provider approval, or formal write behavior.

## Definition of Done

- A generated, JSON-serializable schema exists for `extract_units` output.
- CLI can print the schema without provider calls or dependencies.
- Tests verify schema enums align with domain enums and fixture docs stay connected.
- Docs explain that typed runtime validation remains authoritative.
- Validation passes.
