---
name: spec-to-plan
description: "Turn product requests, issues, rough feature briefs, or ambiguous tasks into DiamondDust execution plans. Use when Codex needs to create or update a plan under docs/exec-plans/active, identify assumptions, review gates, validation, risks, escalation needs, and definition of done before non-trivial work."
---

# Spec To Plan

## Read

- `AGENTS.md`
- `docs/13_EXECUTION_PLAN_AND_MEMORY_POLICY.md`
- `docs/09_REVIEW_GATES.md`
- `docs/14_CONSTRAINT_ESCALATION_POLICY.md`
- Relevant product, architecture, schema, quality, dependency, or workflow docs for the task
- Existing active or completed plans if the task continues prior work

## Inputs

- User request, issue, rough feature, bug report, or implementation brief
- Current repo state and branch
- Any relevant acceptance criteria, constraints, or prior decisions

## Outputs

- A new or updated execution plan in `docs/exec-plans/active/`
- A concise summary of assumptions, risks, review gate impact, validation plan, and escalation needs
- No implementation unless the user explicitly requested implementation in the same task

## Workflow

1. Inspect repo status and read the docs needed to understand the task boundary.
2. Decide whether to create a new plan or update an existing active plan.
3. Use `docs/templates/EXECUTION_PLAN_TEMPLATE.md` as the plan shape.
4. Define product goal, current understanding, assumptions, non-goals, approach, task breakdown, likely files, validation, risks, gate impact, escalation needs, and done conditions.
5. Preserve the coding agent's technical autonomy: choose implementation strategy, task decomposition, and validation approach within approved project constraints.
6. Escalate before any high-impact behavior: governance changes, public schema changes, production dependencies, external services, security or permission changes, destructive operations, formal write behavior changes, or review gate weakening.
7. If implementation is requested, proceed from the plan and revise it when evidence changes.

## Does Not Constrain

- Concrete programming language, library, framework, package layout, or implementation design.
- Test runner, CI system, or command choices beyond project docs and available tooling.
- Internal technical sequencing when multiple safe paths satisfy the same product goal.
- Product scope or high-impact tradeoffs owned by the user.
