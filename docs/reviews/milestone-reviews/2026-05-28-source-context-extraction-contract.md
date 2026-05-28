# Milestone Review: SourceContext Extraction Contract

Review date: 2026-05-28

## Scope

Add top-level `source_context` to current provider-facing `extract_units`
output so whole-note background, domain, main content, and scope are separated
from ordinary reusable knowledge unit candidates.

## Decision

Pass with follow-up.

## What Changed

- Added typed `SourceContext` and constrained `SourceShape` values in the AI
  extraction boundary.
- Bumped current provider-facing extraction output schema to `0.2.0`.
- Kept legacy `0.1.0` extraction output without `source_context` compatible.
- Required `source_context` for current schema output.
- Rejected generated `raw_essay` unit candidates for current schema output.
- Updated prompt instructions to put whole-note context in `source_context`,
  not in ordinary units.
- Bound request-owned `source_context.source_input_id` before typed validation,
  while keeping source refs strict.
- Persisted `source_context`, `knowledge_unit_count_excluding_raw_essay`, and
  `raw_essay_unit_count` in validated extraction artifacts.
- Updated Python fallback client and React trial client to display source
  context separately and count non-raw knowledge units.

## Boundary Check

- `SourceContext` lives in the provider-neutral AI extraction boundary, not in
  provider adapters, storage-specific code, or domain `KnowledgeUnit`.
- Provider-specific SDK imports remain isolated to AI adapter modules.
- Formal vault mutation remains unchanged and out of scope.
- Raw provider request/response persistence remains disabled by default.
- Legacy fixture outputs remain valid only through the legacy schema path.

## Validation

- Focused extraction/prompt/provider/artifact/trial-client tests: passed.
- Full unit suite: 287 tests passed.
- Frontend build: `npm run build` passed.
- Compile check: passed.
- `git diff --check`: passed.
- Local trial fixture smoke: passed with `provider_called: false` and
  `formal_write_performed: false`.
- Architecture boundary scan: `critical_architecture_violations=0`.

## Risks

- Providers may still leak source-level summary into units despite the new
  contract; this needs real-note review feedback.
- `SourceContext` improves unit cleanliness but does not add missing unit types
  such as `procedure` or `configuration_decision`.
- Older generated artifacts do not contain source context and should remain
  labeled as legacy in UI/review surfaces.

## Follow-Up

- Evaluate future real-note outputs for `source_context_leakage`.
- Evaluate future real-note outputs for `missing_minimal_context`.
- Decide whether the unit taxonomy needs procedure/configuration-decision
  types after more trial feedback.
