# Skill Usage Policy

## Purpose

This document defines the boundary between project docs and reusable skills.

## Core Boundary

Project docs describe what DiamondDust is.

Skills describe how an agent should perform a repeatable workflow.

Use this rule:

```text
docs/ save project facts.
skills save reusable processes.
AGENTS.md saves navigation and operating rules.
tests/lint/CI save hard invariants.
scripts/ save deterministic mechanical actions.
```

## What Belongs in Docs

Put these in `docs/`:

- product mission
- MVP scope
- non-goals
- architecture boundaries
- domain model
- schema contracts
- AI output boundary
- storage rules
- review gates
- dependency rules
- Git workflow
- project-specific decisions
- execution plans
- milestone reviews

Docs are the source of truth for DiamondDust-specific facts.

## What Belongs in Skills

Put these in skills:

- turning product specs into execution plans
- milestone review workflow
- PR review workflow
- debugging failed tests
- schema migration planning
- security review workflow
- release note generation
- constraint escalation workflow

Skills should be reusable across tasks and should not duplicate DiamondDust-specific product truth.

## Initial Recommended Skills

### `spec-to-plan`

Use when turning a product request, issue, or rough feature into an execution plan.

The skill should:

1. Read `AGENTS.md`.
2. Read relevant `docs/`.
3. Create or update a plan in `docs/exec-plans/active/`.
4. Identify risks, tests, review gates, and escalation needs.
5. Avoid implementation unless explicitly requested.

### `milestone-review`

Use when a module, API, schema, adapter, or workflow reaches a stable boundary.

The skill should:

1. Read relevant docs and changed files.
2. Review cohesion, coupling, architecture boundaries, tests, security, and risks.
3. Write a review under `docs/reviews/milestone-reviews/`.
4. Identify required changes before continuing.

### `constraint-escalation`

Use when a rule, skill, instruction, dependency limit, architecture constraint, or tool limitation appears to reduce delivery quality.

The skill should:

1. Identify the conflict.
2. Explain quality impact.
3. Propose the smallest permission or rule change.
4. Provide risks and fallback.
5. Wait for user approval before modifying high-impact constraints.

### `pr-review`

Use before PR readiness.

The skill should:

1. Inspect diff.
2. Check tests and docs.
3. Confirm review gate impact.
4. Identify risks and missing validation.
5. Prepare PR notes.

### `debug-failure`

Use when tests, lint, schema validation, patch validation, or CI fails.

The skill should:

1. Read failing output.
2. Identify likely cause.
3. Apply the smallest coherent fix.
4. Re-run the narrowest relevant validation.
5. Escalate after repeated failures.

## Conflict Resolution

When skill guidance conflicts with project docs:

1. Prefer project docs for DiamondDust-specific facts.
2. Prefer hard rules enforced by tests, lint, CI, and review gates.
3. Use skill guidance only as workflow help.
4. If the conflict reduces delivery quality, create an escalation request.

## Skill Creation Threshold

Do not create a skill for one-off guidance.

Create or update a skill when:

- the same workflow is used repeatedly
- the same prompt is being reused
- the same mistakes recur
- the workflow requires ordered steps
- the workflow benefits from bundled templates or scripts

## Skill Anti-patterns

Do not:

- copy all project docs into a skill
- put product truth in a skill
- let skills override architecture boundaries silently
- let skills request unnecessary user confirmation
- make skills so rigid that they prevent better implementation choices
- create many low-value skills before workflows are proven
