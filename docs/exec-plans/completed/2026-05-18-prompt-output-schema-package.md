# Execution Plan: Prompt Output Schema Package

## Product Goal

Prepare concrete provider adapters to receive the `extract_units` structured-output contract through the prompt package without adding a real provider integration.

## Current Understanding

DiamondDust can now print a generated JSON Schema for `extract_units` output. The prompt renderer currently emits text instructions describing the expected JSON fields, but the `RenderedPrompt` object does not carry the machine-readable schema that a future provider adapter may need for structured-output APIs.

## Assumptions

- The generated schema is provider-neutral and safe to keep in the in-memory prompt package.
- Rendering the schema does not approve sending it to a real provider.
- Prompt rendering remains deterministic and provider-free.
- Typed runtime validation remains authoritative after provider output is returned.

## Non-goals

- Do not call a real provider.
- Do not choose a provider-specific structured-output mechanism.
- Do not add SDK dependencies.
- Do not read API keys.
- Do not persist prompt text, schema payloads, or raw provider output.
- Do not record provider approval.
- Do not broaden the first real-provider task beyond `extract_units`.

## Proposed Technical Approach

Extend `RenderedPrompt` with output schema metadata and the generated JSON Schema object. Include the schema hash in the prompt hash input so prompt identity changes if the schema changes. Update execution-request validation to ensure the rendered prompt schema version matches the provider request schema version. Keep storage/run-log behavior unchanged.

## Task Breakdown

- [x] Attach output schema id/version/hash/object to `RenderedPrompt`.
- [x] Include schema information in output instructions and prompt hash.
- [x] Reject prompt rendering when the request schema version is unsupported by the generated schema.
- [x] Validate schema metadata in `ProviderExecutionRequest`.
- [x] Add prompt renderer and execution request tests.
- [x] Update docs and durable context.
- [x] Run validation and milestone review.

## Likely Files Changed

- `src/diamonddust/ai/prompt.py`
- `src/diamonddust/ai/provider_execution.py`
- `tests/unit/test_prompt_renderer.py`
- `tests/unit/test_provider_execution_request.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-18-prompt-output-schema-package.md`

## Validation Plan

- [x] focused prompt/execution tests
- [x] full unittest discovery
- [x] compile check
- [x] diff whitespace check
- [x] local trial fixture smoke
- [x] architecture scan

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. It strengthens the provider execution request boundary without approving real provider integration.

## Risks

- Adding the schema object to rendered prompts increases the prompt package shape and may require future provider-specific schema transforms.
- JSON Schema cannot express every runtime validation rule, so adapters must still pass returned output through typed validation.
- Future persisted prompt diagnostics must avoid storing rendered prompt/schema payloads unless retention policy is approved.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because the task adds no dependency, provider SDK, network call, API key read, raw output persistence, provider approval, or formal write behavior.

## Definition of Done

- Rendered prompts carry output schema metadata and schema content.
- Prompt hash changes with schema identity.
- Execution requests reject mismatched schema metadata.
- Tests and docs preserve the no-provider/no-persistence boundary.
- Validation passes.
