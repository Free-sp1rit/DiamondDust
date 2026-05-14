# Execution Plan: CI Validation

## Product Goal

Make DiamondDust's current local validation suite run automatically for pull requests and task-branch pushes so local trial work is safer to review and merge.

## Current Understanding

The repository has an installable Python package, a `diamonddust` CLI, 114 unit tests, compile checks, whitespace checks, and a local trial fixture smoke path. These checks are currently run locally and documented in milestone reviews, but no CI workflow exists.

## Assumptions

- GitHub Actions is the intended CI surface for this GitHub-hosted repository.
- CI may use hosted Ubuntu runners and `actions/checkout` / `actions/setup-python` without adding product runtime dependencies.
- Python 3.11 is the minimum supported runtime, and Python 3.12 should be used as an early portability check.
- Branch protection configuration is outside this repository-file task.

## Non-goals

- Do not add provider calls, formal vault writes, publication behavior, UI, or product runtime dependencies.
- Do not configure GitHub branch protection or repository settings.
- Do not introduce lint/typecheck tools that require new dependencies.
- Do not change public schemas or artifact formats.

## Proposed Technical Approach

Add a GitHub Actions workflow that runs on pull requests and pushes. The workflow installs the package in editable mode, runs unit tests, runs compile checks, runs `git diff --check`, and runs the installed `diamonddust local-trial-fixture` smoke command against a temporary vault root.

Add a repository test that checks the workflow continues to include the intended validation gates. Update README and repo memory to record CI as the current automation baseline.

## Task Breakdown

- [x] Add GitHub Actions workflow for Python validation.
- [x] Add unit test coverage for CI workflow gate contents.
- [x] Update README and repo context docs.
- [x] Complete milestone review and compress this plan.
- [x] Run local validation.

## Likely Files Changed

- `.github/workflows/ci.yml`
- `tests/unit/test_ci_workflow.py`
- `README.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-14-ci-validation.md`
- `docs/exec-plans/completed/2026-05-14-ci-validation.md`

## Validation Plan

- [x] unit tests: `PYTHONPATH=src python3 -m unittest discover -s tests`
- [x] integration/smoke: module local trial fixture command
- [x] compile: `python3 -m compileall src tests`
- [x] whitespace: `git diff --check`
- [x] manual review: inspect workflow scope and dependency impact

## Review Gate Impact

This is a post-Gate 7 release-quality infrastructure task. It does not change product behavior, public schema, AI output boundary, formal write behavior, or runtime architecture. It strengthens the quality gate used before PR review/merge.

## Risks

- GitHub Actions behavior cannot be fully verified until the branch is pushed and the workflow runs remotely.
- Hosted runner Python availability may change over time.
- Branch protection is not configured by repository files, so CI can exist without being a required GitHub merge check.

## Escalation Needed

- [x] no
- [ ] yes: describe

The user explicitly set full CI as the target. The implementation uses repository files only, adds no production dependency, and does not change runtime product behavior.

## Definition of Done

- CI workflow exists and covers install, unit tests, compile checks, whitespace checks, and local trial fixture smoke.
- Workflow gate contents are covered by a local test.
- README and repo memory describe the new CI baseline and remaining branch-protection follow-up.
- Local validation passes.

## Completion Summary

Added `.github/workflows/ci.yml` with a Python 3.11/3.12 matrix that runs editable install, unit tests, compile checks, whitespace checks, and the installed `diamonddust local-trial-fixture` smoke command. Added `tests/unit/test_ci_workflow.py` to guard the workflow's core gates. Updated README, decisions, open questions, project state, completed milestones, and milestone review.

Local validation passed for 119 unit tests, compile checks, whitespace checks, and the module-based local trial fixture smoke. The current Codex shell lacks `pip` and `ensurepip`, so editable install validation is left to the first remote GitHub Actions run.
