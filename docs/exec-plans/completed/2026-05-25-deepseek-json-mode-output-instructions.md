# Execution Plan: DeepSeek JSON Mode Output Instructions

## Product Goal

Make DeepSeek `extract_units` live smoke output conform to DiamondDust's typed
extraction schema without weakening validation or adding provider-specific
rules to the domain layer.

## Current Understanding

DeepSeek JSON mode returns valid JSON but does not enforce DiamondDust's JSON
Schema. Real-call diagnostics showed non-empty JSON responses with provider
chosen keys such as `units` or `candidates`, while a controlled probe that sent
the existing output instructions and a compact JSON example produced valid
`unit_candidates` / `relation_candidates` output.

## Assumptions

- DeepSeek-specific JSON mode prompt shaping belongs in the DeepSeek adapter.
- Typed runtime validation remains the authoritative acceptance boundary.
- The implementation may support live smoke controls already approved for the
  DeepSeek adapter, but must not persist raw provider request/response bodies.

## Non-goals

- Do not add field alias compatibility such as treating `units` as
  `unit_candidates`.
- Do not modify domain schemas to accommodate DeepSeek output drift.
- Do not enable provider-side tools, web search, file search, MCP, patch
  acceptance, formal apply, or publication.
- Do not persist raw provider request or response bodies.

## Proposed Technical Approach

Keep the fix cohesive inside the DeepSeek adapter by adding a helper that
combines the provider-neutral system prompt, provider-neutral output
instructions, and a compact JSON mode example before mapping to
`chat.completions.create`. Add an adapter-level `max_tokens` setting because
DeepSeek JSON mode recommends a reasonable token limit to reduce empty/truncated
responses.

The CLI exposes `--max-tokens` only for DeepSeek commands and carries the value
into the DeepSeek adapter config. Tests verify the mapping without calling the
provider.

## Task Breakdown

- [x] Add DeepSeek JSON mode message helper and compact output example.
- [x] Add DeepSeek adapter `max_tokens` configuration and CLI flag.
- [x] Update provider-free mapping, safety, and CLI tests.
- [x] Run focused tests, full tests, compile check, diff check, architecture
      scan, and a controlled DeepSeek fixture smoke.
- [x] Complete milestone review and context docs.

## Files Changed

- `src/diamonddust/ai/adapters/deepseek.py`
- `src/diamonddust/cli.py`
- `tests/unit/test_deepseek_adapter_mapping.py`
- `tests/unit/test_deepseek_adapter_safety.py`
- `tests/unit/test_cli_entrypoints.py`
- `docs/designs/2026-05-23-deepseek-provider-adapter.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-25-deepseek-json-mode-output-instructions.md`

## Validation Results

- [x] focused DeepSeek adapter/CLI tests: 31 tests passed
- [x] full unit test suite: 262 tests passed
- [x] compile check: passed
- [x] diff check: passed
- [x] local trial fixture smoke: passed with 12 artifacts
- [x] DeepSeek fixture live smoke: passed typed validation
- [x] architecture boundary scan: 0 violations
- [x] milestone review: pass with follow-up

## Review Gate Impact

This touched a concrete provider adapter and real-call output behavior. A
milestone review was completed at
`docs/reviews/milestone-reviews/2026-05-25-deepseek-json-mode-output-instructions.md`.

## Risks

- The adapter could overfit the fixture prompt instead of generalizing to
  realistic notes.
- Increasing `max_tokens` can increase potential live-smoke cost.
- Adding output instructions to DeepSeek messages increases prompt size, though
  it stays within the approved `extract_units` live-smoke scope.

## Escalation Needed

Does this require user approval?

- [x] no: the user explicitly approved continuing implementation and real-call
      testing for this diagnostic/fix stage.
- [ ] yes

## Definition of Done

- DeepSeek request mapping sends output instructions and a compact JSON example.
- DeepSeek preview/dry-run remains sanitized and provider-free.
- DeepSeek fixture live smoke passes typed extraction validation.
- No raw provider request/response is persisted and no formal vault write occurs.
