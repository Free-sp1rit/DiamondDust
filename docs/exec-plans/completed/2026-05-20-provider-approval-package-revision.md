# Execution Plan: Provider Approval Package Revision

## Product Goal

Record product-owner decisions for first-provider implementation preparation without approving real provider adapter implementation, API key value reads, network calls, live smoke, raw output persistence, formal apply, patch acceptance, or publication.

## Current Understanding

The product owner approved planning/preparation work for real provider code implementation. OpenAI is selected as the first provider target for planning and mapping only. The default model, dependency choice, SDK/direct HTTP approach, API key value reading, real network calls, live smoke, and raw output retention remain pending or explicitly not approved.

## Assumptions

- Decision package fields should remain human-review Markdown, not machine approval artifacts.
- Existing readiness JSON remains the fail-closed machine-readable readiness input.
- Decision package revisions should prefer precise approval status fields over ambiguous checkboxes.

## Non-goals

- No real provider adapter implementation.
- No provider SDK or production dependency.
- No `pyproject.toml` or dependency file changes.
- No API key value reads or API key requests.
- No provider network calls.
- No live smoke.
- No raw provider output persistence.
- No formal apply, patch acceptance, or publication.

## Proposed Technical Approach

Revise the provider adapter decision package template with the product-owner decisions and explicit non-approvals. Extend the adapter design document with an SDK vs direct HTTP comparison, adapter mapping plan, CLI safety valve design, and CI policy. Update tests and repo memory to keep the docs aligned.

## Task Breakdown

- [x] Update provider adapter decision package template.
- [x] Add SDK vs direct HTTP comparison and mapping/safety/CI sections to adapter design.
- [x] Update docs tests for new approval fields and boundaries.
- [x] Update repo memory and milestone review.
- [x] Run validation.

## Likely Files Changed

- `docs/templates/PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md`
- `docs/designs/2026-05-20-first-provider-adapter-design.md`
- `tests/unit/test_provider_adapter_design_docs.py`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-20-provider-approval-package-revision.md`
- `docs/exec-plans/active/2026-05-20-provider-approval-package-revision.md`

## Validation Plan

- [x] focused docs test
- [x] full unit tests
- [x] compile check
- [x] whitespace diff check
- [x] local trial fixture smoke
- [x] architecture scan

## Review Gate Impact

Post-Gate 7 provider-readiness design milestone. This clarifies approval semantics before real provider implementation begins.

## Risks

- Template wording could be mistaken as live-call approval unless explicit non-approvals remain prominent.
- OpenAI-targeted planning could be mistaken as dependency approval unless SDK/direct HTTP decision status is explicit.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because this is a decision package and design revision only.

## Definition of Done

- Product-owner preparation approval is recorded without approving real provider calls.
- OpenAI is recorded as first provider target for planning only.
- Dependency choice remained pending comparison at the time of this completed plan.
- SDK/direct HTTP comparison exists.
- Tests and checks pass.

Superseded note:

- On 2026-05-20, the product owner adopted the OpenAI official SDK as the future first-provider integration style. Dependency file changes and actual provider implementation remain separately unapproved.
