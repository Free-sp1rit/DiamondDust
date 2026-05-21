# Execution Plan: OpenAI SDK Decision Recording

## Product Goal

Record the product-owner decision to adopt the OpenAI official SDK as the first
provider adapter integration style without starting provider implementation.

## Current Understanding

OpenAI is already selected as the first provider planning target. The new
decision selects the OpenAI official SDK over direct HTTP for the future
`extract_units` provider adapter path.

## Assumptions

- This is a decision-recording task.
- Dependency file changes remain unapproved.
- Real provider adapter implementation remains unapproved.
- API key reads, network calls, live smoke, raw output persistence, formal
  apply, patch acceptance, and publication remain unapproved.

## Non-goals

- Do not add the OpenAI SDK dependency.
- Do not modify dependency files.
- Do not implement a real provider adapter.
- Do not read API keys or make network calls.
- Do not run live smoke.

## Proposed Technical Approach

Update the provider decision package template, first-provider adapter design,
repo memory, and design-doc tests so the SDK decision is explicit while the
remaining safety gates stay fail-closed.

## Task Breakdown

- [x] Update dependency choice fields in the decision package template.
- [x] Update first-provider adapter design decision wording.
- [x] Update repo memory and open questions.
- [x] Update design-doc tests.
- [x] Run focused and full validation.

## Likely Files Changed

- `docs/templates/PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md`
- `docs/designs/2026-05-20-first-provider-adapter-design.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/exec-plans/completed/2026-05-20-provider-approval-package-revision.md`
- `tests/unit/test_provider_adapter_design_docs.py`

## Validation Plan

- [x] unit tests
- [ ] integration tests
- [ ] golden tests
- [ ] regression tests
- [x] compile check
- [x] diff check
- [x] manual review

## Review Gate Impact

Post-Gate 7 provider-readiness design update. This records a dependency-path
decision but does not add a production dependency or introduce provider code.

## Risks

- Readers may confuse SDK choice approval with permission to add the dependency
  or make live provider calls.
- Future implementation must keep SDK imports isolated to the AI adapter layer.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because the product owner directly approved the SDK
choice and this task only records that decision.

## Definition of Done

- Decision package and design docs record `openai_official_sdk`.
- Remaining non-approvals stay explicit.
- Repo memory reflects that dependency file changes and live execution remain
  pending.
- Tests and checks pass.
