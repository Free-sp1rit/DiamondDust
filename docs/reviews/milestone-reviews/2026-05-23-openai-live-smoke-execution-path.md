# Milestone Review: OpenAI Live Smoke Execution Path

## Scope Reviewed

- `openai-extract-units` live-smoke execution path.
- OpenAI adapter live-approval handoff.
- AI run-log and validated extraction artifact persistence after provider
  execution.
- Provider-free regression tests for default, preview, dry-run, and CI behavior.

## Product Goal Alignment

This milestone makes the first approved OpenAI fixture smoke executable through
DiamondDust instead of an external script. It keeps the run limited to
`extract_units`, the approved fixture essay, and AI working artifacts.

## Architecture Boundary Compliance

- OpenAI SDK imports remain isolated to the AI adapter module.
- CLI orchestration calls the application provider extraction boundary.
- Storage adapters persist `_ai_runs` and `_ai_suggestions/extractions` when
  called by the CLI path.
- The adapter still does not construct `KnowledgeUnit`, `Relation`, or
  `KnowledgePatch`, and does not persist artifacts directly.
- Formal vault writes remain out of scope.

## Cohesion Assessment

The change is cohesive around one user-visible command path. Preview, dry-run,
readiness, and local trial paths remain unchanged except for shared command
support.

## Coupling Assessment

Provider-specific execution remains coupled only to the OpenAI adapter and
OpenAI-specific CLI command. Domain core, storage adapters, and artifact
contracts do not receive OpenAI SDK types.

## Data and Schema Safety

The live path persists only existing AI working artifact types:

- `ai_run_log`
- `validated_extraction_output`, only after typed validation passes

Raw provider request and response bodies are not persisted. Patch generation,
patch acceptance, formal apply, and publication remain disabled.

## AI Output Boundary

Provider output must pass source binding and typed extraction validation before
it becomes a validated extraction artifact. Failed provider responses create a
failed run log and do not produce candidate notes or patches.

## Tests and Evaluation

- Focused OpenAI adapter safety and CLI tests: 25 tests passed.
- Full unit test suite: 242 tests passed.
- Compile check: `python3 -m compileall src tests` passed.
- Diff check: `git diff --check` passed.
- Local trial fixture smoke: passed with 12 provider-free artifacts,
  `provider_called: false`, and `formal_write_performed: false`.
- Architecture boundary scan: 0 violations.

## Dependency and Portability Impact

No new dependency is added. The existing OpenAI SDK dependency remains isolated
to the AI adapter layer.

## Risks

- The live command could be mistaken for recurring provider approval.
- The first smoke can still fail because the external provider rejects the
  structured-output request shape or model availability.
- Cost is enforced as a configured run guard, not as a pre-call pricing oracle.

## Required Changes Before Continuing

- Keep the actual live smoke unrun until explicitly requested.

## Optional Improvements

- Add a dedicated live-smoke result report after the first execution.
- Add post-smoke product-owner feedback capture for extraction quality.

## Escalation Requests

None for this implementation milestone. Actual live smoke execution remains a
separate operator action.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked
