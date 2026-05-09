# Quality and Test Policy

## Test Philosophy

A change is not safe unless it is covered by validation, tests, or an explicit review gate.

## Required Test Layers

### Unit Tests

Must cover:

- domain schemas
- relation validation
- patch validation
- status rules
- path generation
- tag normalization

### Integration Tests

Must cover:

- Markdown essay → extraction result
- extraction result → KnowledgePatch
- KnowledgePatch → candidate Markdown output
- accepted units → blog draft

### Golden Tests

Use fixed essay fixtures to detect behavior drift.

### Regression Tests

Every bug fix must include a failing test or fixture that reproduces the bug.

## AI Evaluation Metrics

Track where possible:

- schema pass rate
- source_ref preservation
- duplicate unit rate
- unsupported claim rate
- relation validity
- patch validity
- blog draft evidence coverage

## Agent Review as Quality Control

Milestone review is required when a change affects:

- public schema
- storage format
- AI output boundary
- architecture boundary
- formal write behavior
- external service dependency
- module cohesion or coupling
- review gate pass/fail status

Milestone review does not replace tests. It documents risks, tradeoffs, and unresolved questions.

## Merge Blockers

Do not accept changes that:

- bypass schema validation
- write formal notes directly from LLM output
- add provider dependency to domain core
- change public schema without migration note
- remove tests without explanation
- silently weaken review gates
- leave unresolved escalation requests for high-impact changes
