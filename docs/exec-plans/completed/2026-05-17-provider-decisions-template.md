# Execution Plan: Provider Decisions JSON Template

## Product Goal

Make first-provider decision drafting easier by providing a safe JSON template for provider readiness and escalation diagnostics, without selecting a provider or recording approval.

## Current Understanding

The readiness and escalation CLI commands can now load decision values from JSON. The next safe usability step is to generate a blocked-by-default JSON template so the product owner can fill decision values without copying field names from code.

## Assumptions

- The template is an input aid only.
- The template does not record product-owner approval.
- The first real provider task remains limited to `extract_units`.
- The template must not include API key values or provider-specific secrets.

## Non-goals

- No real provider integration.
- No provider selection.
- No default model selection.
- No provider SDK dependency.
- No API key value read.
- No network call.
- No prompt package persistence.
- No raw provider output persistence.
- No formal apply, patch acceptance, publication, or provider-side tool execution.
- No durable approval artifact.

## Proposed Technical Approach

Add an application-level function that returns a strict JSON-serializable mapping for provider decision input. Add a `provider-decisions-template` CLI command that prints the template as deterministic JSON. The template should parse back into `ProviderIntegrationDecisionSet`, default to blocked, and keep all approvals false.

## Task Breakdown

- [x] Add provider decision template mapping function.
- [x] Expose the function through the application package.
- [x] Add `provider-decisions-template` CLI command.
- [x] Add tests for template shape, parser compatibility, blocked default status, and no secret fields.
- [x] Update README, AI pipeline docs, and repo memory.
- [x] Run validation and prepare PR.

## Likely Files Changed

- `src/diamonddust/application/provider_integration_readiness.py`
- `src/diamonddust/application/__init__.py`
- `src/diamonddust/cli.py`
- `tests/unit/test_provider_integration_readiness.py`
- `tests/unit/test_cli_entrypoints.py`
- `README.md`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-17-provider-decisions-template.md`

## Validation Plan

- [x] unit tests
- [x] regression tests
- [x] compile check
- [x] diff check
- [x] architecture scan
- [x] local trial fixture smoke
- [x] provider decisions template CLI smoke
- [x] manual review

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. This improves provider approval package usability without approving real provider integration.

## Risks

- A template file copied to disk could be mistaken for an approval artifact.
- JSON field names remain a user-facing input contract.
- Future durable approval records need a separate schema and storage owner.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this phase adds no provider SDK, API key read, network call, real cost behavior, prompt persistence, raw output persistence, formal apply, patch acceptance, or publication.

## Definition of Done

- CLI can print deterministic provider decision JSON template.
- Template parses into typed decisions and remains blocked by default.
- Tests prove template safety and parser compatibility.
- Docs, repo memory, and milestone review are updated.
- Validation passes and the task branch is ready for PR.
