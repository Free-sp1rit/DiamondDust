# Milestone Review: Trial Client Run Settings And Frontend Parity

## Scope Reviewed

Backend run-settings persistence, `POST /api/run-settings`, status exposure,
React trial-client runtime controls, feedback/boundary/artifact panels,
embedded fallback page parity, alpha distribution docs, and regression tests.

## Product Goal Alignment

Pass. The React frontend no longer lags behind the embedded trial page for
core trial controls, and users can keep preferred DeepSeek model, timeout,
max-output, and cost-limit settings across refreshes and restarts.

## Architecture Boundary Compliance

Pass. Run settings are local interface-layer preferences under
`.diamonddust-trial/`. Provider-specific execution remains in the existing
DeepSeek adapter and CLI path. Domain core, storage adapters, formal vault code,
and artifact contracts are not coupled to the React frontend.

## Cohesion Assessment

Pass. Settings validation and persistence are backend-owned through
`TrialRunSettings`, so React and embedded fallback clients share one contract.
The React changes are contained to the trial-client UI surface.

## Coupling Assessment

Pass. No new frontend framework, provider SDK, or domain dependency was added.
The React client speaks only the local trial-client JSON API.

## Data and Schema Safety

Pass. The new settings file is local runtime state, excluded with
`.diamonddust-trial/`, and contains no API key or provider raw response body.
No AI artifact schema or formal vault schema changed.

## AI Output Boundary

Pass. Provider calls still occur only when users explicitly run extraction.
Raw provider requests/responses remain unpersisted by default. Feedback capture
continues to write review artifacts only and does not record patch acceptance,
formal apply, or publication.

## Tests and Evaluation

Pass.

- Focused trial-client/distribution tests passed.
- React frontend build passed.
- Full unit suite passed: 293 tests.
- Compile check passed.
- Local trial fixture smoke passed with `provider_called: false` and
  `formal_write_performed: false`.
- Architecture scan reported `critical_architecture_violations=0`.
- Diff check passed.

## Dependency and Portability Impact

Pass. No new production or frontend dependency was added. The alpha package
continues to exclude `.diamonddust-trial/` runtime state.

## Risks

- Manually corrupted settings files are ignored and defaults are used, which is
  safer for trial users but may hide a manual edit mistake.
- The React UI has more controls and should be exercised in the next packaged
  Win11 alpha before broader user handoff.

## Required Changes Before Continuing

None.

## Optional Improvements

- Add a small UI indicator when persisted settings were loaded from disk.
- Add editable issue tags beyond the current verdict-derived feedback tag.

## Escalation Requests

None.

## Review Decision

- [x] pass
- [ ] pass with follow-up
- [ ] blocked
