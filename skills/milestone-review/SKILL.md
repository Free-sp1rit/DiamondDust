---
name: milestone-review
description: "Run DiamondDust milestone reviews when a module, public API, schema, storage format, AI task contract, adapter boundary, workflow, review gate, dependency, permission surface, formal write behavior, or repeated failed fix reaches a stable or risky boundary. Use before marking a review gate passed or continuing past a required milestone trigger."
---

# Milestone Review

## Read

- `AGENTS.md`
- `docs/09_REVIEW_GATES.md`
- `docs/templates/MILESTONE_REVIEW_TEMPLATE.md`
- Relevant architecture, domain, schema, AI pipeline, quality, dependency, Git, and execution-plan docs
- Changed files, test results, active plan, and relevant repo memory

## Inputs

- Scope to review
- Diff or changed files
- Validation results and known failures
- Relevant review gate or milestone trigger
- Open risks, blockers, or escalation requests

## Outputs

- A milestone review under `docs/reviews/milestone-reviews/`
- Required changes before continuing, optional improvements, and review decision
- Updates to plans or repo memory when the review changes project state

## Workflow

1. Identify the milestone trigger and the exact scope being reviewed.
2. Read only the docs and changed files needed for that scope.
3. Check product alignment, architecture boundaries, cohesion, coupling, data and schema safety, AI output boundary, tests, dependencies, portability, risks, and unresolved escalations.
4. Write the review using the project template.
5. Mark the decision as pass, pass with follow-up, or blocked according to evidence.
6. Do not waive blockers, pass gates, or approve high-impact tradeoffs without explicit user approval.
7. If the review is blocked, update the active plan or blocker context with the next safe action.

## Does Not Constrain

- Specific implementation technique, library, framework, package layout, or test runner.
- The agent's ability to recommend refactors, tests, or safer sequencing.
- Future product scope beyond the reviewed milestone.
- User-owned approvals, waivers, and product tradeoffs.
