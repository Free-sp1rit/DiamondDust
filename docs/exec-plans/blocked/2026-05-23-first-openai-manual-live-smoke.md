# Execution Plan: First OpenAI Manual Live Smoke

## Product Goal

Run exactly one controlled OpenAI `extract_units` smoke using a small fixture
essay, then validate and persist only safe AI working artifacts.

## Current Understanding

The product owner approved the decision package for one manual live smoke. This
execution plan is intentionally blocked until the product owner explicitly asks
Codex to execute the live smoke after reviewing the decision package.

The CLI execution path is implemented on the
`feat/openai-live-smoke-execution` branch: `openai-extract-units` remains
blocked by default and enters live execution only with all one-smoke approval
flags, the approved model, the approved fixture path, and the approved cost and
timeout policy.

## Blocker

- Awaiting explicit instruction to execute the live smoke.

## Approved Scope

- first_provider: openai
- model: gpt-5.5
- task: extract_units
- fixture: one small fixture essay only
- API key env var: DIAMONDDUST_OPENAI_API_KEY
- timeout_seconds: 60
- max_retries: 0
- fallback_behavior: disabled
- per_run_cost_limit: USD 1.00
- raw_output_retention: hash_and_metadata_only

## Non-goals

- Do not use real user essays.
- Do not run recurring live smoke.
- Do not enable provider-side tools, web search, file search, or MCP tool
  calling.
- Do not persist raw provider request or response bodies.
- Do not accept patches, formal apply, or publish.

## Proposed Execution Steps

1. Sync `main` and create or reuse a dedicated live-smoke branch.
2. Confirm `DIAMONDDUST_OPENAI_API_KEY` is present without printing its value.
3. Use `tests/fixtures/local_trial/trial-essay.md`.
4. Run `diamonddust openai-extract-units` with all approved one-smoke flags.
5. Execute one OpenAI call through the approved adapter path.
6. Validate provider output with source binding and typed runtime validation.
7. Persist run log, validated extraction artifact, and reviewable AI working
   reports only.
8. Confirm no formal vault files changed.
9. Report cost/latency/token metadata if available without raw output.

## Validation Plan

- Check no formal vault write occurred.
- Check raw provider request/response bodies were not persisted.
- Check run log records provider metadata without secrets.
- Check validated extraction artifact exists only if typed validation passed.
- Check patch acceptance, formal apply, and publication remain absent.

## Rollback Plan

If the smoke creates only AI working artifacts, delete or archive the smoke
artifacts in a follow-up cleanup task if the product owner requests it. No
formal vault rollback should be needed because formal writes are out of scope.

## Review Gate Impact

This future execution will affect auth, network, cost, provider output, and user
data externalization boundaries. It requires milestone review immediately after
execution.
