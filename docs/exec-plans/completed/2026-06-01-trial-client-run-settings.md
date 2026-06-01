# Execution Plan: Trial Client Run Settings And Frontend Parity

## Product Goal

Bring the React trial-client frontend up to the embedded trial webpage feature
level and let the client remember user-selected run settings for model,
timeout seconds, max output tokens, and per-run cost limit.

## Current Understanding

The embedded fallback webpage already exposes runtime controls for model,
timeout, maximum output, and cost limit, plus feedback, boundary, and artifact
panels. The React frontend served from `frontend/trial-client/dist` currently
only sends the selected model and therefore lags behind the fallback trial page.

Run settings should persist locally so trial users do not need to re-enter
their preferred model and limits after refresh or restart.

## Assumptions

- Settings are non-secret local preferences and can be stored as JSON under the
  ignored `.diamonddust-trial/` runtime directory.
- API keys remain separate in the local secrets file and must never be stored in
  the settings file.
- Settings persistence should be backend-owned so both built React and embedded
  fallback clients can share it.

## Non-goals

- Do not read or write API key values beyond existing approved trial-client
  paths.
- Do not make provider calls during implementation validation.
- Do not persist raw provider request or response bodies.
- Do not introduce a new frontend framework or production dependency.
- Do not change DeepSeek provider approvals, retry behavior, or formal write
  behavior.

## Proposed Technical Approach

Add a small trial-client run-settings contract in the interface layer:

- `TrialRunSettings` for model, timeout seconds, max tokens, and cost limit.
- Package-local settings file at `.diamonddust-trial/trial-client-settings.json`.
- `status()` includes current `run_settings` and `run_settings_file`.
- `POST /api/run-settings` validates and persists user preferences.
- `run_extraction()` uses saved settings as defaults and persists settings
  included with a run request.

Update the React frontend to:

- Initialize runtime controls from backend `run_settings`.
- Expose model, timeout, maximum output, and cost limit controls.
- Save settings explicitly and include settings in extraction requests.
- Add feedback, boundary, and artifact panels to catch up with embedded trial
  webpage functionality.

## Task Breakdown

- [x] Add backend run-settings persistence and status exposure.
- [x] Add `/api/run-settings` endpoint and unit tests.
- [x] Update React frontend runtime controls and persistence flow.
- [x] Add React panels for feedback, boundaries, and artifacts.
- [x] Update docs/context and milestone review.
- [x] Run focused backend tests, frontend build, full tests, compile, diff,
  local fixture smoke, and architecture scan.
- [x] Commit and open PR.

## Likely Files Changed

- `src/diamonddust/interface/trial_client.py`
- `frontend/trial-client/src/App.tsx`
- `frontend/trial-client/src/styles.css`
- `tests/unit/test_trial_client.py`
- `docs/guides/trial-client.md`
- `docs/guides/trial-client-alpha-distribution.md`
- `docs/context/project-state.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/<date>-trial-client-run-settings.md`

## Validation Plan

- [x] focused trial-client unit tests
- [x] frontend build
- [x] full unit test suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan
- [x] milestone review

## Review Gate Impact

This changes trial-client local preference persistence and frontend behavior, so
a milestone review is required before completion.

## Risks

- Settings files could become stale or invalid if edited manually. The backend
  should fall back to defaults for unreadable persisted settings.
- React and embedded fallback clients could drift again. Backend-owned settings
  reduce that risk.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

The user requested planning and implementation, and the change stays within the
existing trial-client stack and local runtime boundary.

## Definition of Done

- React frontend exposes and sends model, timeout seconds, max tokens, and cost
  limit.
- Trial client can persist and reload those settings locally.
- React frontend can save feedback and inspect boundaries/artifact paths.
- No secrets, raw provider bodies, real trial artifacts, or formal vault writes
  are introduced.
