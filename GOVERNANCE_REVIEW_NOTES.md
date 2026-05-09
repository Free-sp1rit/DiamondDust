# Governance Constraint Review

## Summary

The existing governance set is strong on product invariants, AI output boundaries, architecture separation, schema validation, and Git review flow.

The main gap is that it does not clearly separate:

1. runtime AI autonomy inside DiamondDust
2. coding-agent autonomy during development
3. project docs as source of truth
4. skills as reusable workflows
5. hard constraints vs flexible defaults
6. escalation requests vs silent compromise

This revision keeps the existing product boundaries and adds agent-development governance without weakening the formal knowledge patch safety model.

## Key Findings

### 1. `AGENTS.md` was too mixed

It mixed mission, architecture rules, AI output rules, Git rules, and task process in one file.

The revised version keeps it as a navigation and operating-control document, while moving detailed agent autonomy, skill usage, execution planning, memory, and escalation into separate docs.

### 2. Runtime autonomy and development autonomy were ambiguous

The original language said not to introduce agent autonomy before patch review is stable. That is correct for runtime product behavior, but it can accidentally restrict the coding agent.

The revision clarifies that runtime AI autonomy and development-agent autonomy are separate.

### 3. Skills were missing

There was no clear rule for when to use skills, what belongs in a skill, and what belongs in docs.

The revision adds `docs/12_SKILL_USAGE_POLICY.md`.

### 4. Planning and repo memory were missing

The existing workflow required task specs and PRs, but did not define durable execution plans or context compression.

The revision adds `docs/13_EXECUTION_PLAN_AND_MEMORY_POLICY.md` and templates.

### 5. Escalation was missing

The original rules could cause the agent to produce lower-quality work when blocked by stale or over-restrictive guidance.

The revision adds `docs/14_CONSTRAINT_ESCALATION_POLICY.md`.

### 6. Review gates were product-phase oriented only

The original `09_REVIEW_GATES.md` was useful, but it did not define development-agent milestone reviews.

The revision keeps the product gates and adds milestone review triggers.

## Files Changed

Replacements:

- `AGENTS.md`
- `README.md`
- `目录结构.md`
- `docs/07_QUALITY_AND_TEST_POLICY.md`
- `docs/08_DEPENDENCY_AND_PORTABILITY_POLICY.md`
- `docs/09_REVIEW_GATES.md`
- `docs/10_GIT_WORKFLOW.md`

New files:

- `docs/11_AGENT_OPERATING_MODEL.md`
- `docs/12_SKILL_USAGE_POLICY.md`
- `docs/13_EXECUTION_PLAN_AND_MEMORY_POLICY.md`
- `docs/14_CONSTRAINT_ESCALATION_POLICY.md`
- `docs/templates/EXECUTION_PLAN_TEMPLATE.md`
- `docs/templates/MILESTONE_REVIEW_TEMPLATE.md`
- `docs/templates/ESCALATION_REQUEST_TEMPLATE.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`

## Recommended Adoption Order

1. Replace `AGENTS.md`.
2. Add the new docs and templates.
3. Replace `README.md` documentation map.
4. Replace `09_REVIEW_GATES.md`.
5. Replace `07`, `08`, and `10` after a quick read.
6. Ask Codex to run one dry-run planning task using the new rules before product implementation.
