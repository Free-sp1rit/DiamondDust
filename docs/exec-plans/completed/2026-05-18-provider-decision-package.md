# Execution Plan: Provider Decision Package

## Product Goal

Make first-provider approval review easier by rendering one local Markdown package that combines provider readiness status and the first-provider escalation request draft from the same typed decision input.

## Current Understanding

DiamondDust already has a provider-neutral readiness gate, strict provider decision JSON parsing, a blocked-by-default decision template, a readiness report renderer, an escalation request renderer, and CLI commands for each diagnostic artifact. The next useful step is to compose these existing pieces into a single review package without expanding runtime provider behavior.

## Assumptions

- The package is a diagnostic/review artifact only.
- Decision JSON remains input only and is not a durable approval artifact.
- A ready package still does not authorize implementation, provider calls, SDK dependencies, or API key reads.
- First real-provider scope remains limited to `extract_units`.

## Non-goals

- Do not add provider SDK dependencies.
- Do not choose a first provider or default model.
- Do not read API key values.
- Do not make network calls or real provider calls.
- Do not persist prompt text or raw provider output.
- Do not record provider approval.
- Do not change formal vault behavior.
- Do not implement provider integration.

## Proposed Technical Approach

Add an application renderer that accepts an existing `ProviderIntegrationReadinessReport` and returns a deterministic Markdown decision package. The package will include an explicit package boundary, the readiness report, and the escalation request draft. Add a CLI command that uses the same decision-input parser as the existing readiness commands and writes the package to stdout.

## Task Breakdown

- [x] Add provider decision package renderer in the application layer.
- [x] Export the renderer through the application package.
- [x] Add `diamonddust provider-decision-package`.
- [x] Add unit and CLI tests for blocked/ready packages, JSON input, and secret redaction.
- [x] Update user-facing docs and durable context.
- [x] Run focused and full validation.
- [x] Record milestone review and complete the plan.

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
- `docs/reviews/milestone-reviews/2026-05-18-provider-decision-package.md`

## Validation Plan

- [x] unit tests: provider integration readiness tests
- [x] CLI tests: provider decision package command tests
- [x] full unittest discovery
- [x] compile check
- [x] architecture scan
- [x] local trial fixture smoke
- [x] diff whitespace check
- [x] manual review of generated package output

## Review Gate Impact

Post-Gate 7 provider-readiness milestone. It improves first-provider review packaging but does not approve or implement real provider integration.

## Risks

- The package could be mistaken for approval if boundaries are unclear.
- Reusing rendered Markdown could create confusing heading hierarchy.
- CLI expansion could duplicate existing readiness commands if not clearly positioned.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is needed because the task does not add dependencies, call providers, read API keys, expand allowed provider task scope, persist raw provider output, or change formal write behavior.

## Definition of Done

- `provider-decision-package` renders one deterministic Markdown package from inline flags or decision JSON.
- The package includes explicit non-approval/no-provider/no-secret/no-formal-write boundaries.
- Tests cover blocked and ready decisions, JSON input, and secret redaction.
- Docs and repo memory describe the new diagnostic command without implying implementation approval.
- Validation passes.
