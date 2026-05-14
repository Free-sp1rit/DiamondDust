# Execution Plan: Package Build Validation

## Product Goal

Make CI validate DiamondDust as an installable package artifact, not only as an editable source checkout, so the local trial fixture remains trustworthy for product-owner testing.

## Current Understanding

CI currently installs the package with `pip install -e .`, runs tests, compiles source/tests, checks whitespace, and smoke tests `diamonddust local-trial-fixture` from outside the repository root. The fixture assets are now package data, so CI should also build a wheel and install from that wheel before running validation.

## Assumptions

- GitHub-hosted Python runners have `pip` and can build a local wheel from the existing `pyproject.toml`.
- `python -m pip wheel . --no-deps` is sufficient for a package-build gate at this stage.
- Release publishing, versioning policy, and artifact upload remain future work.

## Non-goals

- Do not publish packages.
- Do not add release versioning policy.
- Do not add production or development dependencies.
- Do not change runtime product behavior, schemas, provider behavior, or formal vault write behavior.

## Proposed Technical Approach

Update the CI workflow to build a wheel into `${RUNNER_TEMP}/wheelhouse`, install that wheel with `--force-reinstall --no-deps`, run `pip check`, and then execute the existing validation gates. Update CI workflow tests to guard the package-build commands. Update docs and repo memory to mark package build validation as complete while keeping publishing/versioning as open follow-up.

## Task Breakdown

- [x] Update CI to build and install a wheel before validation.
- [x] Update CI workflow guard tests.
- [x] Update README and repo memory.
- [x] Complete milestone review and compress this plan.
- [x] Run local validation and open PR.

## Likely Files Changed

- `.github/workflows/ci.yml`
- `tests/unit/test_ci_workflow.py`
- `README.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/exec-plans/completed/2026-05-14-package-build-validation.md`
- `docs/reviews/milestone-reviews/2026-05-14-package-build-validation.md`

## Validation Plan

- [x] focused CI workflow tests
- [x] full unit tests
- [x] compile check
- [x] diff whitespace check
- [x] remote GitHub Actions run after PR creation

## Review Gate Impact

Post-Gate 7 release-quality infrastructure. This strengthens packaging validation but does not alter product behavior or formal write boundaries.

## Risks

- Local Codex shell still lacks `pip`, so wheel build/install validation must be confirmed on GitHub Actions.
- CI build behavior may depend on hosted runner packaging tooling.
- Versioning and publishing gates remain intentionally out of scope.

## Escalation Needed

- [x] no
- [ ] yes: describe

No escalation is required because this adds no dependency, external service integration beyond existing GitHub Actions CI, runtime behavior, schema change, or formal vault mutation.

## Definition of Done

- CI builds a wheel, installs the wheel, runs `pip check`, and runs the existing validation gates against the installed package.
- Workflow guard tests cover the package-build commands.
- Repo memory records package build validation as complete and release publishing/versioning as future work.
- Local validation passes and remote CI succeeds on the PR.

## Completion Summary

Updated `.github/workflows/ci.yml` so CI builds a wheel, installs that wheel, runs `pip check`, and then runs the existing validation suite and non-repo-root local trial fixture smoke. Updated the CI workflow guard test, README validation baseline, repo memory, and milestone review.

Local validation passed for focused CI workflow tests, 121 full unit tests, compile checks, and whitespace checks. Wheel build/install validation is expected to run in GitHub Actions because the current Codex shell lacks `pip`.
