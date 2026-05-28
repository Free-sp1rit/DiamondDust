# Execution Plan: Trial Client Alpha Distribution

## Product Goal

Create a simple, repeatable alpha distribution path for a small number of
Win11 trial users so DiamondDust can collect real-note feedback on core
extraction quality.

## Current Understanding

The merged trial client already supports DeepSeek model presets, local API key
setup, configurable workspaces, Markdown import, historical artifact loading
and deletion, source context display, structured unit review cards, and Win11
launcher scripts. The missing piece is a trial distribution workflow that can
package the client predictably, explain first-run usage, and prove that local
secrets and generated vault artifacts are excluded.

## Assumptions

- This is an alpha trial distribution, not a stable product release.
- The distribution can remain source-based and local-first for this stage.
- Trial users may have Python installed, but should not need Node/npm to run
  the client if the maintainer builds the React frontend before packaging.
- Generated packages should not be committed to the repository.
- No provider calls, API key reads, formal apply, patch acceptance, or
  publication are required to build a distribution package.

## Non-goals

- Do not create a GitHub Release or tag unless separately requested.
- Do not build a native installer.
- Do not add production dependencies.
- Do not include API key values, local secret files, `knowledge-vault/`, test
  run artifacts, `node_modules/`, `.venv/`, or `.git/` in the package.
- Do not weaken existing provider, formal-write, or raw-output safety
  boundaries.

## Proposed Technical Approach

Add a small standard-library distribution builder under the interface layer and
a thin script entrypoint that:

- verifies required distribution inputs are present,
- optionally builds the React frontend,
- stages an allowlisted package tree,
- writes first-run instructions and a manifest,
- blocks forbidden secret/runtime paths from entering the package, and
- writes a zip artifact under an ignored output directory or caller-supplied
  output root.

Update the Win11 launcher scripts to automatically serve the built React
frontend when present and make double-click startup easier for trial users.

## Task Breakdown

- [x] Add the alpha distribution execution plan.
- [x] Add an importable trial distribution builder and package manifest.
- [x] Add a packaging script for maintainers.
- [x] Improve Win11 launcher behavior for packaged use.
- [x] Add trial distribution documentation.
- [x] Add tests for package contents, manifest, and secret/runtime exclusions.
- [x] Generate a local alpha package artifact for inspection.
- [x] Run validation and write milestone review.
- [x] Update durable context and complete the plan.

## Likely Files Changed

- `src/diamonddust/interface/trial_distribution.py`
- `scripts/package-trial-client-alpha.py`
- `scripts/windows/start-trial-client.cmd`
- `scripts/windows/start-trial-client.ps1`
- `docs/guides/trial-client.md`
- `docs/guides/trial-client-alpha-distribution.md`
- `tests/unit/test_trial_distribution.py`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-28-trial-distribution-alpha.md`

## Validation Plan

- [x] focused trial distribution unit tests
- [x] full unit test suite
- [x] frontend build
- [x] package generation smoke
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan
- [x] milestone review

## Review Gate Impact

Post-Gate 7 trial distribution milestone. Milestone review is required because
the task affects user-facing distribution, local secret boundaries, and trial
workflow safety.

## Risks

- A source-based alpha package still depends on local Python and internet
  access for installing Python dependencies if the user has not set up a venv.
- Win11 execution policy can block PowerShell scripts; a `.cmd` fallback should
  remain available.
- The alpha package may be mistaken for a stable release unless docs and naming
  stay explicit.
- Browser-client convenience could encourage real-note sharing before quality
  feedback is reviewed; this stage remains trial-only.

## Escalation Needed

Does this require user approval?

- [x] no: the product owner requested completion of the trial distribution
  stage, and the approach does not add dependencies, publish externally, or
  weaken safety boundaries.

## Definition of Done

- A maintainer can generate an alpha package with one command.
- The generated package contains built client assets, Python source, launcher
  scripts, docs, and a manifest.
- The generated package excludes secrets, `knowledge-vault/`, `.git/`,
  `.venv/`, `node_modules/`, raw provider output, and generated AI artifacts.
- The package has a simple first-run guide for Win11 trial users.
- Tests and validation pass.
- The PR is ready for review, but no formal GitHub Release is created.
