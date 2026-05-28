# Execution Plan: Win Trial Alpha Startup Fixes

## Product Goal

Make the Win11 alpha trial package start reliably in real user environments
without manual script editing, and make key storage/path behavior clear enough
for successful provider calls.

## Current Understanding

A Win11 tester has Python 3.13.5 installed, but the `.cmd` launcher did not
select it and then executed `-m venv` with an empty Python command because of
batch variable expansion inside a parenthesized block. The package docs also
describe the Unix-like `~/.config/diamonddust/provider-secrets.env` path, which
is confusing in the Win11 alpha package and may contribute to failed provider
commands when users think the key was saved elsewhere.

## Assumptions

- The alpha package should support Python 3.13, 3.12, and 3.11.
- Bundling a Python runtime is too heavy for this source-based alpha package
  and should wait for a future native installer decision.
- The Win alpha launcher may store trial secrets under the local package
  runtime directory for usability, as long as docs warn users not to share that
  directory after saving a key.
- Port 8765 conflicts are possible and should be handled by automatic fallback
  where practical.

## Non-goals

- Do not add bundled Python binaries.
- Do not create a native installer.
- Do not add production dependencies.
- Do not change provider adapter behavior, raw output retention, formal apply,
  patch acceptance, or publication.
- Do not read API keys during launcher setup.

## Proposed Technical Approach

- Harden `scripts/windows/start-trial-client.cmd` with delayed expansion,
  Python discovery for `py -3.13`, `py -3.12`, `py -3.11`, `py -3`, and
  `python`, and safe command invocation.
- Add simple port selection in the `.cmd` launcher: use
  `DIAMONDDUST_TRIAL_PORT` if set, otherwise choose the first non-listening
  port from 8765 through 8775.
- Align the PowerShell launcher with the same Python version candidates, local
  alpha secrets path, and dynamic port behavior.
- Pass `--secrets-env-file` from Win launchers to
  `.diamonddust-trial/secrets/provider-secrets.env`.
- Exclude `.diamonddust-trial/` from packages and document the generated
  runtime directory.
- Add tests for generated package guidance and local alpha runtime path
  exclusions where useful.

## Task Breakdown

- [x] Create execution plan.
- [x] Fix `.cmd` Python selection and delayed expansion.
- [x] Add `.cmd` port fallback and local secrets path.
- [x] Fix PowerShell Python candidates, port fallback, and local secrets path.
- [x] Update package docs and generated `START_HERE.md`.
- [x] Update package exclusion policy for runtime dirs.
- [x] Add/update tests.
- [x] Run validation and package smoke.
- [x] Commit, push, and open PR.

## Likely Files Changed

- `scripts/windows/start-trial-client.cmd`
- `scripts/windows/start-trial-client.ps1`
- `src/diamonddust/interface/trial_client.py`
- `src/diamonddust/interface/trial_distribution.py`
- `docs/guides/trial-client.md`
- `docs/guides/trial-client-alpha-distribution.md`
- `tests/unit/test_trial_client.py`
- `tests/unit/test_trial_distribution.py`
- `docs/context/project-state.md`
- `docs/context/completed-milestones.md`

## Validation Plan

- [ ] focused trial-client tests
- [x] focused trial-distribution tests
- [x] full unit test suite
- [x] frontend build
- [x] package generation smoke
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke

## Review Gate Impact

Post-Gate 7 alpha distribution fix. No milestone review is required unless
package boundaries, dependency behavior, or provider safety boundaries change.

## Risks

- `.cmd` and `.ps1` cannot be executed natively in this Linux workspace, so
  validation is by tests, package generation, and static review.
- Local package-root secret storage is less safe if a tester shares the unpacked
  directory after saving a key; docs must make that clear.

## Escalation Needed

Does this require user approval?

- [x] no: the user explicitly requested project fixes, commit, and PR. No new
  dependency, bundled runtime, formal write, provider policy expansion, or
  publication behavior is introduced.

## Definition of Done

- Win launchers support Python 3.13/3.12/3.11 without manual editing.
- Win launchers use a concrete alpha secrets path that the backend receives.
- Win launchers can avoid an occupied default port.
- Package docs and generated instructions match actual Win launcher behavior.
- Tests and package smoke pass.
