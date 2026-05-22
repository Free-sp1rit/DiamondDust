# Execution Plan: First OpenAI Manual Live Smoke Decision Package

## Product Goal

Record the product-owner decisions needed before a single controlled OpenAI
`extract_units` live smoke and make the readiness gate reflect those decisions
without reading API keys, calling OpenAI, or running the live smoke.

## Current Understanding

The project is technically ready to prepare for one manual live smoke, but live
execution still requires a separate execution step. The product owner approved
one tightly scoped OpenAI live smoke using `gpt-5.5`, the
`DIAMONDDUST_OPENAI_API_KEY` environment variable, one small fixture essay, no
retries, no fallback, a USD 1.00 per-run cost limit, and hash/metadata-only raw
output retention.

The approval is not recurring. It does not approve real user essay
externalization, provider-side tools, web/file search, MCP tool calling, patch
acceptance, formal apply, publication, or raw provider request/response
persistence.

## Assumptions

- This task records and validates decisions only.
- Actual live smoke execution remains a separate task after this package is
  reviewed.
- `prompt_source_schema_externalization_approved` is represented by separate
  `prompt_text_external_approved`, `source_body_external_approved`, and
  `output_schema_external_approved` fields.
- `raw_output_retention: hash_and_metadata_only` means raw request/response
  bodies are not persisted, but hashes, run metadata, and typed validated
  extraction artifacts may be persisted.

## Non-goals

- Do not read `DIAMONDDUST_OPENAI_API_KEY`.
- Do not call OpenAI or make network requests.
- Do not run live smoke.
- Do not send prompt/source/schema content externally.
- Do not persist raw provider request or response bodies.
- Do not record patch acceptance, formal apply, or publication.
- Do not enable recurring live smoke or real user essay externalization.

## Proposed Technical Approach

Update the OpenAI live-smoke readiness policy to accept the revised one-smoke
configuration: `timeout_seconds: 60`, `max_retries: 0`,
`fallback_behavior: disabled`, `raw_output_retention: hash_and_metadata_only`,
and OpenAI-specific provider/model/key/task values.

Add a concrete decision package document that records the accepted decisions,
explicit non-approvals, and safety boundaries. Add a follow-on live-smoke
execution plan draft that can be used only after this decision package is
reviewed. Update tests so the readiness gate reports ready for the approved
decision set while still not reading secrets or calling providers.

## Task Breakdown

- [x] Update OpenAI live-smoke readiness policy and tests.
- [x] Create the concrete live-smoke decision package.
- [x] Create the live-smoke execution plan draft.
- [x] Update design/template/context docs.
- [x] Run validation.

## Likely Files Changed

- `src/diamonddust/application/provider_integration_readiness.py`
- `tests/unit/test_provider_integration_readiness.py`
- `tests/unit/test_cli_entrypoints.py`
- `docs/designs/2026-05-20-first-provider-adapter-design.md`
- `docs/templates/PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md`
- `docs/designs/2026-05-23-first-openai-manual-live-smoke-decision-package.md`
- `docs/exec-plans/blocked/2026-05-23-first-openai-manual-live-smoke.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-23-openai-live-smoke-decision-package.md`

## Validation Plan

- [x] focused provider readiness tests
- [x] focused CLI tests
- [x] full unit test suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan

## Review Gate Impact

Post-Gate 7 provider-readiness decision milestone. This records a high-impact
network/API-key decision, so milestone review is required even though no live
call is executed.

## Risks

- The decision package could be mistaken for the actual live smoke execution.
- A broad externalization approval could accidentally include real user essays.
- Hash/metadata retention must not drift into raw provider request/response
  persistence.

## Escalation Needed

Does this require user approval?

- [x] no: the product owner supplied the live-smoke decision set, and this task
  records it without executing live behavior.
- [ ] yes

## Definition of Done

- A concrete decision package records the revised decision set and explicit
  non-approvals.
- OpenAI live-smoke readiness is ready for that exact decision set and remains
  provider-free when rendered.
- A separate execution plan draft exists for the future live smoke.
- No API key is read, no network call occurs, and no live smoke is run.

## Completion Summary

- OpenAI live-smoke readiness now accepts the revised one-smoke policy:
  `gpt-5.5`, `DIAMONDDUST_OPENAI_API_KEY`, timeout 60 seconds, zero retries,
  disabled fallback, USD 1.00 cost limit, and hash/metadata-only retention.
- The concrete decision package and blocked execution plan are recorded.
- Validation passed: 240 unit tests, compile check, diff check, local trial
  fixture smoke with 12 provider-free artifacts, and architecture scan with 0
  violations.
