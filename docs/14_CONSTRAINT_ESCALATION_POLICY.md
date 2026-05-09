# Constraint Escalation Policy

## Purpose

This document defines how a coding agent should respond when project constraints, skills, tool limits, or instructions appear to reduce delivery quality.

## Principle

Project delivery quality is the goal, but the agent must not silently ignore, weaken, or bypass constraints.

When a constraint blocks good delivery, request permission to change the constraint or scope.

Do not self-approve high-impact changes.

## When to Escalate

Escalate when the task appears to require:

- modifying `AGENTS.md`
- modifying skill behavior
- weakening a review gate
- changing architecture boundaries
- changing public schema
- adding a production dependency
- adding an external service
- network access not currently allowed
- destructive file or data operations
- auth, permission, payment, or user data changes
- large rewrites
- removing tests
- changing formal write behavior
- merging or pushing to protected branches
- implementation that contradicts current docs

Escalate also when following a constraint would force:

- worse architecture
- hard vendor lock-in
- duplicated domain logic
- untyped JSON through the domain layer
- direct AI mutation of formal knowledge
- missing tests for changed behavior
- hidden risk to user data

## What Does Not Require Escalation

No escalation is required for:

- internal implementation details
- low-risk refactors inside task scope
- tests for changed behavior
- docs updates that reflect implemented behavior
- non-production helper scripts
- plan revisions
- moving completed plans to completed memory
- formatting or minor cleanup inside touched files

## Escalation Request Format

Use:

```text
docs/templates/ESCALATION_REQUEST_TEMPLATE.md
```

An escalation request must include:

1. blocked goal
2. conflicting constraint
3. why following it reduces quality
4. recommended change
5. affected files or rules
6. risks if approved
7. safe fallback if denied
8. exact user decision needed

## Allowed Work While Waiting

While waiting for approval, the agent may continue only on unaffected work.

The agent may:

- write tests
- improve docs
- prepare non-invasive refactors
- explore alternatives
- update the execution plan
- document the blocker

The agent must not:

- implement the blocked change
- weaken the constraint
- change permissions
- add the production dependency
- modify formal write behavior
- push or merge protected branches

## Outcome Handling

If approved:

1. Update the relevant docs, skill, rules, or plan.
2. Record the decision in `docs/context/decisions.md`.
3. Continue implementation.
4. Include the approval in final status.

If denied:

1. Use the safe fallback.
2. Record the limitation.
3. Continue within the approved boundary.
4. Do not repeatedly ask for the same escalation unless new evidence appears.
