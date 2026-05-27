# Milestone Review: Trial Client

## Scope Reviewed

- `src/diamonddust/interface/trial_client.py`
- `src/diamonddust/cli.py`
- Trial client tests
- Trial client guide
- Durable context updates

## Product Goal Alignment

Pass. The client shifts the project from more core feature expansion toward
small-user real-note feedback on the existing extraction pipeline.

## Architecture Boundary Compliance

Pass with follow-up. The new code lives in the interface layer and invokes the
existing CLI command through a subprocess boundary. Provider SDK imports remain
inside AI adapter modules. The interface does not mutate formal vault files.

## Cohesion Assessment

Pass. Trial UI, local secret-file loading, command construction, artifact
summary, empty-extraction quality classification, and feedback persistence are
kept in one interface module.

## Coupling Assessment

Pass with follow-up. The client is coupled to the DeepSeek trial command and its
artifact shape, intentionally for this first trial stage. Future provider choice
should introduce a small provider-runner abstraction before adding more
providers to the UI.

## Data and Schema Safety

Pass. The client reads persisted validated extraction artifacts and run logs
without changing their schema. Feedback artifacts are local manual-trial files
and do not change formal domain schema.

## AI Output Boundary

Pass. The client can trigger approved DeepSeek `extract_units` calls but cannot
generate patches, accept patches, formal apply, or publish. Empty extractions
are surfaced as product-quality failures even when typed schema validation
passes. Unit candidates are rendered as structured fields plus expandable JSON
so trial reviewers can inspect machine structure instead of prose-only cards.

## Tests and Evaluation

- Focused trial-client and CLI tests: passed.
- Full unit suite: 268 tests passed.
- Compile check: passed.
- `git diff --check`: passed.
- Local trial fixture smoke: passed; `provider_called: false`,
  `formal_write_performed: false`.
- Architecture boundary scan: 0 critical violations.
- Manual client smoke: `/api/status` served successfully from the local client.

## Dependency and Portability Impact

No dependency was added or changed. The client uses Python standard-library HTTP
serving and browser APIs.

## Risks

- The subprocess command wrapper can drift from CLI flags.
- The first client is DeepSeek-only.
- Quality classification is intentionally narrow and does not replace human
  review.

## Required Changes Before Continuing

- None.

## Optional Improvements

- Add provider selection after another provider has enough real-note evidence.
- Add a richer quality rubric once users produce several feedback artifacts.

## Escalation Requests

None.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked
