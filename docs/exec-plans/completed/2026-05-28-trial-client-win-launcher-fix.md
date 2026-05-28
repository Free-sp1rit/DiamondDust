# Execution Plan: Trial Client Win Launcher Fix

## Product Goal

Make the trial-client alpha package reliably diagnosable and easier to start on
Win11 after the `.cmd` launcher failed to run the program in a real trial
environment.

## Current Understanding

The current launcher assumes `python` is available, opens the browser before
the backend is confirmed running, and exits immediately on setup failures. In a
double-click Win11 flow, that can look like "nothing happened" or a browser page
that cannot connect.

## Assumptions

- The failure may be caused by missing `python` on `PATH`, failed venv
  creation, failed dependency installation, or backend startup failure.
- A robust alpha launcher should keep the console open on failure and write a
  local diagnostic log.
- The fix should not change provider behavior, formal write behavior, or add
  dependencies.

## Non-goals

- Do not create a native installer.
- Do not change trial-client provider execution semantics.
- Do not read API keys during launcher setup.
- Do not publish a release from this fix unless separately requested.

## Proposed Technical Approach

Update the Win11 `.cmd` and PowerShell launchers to:

- create a local `.diamonddust-trial/logs/` directory,
- log setup and server output,
- prefer the Windows `py -3.11` launcher when available, with `python` as
  fallback,
- run from the package/repo root,
- keep the terminal open with a clear message when setup or server startup
  fails,
- open the browser after setup succeeds and immediately before backend start.

Update generated package launcher text and docs to tell users where logs live.

## Task Breakdown

- [x] Create the execution plan.
- [x] Harden Win11 `.cmd` launcher.
- [x] Harden Win11 PowerShell launcher.
- [x] Update generated `START_HERE.md` and distribution docs.
- [x] Add tests for launcher/package guidance where practical.
- [x] Rebuild package smoke.
- [x] Run validation and prepare PR.

## Likely Files Changed

- `scripts/windows/start-trial-client.cmd`
- `scripts/windows/start-trial-client.ps1`
- `src/diamonddust/interface/trial_distribution.py`
- `docs/guides/trial-client-alpha-distribution.md`
- `docs/guides/trial-client.md`
- `tests/unit/test_trial_distribution.py`
- `docs/context/project-state.md`

## Validation Plan

- [x] focused distribution tests
- [x] full unit test suite
- [x] frontend build
- [x] package generation smoke
- [x] compile check
- [x] diff check

## Review Gate Impact

Post-Gate 7 alpha distribution fix. Milestone review is not required unless the
fix changes package boundaries or dependency behavior.

## Risks

- We cannot execute `.cmd` natively inside the current Linux workspace.
- First-run installation can still fail without Python or network access, but
  the failure should now be visible and logged.

## Escalation Needed

Does this require user approval?

- [x] no: this is a direct fix for the approved alpha distribution flow and
  does not add dependencies or broaden runtime safety boundaries.

## Definition of Done

- Launchers leave a useful log on Win11 failures.
- Launchers do not silently close on setup errors.
- The generated package includes updated first-run troubleshooting guidance.
- Tests and local packaging checks pass.
