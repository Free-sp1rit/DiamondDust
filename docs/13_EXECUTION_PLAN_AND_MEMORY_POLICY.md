# Execution Plan and Memory Policy

## Purpose

This document defines how coding agents should plan work, persist durable context, and compress completed development state.

## Execution Plans

For any non-trivial task, create or update a plan under:

```text
docs/exec-plans/active/
```

Use:

```text
docs/templates/EXECUTION_PLAN_TEMPLATE.md
```

A task is non-trivial if it:

- changes more than one file
- changes public behavior
- touches schema, storage, AI output, or architecture
- requires tests
- affects docs
- introduces a new module or adapter
- has meaningful uncertainty

## Plan Ownership

The agent owns the technical plan.

The user owns product intent and approval of high-impact tradeoffs.

The plan is not a contract. It is a live navigation document.

If implementation evidence shows the plan is wrong, revise the plan before continuing.

## Required Plan Sections

Each plan must include:

- product goal
- current understanding
- assumptions
- non-goals
- proposed technical approach
- task breakdown
- likely files changed
- validation plan
- risks
- review gate impact
- escalation needs
- definition of done

## Stage Progression

When executing a plan:

1. Work in the smallest coherent step.
2. Keep implementation autonomy unless escalation is required.
3. Run narrow validation after each step.
4. Update the plan checklist.
5. Do not start a new major step while relevant tests are failing.
6. Revise the plan when reality contradicts it.
7. Run full validation at the end.
8. Self-review the diff before reporting completion.

## Repo Memory

Durable development context must live in repo docs, not chat history.

Use:

```text
docs/context/project-state.md
docs/context/decisions.md
docs/context/open-questions.md
docs/context/completed-milestones.md
```

## What to Persist

Persist:

- current project state
- completed milestones
- accepted technical decisions
- public API or schema changes
- migration decisions
- known risks
- unresolved blockers
- follow-up tasks
- validation results that affect future work

Do not persist:

- raw chain-of-thought
- large tool logs
- temporary debugging noise
- irrelevant failed experiments
- repetitive command output
- stale assumptions

## Context Compression

When a stage is complete, compress it into a short summary and move the plan from:

```text
docs/exec-plans/active/
```

to:

```text
docs/exec-plans/completed/
```

The completion summary must preserve:

1. original goal
2. final implementation
3. files changed
4. public interfaces changed
5. important decisions
6. known risks
7. follow-up tasks
8. validation results

## Blocked Work

If blocked, move or copy the plan to:

```text
docs/exec-plans/blocked/
```

and record:

- blocker
- attempted approaches
- required user decision
- safe fallback
- next action after approval
