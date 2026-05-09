# Review Gates

## Purpose

Review gates keep DiamondDust reviewable, reversible, and architecturally coherent.

There are two types of gates:

1. Product and architecture phase gates
2. Development-agent milestone review gates

## Product and Architecture Phase Gates

### Gate 0: Direction Freeze

Pass conditions:

- Project Charter approved
- MVP Scope approved
- Non-goals approved

Blockers:

- Product goal unclear
- MVP includes P1/P2 features
- AI write boundary unclear

### Gate 1: Architecture Freeze

Pass conditions:

- Architecture boundary approved
- Domain model approved
- Data contract approved
- AI pipeline contract approved

Blockers:

- domain core depends on provider SDK
- storage is not portable
- patch workflow undefined

### Gate 2: Schema Skeleton

Pass conditions:

- KnowledgeUnit schema implemented
- Relation schema implemented
- KnowledgePatch schema implemented
- validation tests pass

Blockers:

- untyped JSON crosses domain boundary
- relation types are open-ended
- no schema tests

### Gate 3: Markdown Ingestion

Pass conditions:

- Markdown essay can be read
- frontmatter can be parsed
- source refs can be created
- content hash can be computed

Blockers:

- original essay can be overwritten
- no source ref preservation

### Gate 4: AI Extraction Proposal

Pass conditions:

- LLM output is structured
- output passes schema validation
- invalid output fails safely
- run log is recorded

Blockers:

- free-form AI output becomes internal data
- no prompt version
- no run log

### Gate 5: Patch Review

Pass conditions:

- KnowledgePatch can be generated
- patch diff can be inspected
- accept/reject works
- formal vault changes only after acceptance

Blockers:

- AI writes directly to formal notes
- patch cannot be rolled back

### Gate 6: Blog Draft

Pass conditions:

- blog draft generated from accepted units
- claim inventory exists
- unsupported claims are reported
- quality report exists

Blockers:

- draft invents sources
- no evidence coverage report

### Gate 7: MVP Release

Pass conditions:

- 5 sample essays pass end-to-end
- tests pass
- docs reflect behavior
- no critical architecture violations

## Development-Agent Milestone Reviews

Milestone reviews are required before continuing when:

- a module reaches a stable boundary
- a public API or schema is introduced or changed
- a storage format or migration is introduced
- an AI task contract is introduced or changed
- an adapter boundary is introduced or changed
- a production dependency or external service is added
- auth, permissions, user data, or formal write behavior is affected
- two consecutive fixes fail
- coupling risk or architecture drift appears
- a review gate is about to be marked passed

Milestone reviews should be written under:

```text
docs/reviews/milestone-reviews/
```

Use:

```text
docs/templates/MILESTONE_REVIEW_TEMPLATE.md
```

## Milestone Review Checks

Each milestone review must check:

- scope reviewed
- product goal alignment
- architecture boundary compliance
- cohesion
- coupling
- data and schema safety
- AI output boundary
- tests and evaluation
- dependency and portability impact
- risks
- required changes before continuing
- optional improvements
- escalation requests

## Passing a Gate

A gate may be marked passed only when:

- pass conditions are satisfied
- blockers are absent or explicitly waived by the user
- required tests or validation pass
- milestone review is complete when applicable
- docs reflect current behavior

## Waiving a Blocker

A blocker may be waived only by explicit user approval.

A waiver must record:

- blocker
- reason for waiver
- risk
- fallback or follow-up task
- user approval reference

Record waivers in:

```text
docs/context/decisions.md
```
