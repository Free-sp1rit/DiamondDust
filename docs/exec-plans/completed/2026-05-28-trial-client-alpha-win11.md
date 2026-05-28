# Execution Plan: Trial Client Alpha Win11 Distribution

## Product Goal

Create a simple, approachable trial client suitable for a small number of
Win11 users so DiamondDust can gather real-note feedback before expanding core
knowledge features.

## Current Understanding

The current Python stdlib browser client can save a local DeepSeek API key, run
real-note extraction, show historical artifacts, and collect feedback. It has
validated the core provider path, but the product now needs easier distribution
and a more maintainable frontend surface for broader trial use.

This stage prioritizes real user trial throughput over new core knowledge
capabilities.

## Assumptions

- DeepSeek remains the trial provider for this alpha client.
- The backend remains Python and continues to own provider execution,
  artifact loading, feedback persistence, and safety boundaries.
- The frontend may be introduced as a separate maintainable app, but domain
  rules and provider logic must not move into frontend code.
- Win11 support means an easy local launcher and documentation for testers, not
  a signed installer yet.

## Non-goals

- Do not build a full note editor.
- Do not formal apply, publish, or record patch acceptance.
- Do not directly mutate formal knowledge files from LLM output.
- Do not move domain validation, provider execution, or persistence ownership
  into frontend code.
- Do not introduce provider-side tools, web search, file search, or runtime
  agent autonomy.
- Do not build a complete packaged desktop installer in this stage.

## Proposed Technical Approach

Keep the existing Python trial-client service as the local backend and add API
support for trial workspaces, note import, and optional static frontend serving.
Create a React + Vite + TypeScript frontend source tree that consumes the local
API and can later replace the embedded fallback HTML without changing the
provider/domain/storage boundaries.

Provide Win11 launcher scripts that start the existing Python backend with the
default local trial configuration. The scripts should not require users to type
long Python commands.

## Task Breakdown

- [x] Add mutable trial workspace configuration and status reporting.
- [x] Add a note import API that writes Markdown into the selected trial input
      directory.
- [x] Add optional static frontend serving while preserving the embedded HTML
      fallback.
- [x] Create a React/Vite trial frontend source tree.
- [x] Add Win11 launcher scripts and update the trial client guide.
- [x] Add unit tests for workspace, import, and static frontend behavior.
- [x] Run validation and update durable context docs.

## Likely Files Changed

- `src/diamonddust/interface/trial_client.py`
- `src/diamonddust/cli.py`
- `tests/unit/test_trial_client.py`
- `frontend/trial-client/`
- `scripts/windows/`
- `docs/guides/trial-client.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/exec-plans/active/2026-05-28-trial-client-alpha-win11.md`

## Validation Plan

- [x] focused trial-client tests
- [x] focused CLI tests if CLI behavior changes
- [x] frontend build
- [x] full unit suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan

## Review Gate Impact

This stage affects the trial-client interface, local secret handling UX, and
frontend dependency surface. It requires a milestone review before being marked
complete.

## Risks

- Frontend framework files may be mistaken for domain ownership unless the API
  boundary stays explicit.
- Win11 launcher scripts can become stale if CLI flags change.
- Workspace import could write outside the selected trial directory if path
  validation is weak.
- Local key writing remains less secure than shell-managed secrets, even though
  it improves trial convenience.

## Escalation Needed

Does this require user approval?

- [x] yes: the product owner approved entering this stage and requested a
      maintainable frontend framework plus a Win11-oriented trial distribution.

## Definition of Done

- The backend can configure a trial workspace and import Markdown notes through
  local API calls.
- A React/Vite trial frontend exists as the maintainable client surface.
- Win11 users have a short launcher path and guide.
- Existing provider/domain/storage boundaries remain intact.
- Tests pass and no formal vault writes are introduced.
