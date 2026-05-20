# Execution Plan: Provider Adapter Design

## Product Goal

Prepare DiamondDust for the first real-provider adapter by documenting the adapter boundary, implementation constraints, approval requirements, and product-owner decision package template before any SDK, API key, or network behavior is introduced.

## Current Understanding

The provider-neutral skeleton is ready for design-level adapter planning. DiamondDust now has provider-neutral requests, prompt rendering, output schema packaging, execution payload preview, typed response/error envelopes, source binding, validation, run-log context, and readiness diagnostics. Real provider integration is still blocked until product-owner decisions are explicit.

## Assumptions

- The first real-provider task remains `extract_units` only.
- Adapter design may describe provider-specific mapping but must not implement it.
- A decision package template may list required approvals, but it must not approve real provider integration by itself.
- API key values must never be requested, stored, printed, or committed.

## Non-goals

- No provider SDK dependency.
- No API key reads.
- No real network calls.
- No provider-specific request mapping implementation.
- No raw provider output persistence.
- No provider-side tools, web search, file search, MCP, or autonomous tool execution.
- No KnowledgePatch generation changes.
- No formal apply, patch acceptance, blog publication, or provider-backed blog drafting.

## Proposed Technical Approach

Create a design document that defines the future first-provider adapter boundary around `ProviderExecutionClient.generate(ProviderExecutionRequest) -> ProviderResult`. The design will specify module ownership, dependency direction, request mapping, structured output handling, error mapping, metrics, logging, test strategy, and implementation gates.

Add a Markdown decision package template for product-owner approval. The template will make every high-impact decision explicit and keep the default state as pending/not approved.

## Task Breakdown

- [x] Write provider adapter design document.
- [x] Add product-owner decision package template.
- [x] Update AI pipeline contract with adapter design package boundary.
- [x] Update README/provider readiness notes if needed.
- [x] Update repo memory and milestone review.
- [x] Run checks.

## Likely Files Changed

- `docs/designs/2026-05-20-first-provider-adapter-design.md`
- `docs/templates/PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `README.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-20-provider-adapter-design.md`
- `docs/exec-plans/active/2026-05-20-provider-adapter-design.md`

## Validation Plan

- [x] unit tests
- [x] compile check
- [x] whitespace diff check
- [x] local trial fixture smoke
- [x] architecture scan
- [x] manual docs review

## Review Gate Impact

Post-Gate 7 provider-readiness design milestone. It prepares for, but does not approve or implement, real provider integration.

## Risks

- A design package could be mistaken for real-provider approval if boundary text is unclear.
- Provider-specific details may need revision after the product owner selects the first provider and model.
- The decision template must stay aligned with existing readiness decisions without replacing the current readiness gate.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed for design and templates. Escalation remains required before SDK dependencies, API key reads, real network calls, prompt externalization, cost-bearing behavior, or raw provider output retention.

## Definition of Done

- Adapter design defines future implementation boundaries without adding code.
- Decision package template lists every required product-owner approval and defaults to pending.
- Docs preserve provider-neutral/domain/storage boundaries.
- Existing tests and checks pass.
