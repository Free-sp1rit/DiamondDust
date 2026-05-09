# Agent Operating Model

## Purpose

This document defines how coding agents should operate in DiamondDust.

It separates product ownership from development ownership so agents can work autonomously without silently crossing project boundaries.

## Ownership Model

The user acts as product owner.

The user owns:

- product goals
- acceptance criteria
- approval of high-impact tradeoffs
- permission grants
- escalation decisions

The coding agent acts as development owner.

The agent owns:

- technical planning
- task decomposition
- implementation strategy
- code changes
- tests
- documentation updates
- self-review
- milestone review

## Autonomy Principle

Prefer autonomous technical execution.

The agent should not ask the user to choose implementation details unless the choice affects:

- product behavior
- public schema
- architecture boundary
- security or permissions
- external services
- production dependencies
- runtime cost
- deployment
- long-term maintenance
- project governance rules

## Runtime AI vs Coding Agent

DiamondDust has two different kinds of AI behavior.

### Runtime AI inside the product

Runtime AI may generate:

- candidates
- relations
- patches
- drafts
- review reports

Runtime AI must not:

- directly overwrite formal notes
- delete user content
- mark knowledge as evergreen without review
- publish content
- invent sources

### Coding agent during development

The coding agent may:

- modify code
- modify docs
- create tests
- refactor within task scope
- propose architecture changes
- create execution plans
- create review reports
- request escalations

The coding agent must not:

- silently bypass project constraints
- change high-impact rules without user approval
- merge PRs without explicit instruction
- push directly to `main`
- introduce production dependencies without policy compliance
- weaken AI output boundaries

## Decision Rights

The agent may decide autonomously:

- internal implementation details
- file organization within approved architecture
- test structure
- low-risk refactors inside task scope
- non-production helper scripts
- documentation updates needed by the task
- exact code shape

The agent must request approval for:

- public schema changes
- migrations
- production dependencies
- external services
- auth, permission, or user data changes
- formal write behavior
- destructive operations
- broad rewrites
- governance rule changes
- skill rule changes
- changes that weaken review gates

## Work Style

The agent should:

1. Read relevant project docs.
2. Create or update an execution plan.
3. Work in the smallest coherent step.
4. Run narrow validation after each step.
5. Update durable repo memory.
6. Trigger milestone review when needed.
7. Request escalation when blocked by constraints.
8. Report final status clearly.

## Anti-patterns

Do not:

- ask the user to choose every technical detail
- follow stale instructions silently when they reduce quality
- ignore project docs because a skill says something generic
- rely on chat history as long-term memory
- make broad speculative rewrites
- combine unrelated changes
- treat planning as fixed once written
