# Execution Plan: OpenAI API Key Environment Variable Decision

## Product Goal

Record the product-owner decision to approve `DIAMONDDUST_OPENAI_API_KEY` as
the future OpenAI adapter API key environment variable name without approving
API key value reads.

## Current Understanding

The product owner approved the environment variable name and explicitly kept key
values out of packages, repo files, logs, and persisted artifacts. Preview
commands and current real-provider-run settings must not read the key value.

## Assumptions

- This is a decision-recording task.
- API key value reading remains unapproved.
- Real provider adapter implementation remains unapproved.
- Network calls and live smoke remain unapproved.

## Non-goals

- Do not read or request an API key value.
- Do not add provider implementation code.
- Do not modify dependency files.
- Do not make network calls.
- Do not run live smoke.

## Proposed Technical Approach

Update the provider decision package template, first-provider adapter design,
repo memory, and design-doc tests so the approved env var name is explicit
while key-value handling remains fail-closed.

## Task Breakdown

- [x] Update API key env var fields in the decision package template.
- [x] Update design documentation and implementation gates.
- [x] Update repo memory and open questions.
- [x] Update design-doc tests.
- [x] Run focused and full validation.

## Likely Files Changed

- `docs/templates/PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md`
- `docs/designs/2026-05-20-first-provider-adapter-design.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
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

Post-Gate 7 provider-readiness design update. This records a secret-name
decision but does not read or persist secrets.

## Risks

- Env var name approval could be mistaken for secret read approval.
- Future implementation must avoid SDK default secret lookup behavior unless it
  is explicitly constrained to the approved env var during an approved live run.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

No escalation is needed because the product owner directly approved the env var
name and this task only records that decision.

## Definition of Done

- Decision package and design docs record `DIAMONDDUST_OPENAI_API_KEY`.
- Key reading, logging, and persistence remain explicitly forbidden.
- Repo memory reflects that API key value reading is still pending.
- Tests and checks pass.
