# Milestone Review: OpenAI Manual Live Smoke Decision Package

## Scope Reviewed

- OpenAI live-smoke decision package documentation.
- OpenAI live-smoke readiness policy updates.
- Follow-on blocked execution plan for one manual fixture smoke.
- Provider decision template and first-provider adapter design updates.

## Product Goal Alignment

This milestone advances DiamondDust from pre-live-smoke readiness to a recorded
product-owner decision for exactly one controlled OpenAI `extract_units` fixture
smoke. It preserves the MVP boundary by keeping patch acceptance, formal apply,
publication, provider-side tools, and real user essay externalization out of
scope.

## Architecture Boundary Compliance

- Provider-specific behavior remains behind the existing AI adapter boundary.
- The readiness gate records decisions and does not construct provider clients.
- Storage adapters remain responsible for persistence during future execution.
- The decision package and readiness report do not read API keys, call OpenAI,
  make network requests, or write formal vault files.

## Cohesion Assessment

The change is cohesive around one concern: recording and validating the exact
decision set for a first manual live smoke. The blocked execution plan is kept
separate so approval records are not confused with execution records.

## Coupling Assessment

The readiness policy now contains OpenAI-specific constants for the approved
first smoke. This is intentional provider-specific policy in the application
readiness layer and does not leak SDK types into domain, storage, or formal
vault code.

## Data and Schema Safety

No public formal vault schema changes are introduced. The decision package uses
existing provider decision field names and documents the revised retention
semantics: raw provider request/response bodies remain unpersisted, while hash
and metadata retention is allowed for the first fixture smoke.

## AI Output Boundary

No AI/provider output is generated in this milestone. The future live smoke
must still pass source binding and typed runtime validation before any provider
output becomes internal extraction data.

## Tests and Evaluation

- Focused provider readiness, CLI, and provider adapter design-doc tests:
  44 tests passed.
- Full unit test suite: 240 tests passed.
- Compile check: `python3 -m compileall src tests` passed.
- Diff check: `git diff --check` passed.
- Local trial fixture smoke: passed with 12 provider-free artifacts,
  `provider_called: false`, and `formal_write_performed: false`.
- Architecture boundary scan: 0 violations.

## Dependency and Portability Impact

No new dependency is added. The existing OpenAI SDK dependency remains isolated
to the AI adapter implementation from the previous milestone.

## Risks

- The decision package could be mistaken for execution approval unless the
  blocked execution plan boundary remains explicit.
- The one-smoke model approval for `gpt-5.5` could be mistaken for a default
  model for broader live usage.
- Hash/metadata retention must not drift into raw provider request/response
  persistence.

## Required Changes Before Continuing

- Keep the live-smoke execution plan blocked until the product owner explicitly
  asks to run it.

## Optional Improvements

- Add a durable executed-live-smoke report artifact after the first smoke is
  run.
- Add a post-smoke product-owner feedback checklist based on real provider
  output quality.

## Escalation Requests

None for this decision-recording milestone. Actual live-smoke execution remains
separately blocked until explicitly requested.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked
