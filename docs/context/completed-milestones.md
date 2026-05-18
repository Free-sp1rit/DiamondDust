# Completed Milestones

Record completed development milestones and links to reviews here.

## 2026-05-10 — Project Context Initialized

- Scope: Read `AGENTS.md`, `GOVERNANCE_REVIEW_NOTES.md`, `README.md`, `目录结构.md`, and `docs/*`.
- Outcome: Established the current repo-memory baseline in `docs/context/`.
- Gate impact: Supports Gate 0 Direction Freeze and Gate 1 Architecture Freeze, but does not mark either gate passed.
- Validation: Manual documentation review and Git status check.
- Review: No milestone review required because no module, public API, schema, storage format, AI task contract, dependency, or formal write behavior was introduced.

## 2026-05-10 — Minimal Governance Skills Initialized

- Scope: Created repo-local `SKILL.md` files for planning, escalation, milestone review, PR review, and Git workflow.
- Outcome: Added lightweight reusable workflows under `skills/` without scripts, assets, references, or project-fact duplication.
- Gate impact: Supports Gate 0 Direction Freeze and Gate 1 Architecture Freeze, but does not mark either gate passed.
- Validation: Manual skill review, directory shape check, and Git status check.
- Review: No milestone review required because no runtime module, public API, schema, storage format, AI task contract, dependency, or formal write behavior was introduced.

## 2026-05-10 — Initialization Acceptance Completed

- Scope: Validated project context initialization, governance skill boundaries, Gate 2 planning readiness, constraint escalation behavior, Git workflow, and memory persistence.
- Outcome: Wrote `docs/reviews/milestone-reviews/2026-05-10-initialization-acceptance.md`.
- Score: 18/20.
- Review decision: pass with follow-up.
- Gate impact: Gate 2 planning may begin; Gate 2 implementation is not yet recommended.
- Validation: Manual review of governance docs, repo-local skills, context memory, Git status, and acceptance report.
- Follow-up: Prepare governance initialization for PR review, confirm Gate 0/Gate 1 status, confirm skill discovery path, and create a Gate 2 execution plan before implementation.

## 2026-05-10 — Governance Initialization PR Merged

- Scope: Product owner completed PR review and merge for the initialization branch.
- Outcome: `main` now includes governance docs, context memory, review templates, initialization acceptance review, and minimal governance skills.
- Gate impact: Gate 2 planning may begin; Gate 2 implementation still requires Gate 0/Gate 1 status confirmation and a Gate 2 execution plan.
- Workflow update: Future development may run GitHub PR preflight, push current task branches, and use `gh pr create`, but must not use `gh pr merge`, push `main`, or force push.
- Follow-up: Run proxy and GitHub preflight before PR creation; if it fails, stop and output an escalation request.

## 2026-05-10 — GitHub PR Workflow Verified

- Scope: Verified proxy, GitHub authentication, repository lookup, current task branch push, and PR creation for the workflow-permissions branch.
- Outcome: Created PR #2 for `docs/github-workflow-permissions`.
- PR: `https://github.com/Free-sp1rit/DiamondDust/pull/2`
- Boundary respected: Did not merge, did not push `main`, did not force push, did not print token values in the final report, and did not start Gate 2 implementation.
- Follow-up: Keep using preflight before future PR creation in workspace-write mode.

## 2026-05-10 — Gate 2 Schema Skeleton Completed

- Scope: Implemented typed domain schemas and validation tests for `KnowledgeUnit`, `Relation`, and `KnowledgePatch`.
- Outcome: Added standard-library domain schema package under `src/diamonddust/domain/`.
- Review: `docs/reviews/milestone-reviews/2026-05-10-gate-2-schema-skeleton.md`.
- Review decision: pass.
- Gate impact: Gate 2 Schema Skeleton is passed; next candidate milestone is Gate 3 Markdown Ingestion.
- Validation: 12 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.

## 2026-05-10 — Gate 3 Markdown Ingestion Completed

- Scope: Implemented read-only Markdown ingestion with frontmatter parsing, source ref creation, and content hashing.
- Outcome: Added a standard-library storage adapter under `src/diamonddust/storage/`.
- Review: `docs/reviews/milestone-reviews/2026-05-10-gate-3-markdown-ingestion.md`.
- Review decision: pass with follow-up.
- Gate impact: Gate 3 Markdown Ingestion is passed for the MVP skeleton; next candidate milestone is Gate 4 AI Extraction Proposal.
- Validation: 19 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Reconsider parser dependencies only after fixture evidence requires richer Markdown or YAML behavior.

## 2026-05-10 — Gate 4 AI Extraction Proposal Completed

- Scope: Implemented provider-neutral validation for structured AI extraction proposal output.
- Outcome: Added typed AI run metadata, run logs, extraction proposals, validation results, output hashing, and fail-safe invalid-output handling under `src/diamonddust/ai/`.
- Review: `docs/reviews/milestone-reviews/2026-05-10-gate-4-ai-extraction-proposal.md`.
- Review decision: pass with follow-up.
- Gate impact: Gate 4 AI Extraction Proposal is passed for the MVP skeleton; next candidate milestone is Gate 5 Patch Review.
- Validation: 27 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add durable AI run log storage and provider adapter interfaces before real model calls are enabled.

## 2026-05-10 — Gate 5 Patch Review Completed

- Scope: Implemented application-layer patch generation, diff inspection, rollback instructions, and accept/reject review results.
- Outcome: Added a patch review workflow under `src/diamonddust/application/`.
- Review: `docs/reviews/milestone-reviews/2026-05-10-gate-5-patch-review.md`.
- Review decision: pass with follow-up.
- Gate impact: Gate 5 Patch Review is passed for the MVP skeleton; next candidate milestone is Gate 6 Blog Draft.
- Validation: 38 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add patch persistence, duplicate ID/path checks, and storage apply/revert behavior before formal vault mutation is enabled.

## 2026-05-10 — Gate 6 Blog Draft Completed

- Scope: Implemented deterministic blog draft generation, claim inventory, unsupported claim reporting, and blog quality reports.
- Outcome: Added a blog draft workflow under `src/diamonddust/application/`.
- Review: `docs/reviews/milestone-reviews/2026-05-10-gate-6-blog-draft.md`.
- Review decision: pass with follow-up.
- Gate impact: Gate 6 Blog Draft is passed for the MVP skeleton; next candidate milestone is Gate 7 MVP Release.
- Validation: 46 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add durable draft persistence/export, provider-backed editorial drafting, and golden fixture quality evaluation later.

## 2026-05-10 — Gate 7 MVP Release Readiness Completed

- Scope: Implemented a deterministic release readiness harness over five sample Markdown essays.
- Outcome: Added application-level readiness reporting, failure-safe sample results, source ID mismatch checks, a minimal domain architecture import scan, five fixtures, and tests.
- Review: `docs/reviews/milestone-reviews/2026-05-10-gate-7-mvp-release-readiness.md`.
- Review decision: pass with follow-up.
- Gate impact: Gate 7 MVP Release readiness is passed for the current MVP skeleton; post-Gate 7 hardening should focus on durable AI working artifacts, candidate Markdown rendering/export, formal vault apply/revert safety, product-owner-approved golden essays, and CI.
- Validation: 53 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Keep provider calls, formal vault mutation, and publishing behind explicit review and approval boundaries.

## 2026-05-11 — Candidate Markdown Export Completed

- Scope: Implemented rendering and export of candidate Markdown notes from validated `KnowledgePatch` create-note operations.
- Outcome: Added a storage adapter that writes candidate notes and a manifest under `_ai_suggestions/candidate-notes/<patch_id>/` while preserving formal target paths as metadata only.
- Review: `docs/reviews/milestone-reviews/2026-05-11-candidate-markdown-export.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; improves MVP candidate Markdown output without enabling formal vault mutation.
- Validation: 59 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add raw patch persistence, review report rendering, duplicate target checks, and formal apply/revert in separate reviewed milestones.

## 2026-05-11 — Review Report Rendering Completed

- Scope: Implemented rendering and export of patch review reports from validated `KnowledgePatch` values.
- Outcome: Added a storage adapter that writes reports under `_ai_reports/patch-reviews/<patch_id>.md` with patch diff summaries, candidate note links, risks, rollback steps, and explicit review boundaries.
- Review: `docs/reviews/milestone-reviews/2026-05-11-review-report-rendering.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; improves MVP review report output without enabling formal vault mutation.
- Validation: 65 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add raw patch persistence and a combined review package writer before formal apply/revert.

## 2026-05-11 — Review Package Persistence Completed

- Scope: Implemented a combined writer for raw patch JSON, candidate Markdown notes, and patch review reports.
- Outcome: Added a storage adapter that writes review package artifacts under `_ai_suggestions/patches/`, `_ai_suggestions/candidate-notes/`, and `_ai_reports/patch-reviews/` without formal vault mutation.
- Review: `docs/reviews/milestone-reviews/2026-05-11-review-package-persistence.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; improves review artifact traceability before formal apply/revert.
- Validation: 70 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add AI run log and blog draft persistence, then duplicate path/ID checks before formal apply/revert.

## 2026-05-11 — AI Run Log Persistence Completed

- Scope: Implemented rendering and writing of typed AI run logs under `_ai_runs/`.
- Outcome: Added a storage adapter that persists passed and failed run logs with run metadata, output hash, validation status, `created_at`, and optional cache metadata while excluding raw AI output.
- Review: `docs/reviews/milestone-reviews/2026-05-11-ai-run-log-persistence.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; improves AI pipeline traceability before real provider integration.
- Validation: 76 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add durable blog draft package persistence and artifact schema versioning before external CLI/UI consumers depend on artifact JSON shape.

## 2026-05-11 — Blog Draft Package Persistence Completed

- Scope: Implemented rendering and writing of blog draft packages under AI working directories.
- Outcome: Added a storage adapter that persists draft Markdown under `_ai_suggestions/blog-drafts/<draft_id>/draft.md` and quality reports under `_ai_reports/blog-quality/<draft_id>.md` while marking `formal_write: false` and `publication_ready: false`.
- Review: `docs/reviews/milestone-reviews/2026-05-11-blog-draft-persistence.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; improves local trial output without enabling publication or formal vault mutation.
- Validation: 81 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add local trial harness or CLI and explicit artifact versioning before external consumers depend on draft artifact shape.

## 2026-05-11 — Local Trial Harness Completed

- Scope: Implemented local trial orchestration for one Markdown essay plus structured extraction JSON.
- Outcome: Added an application harness and module-based CLI that write AI run logs, review packages, candidate Markdown notes, patch review reports, blog draft packages, and blog quality reports under AI working directories without provider calls or formal vault mutation.
- Review: `docs/reviews/milestone-reviews/2026-05-11-local-trial-harness.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; improves product-owner trialability before real provider integration and formal apply/revert.
- Validation: 85 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add example extraction JSON fixtures, artifact schema versioning, product-owner-approved golden essays, CI, and formal apply/revert safety checks.

## 2026-05-11 — Artifact Schema Versioning Completed

- Scope: Added explicit artifact schema version markers to persisted AI working artifacts.
- Outcome: Introduced shared `artifact_schema_version: 0.1.0` metadata for AI run logs, raw patch JSON, candidate Markdown notes and manifests, patch review reports, blog drafts, and blog quality reports.
- Review: `docs/reviews/milestone-reviews/2026-05-11-artifact-schema-versioning.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; stabilizes local trial output formats before broader CLI/UI consumption.
- Validation: 89 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add example local trial extraction JSON fixtures, golden essays, CI, and future compatibility handling when artifact import/replay exists.

## 2026-05-11 — Local Trial Fixtures Completed

- Scope: Added a checked-in local trial Markdown essay and matching structured extraction JSON.
- Outcome: The README local trial command now points to runnable fixtures under `tests/fixtures/local_trial/`, and tests verify the fixture pair validates and writes reviewable AI working artifacts through the CLI.
- Review: `docs/reviews/milestone-reviews/2026-05-11-local-trial-fixtures.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; improves product-owner trialability before real provider integration.
- Validation: 91 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add standalone extraction JSON schema notes, product-owner-approved golden essays, CI, and formal apply/revert safety checks.

## 2026-05-12 — Local Trial Extraction JSON Notes Completed

- Scope: Added user-facing documentation for the structured extraction JSON input accepted by the local trial CLI.
- Outcome: Added `docs/guides/local-trial-extraction-json.md`, linked it from README, and added tests that validate the guide's embedded example against the current extraction boundary.
- Review: `docs/reviews/milestone-reviews/2026-05-12-local-trial-extraction-json-notes.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; improves local trial usability without changing runtime schema or enabling provider calls.
- Validation: 93 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add product-owner-approved golden essays, CI, and formal apply/revert safety checks in separate reviewed milestones.

## 2026-05-12 — Formal Vault Conflict Checks Completed

- Scope: Added read-only conflict preflight checks for future formal vault apply behavior.
- Outcome: Added a storage adapter that reports existing formal target paths, existing formal unit IDs, duplicate patch target paths, and duplicate patch unit IDs without mutating vault files.
- Review: `docs/reviews/milestone-reviews/2026-05-12-vault-conflict-checks.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening and Gate 5 follow-up; improves formal write safety prerequisites without enabling formal writes.
- Validation: 99 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add explicit formal apply/revert boundaries, rollback/write-failure tests, product-owner-approved golden essays, and CI in separate reviewed milestones.

## 2026-05-12 — Formal Apply Dry-Run Plan Completed

- Scope: Added non-mutating formal apply dry-run plans for conflict-free patches.
- Outcome: Added storage adapter planning types that list planned formal note files, content hashes, and rollback steps while preserving the no-write formal vault boundary.
- Review: `docs/reviews/milestone-reviews/2026-05-12-formal-apply-plan.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening and Gate 5 follow-up; improves formal apply readiness without enabling formal writes.
- Validation: 105 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add explicit user acceptance handoff, formal apply/revert execution, rollback/write-failure tests, product-owner-approved golden essays, and CI in separate reviewed milestones.

## 2026-05-14 — Local Trial Feedback Report Completed

- Scope: Added a first-open feedback report artifact for local trial runs.
- Outcome: Local trials now write `_ai_reports/local-trials/<trial_id>.md` for passed and safely finalized failed runs, include it in CLI output, and preserve provider-free/no-formal-write boundaries.
- Review: `docs/reviews/milestone-reviews/2026-05-14-local-trial-feedback-report.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; improves readiness for controlled product-owner feedback before provider calls or formal vault mutation.
- Validation: 108 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Use the feedback report in a controlled trial, then decide which feedback prompts should become release criteria or golden fixture expectations.

## 2026-05-14 — Local Trial Feedback Capture Completed

- Scope: Added human-fillable feedback capture fields and a user-facing local trial feedback guide.
- Outcome: Local trial feedback reports now include a `Feedback Capture` section for product-owner trial notes, and README links to `docs/guides/local-trial-user-feedback.md`.
- Review: `docs/reviews/milestone-reviews/2026-05-14-local-trial-feedback-capture.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; improves controlled user trial feedback without enabling provider calls, formal vault writes, or publication.
- Validation: 111 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Run a controlled product-owner trial and decide which feedback fields should become release criteria or golden fixture expectations.

## 2026-05-14 — CLI Trial Entrypoint Completed

- Scope: Added minimal Python package metadata and standard CLI entrypoints for local trial usage.
- Outcome: `pyproject.toml` now exposes `diamonddust = "diamonddust.cli:main"`, `python3 -m diamonddust` delegates to the same CLI, and README/guides show the installable command plus development fallback.
- Review: `docs/reviews/milestone-reviews/2026-05-14-cli-trial-entrypoint.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; improves product-owner trial ergonomics without changing provider, formal vault, or publication behavior.
- Validation: 113 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed.
- Dependency impact: No runtime dependency was added; packaging metadata uses the standard setuptools build backend for editable installs.
- Follow-up: Add CI/package install checks before treating packaging metadata as a release contract.

## 2026-05-14 — Local Trial Fixture Command Completed

- Scope: Added a one-command fixture shortcut for provider-free local trial runs.
- Outcome: `diamonddust local-trial-fixture` runs the checked-in trial essay and extraction JSON through the existing local trial path, defaults output to ignored `knowledge-vault/`, and preserves no-provider/no-formal-write boundaries.
- Review: `docs/reviews/milestone-reviews/2026-05-14-local-trial-fixture-command.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 hardening; improves product-owner trialability before custom essays, provider adapters, or formal vault mutation.
- Validation: 114 unit tests passed, `python3 -m compileall src tests` passed, `git diff --check` passed, and `PYTHONPATH=src python3 -m diamonddust local-trial-fixture --root . --vault-root /tmp/diamonddust-fixture-smoke --created-at 2026-05-14T00:00:00Z` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Run a controlled product-owner trial using the shortcut, then decide whether shortcut behavior should be package-data-backed or CI-gated.

## 2026-05-14 — CI Validation Completed

- Scope: Added repository CI for the current Python validation baseline.
- Outcome: GitHub Actions now runs on pull requests and pushes, validates editable install, runs the full unit suite, compiles `src` and `tests`, checks whitespace, and smoke tests `diamonddust local-trial-fixture` on Python 3.11 and 3.12.
- Review: `docs/reviews/milestone-reviews/2026-05-14-ci-validation.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 release-quality infrastructure; strengthens PR validation without changing product runtime behavior, schema, provider behavior, or formal vault writes.
- Validation: 119 unit tests passed, `python3 -m compileall src tests` passed, `git diff --check` passed, and `PYTHONPATH=src python3 -m diamonddust local-trial-fixture --root . --vault-root /tmp/diamonddust-ci-smoke --created-at 2026-05-14T00:00:00Z` passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Confirm the first remote GitHub Actions run after push and decide whether branch protection should require CI before merge.

## 2026-05-14 — Portable Local Trial Fixture Completed

- Scope: Made the `local-trial-fixture` shortcut load packaged fixture assets instead of repository-relative test fixture files.
- Outcome: The fixture essay and extraction JSON are packaged under `diamonddust.fixtures.local_trial`, `diamonddust local-trial-fixture` can run from a non-repository working directory, and tests enforce package/test fixture parity.
- Review: `docs/reviews/milestone-reviews/2026-05-14-portable-local-trial-fixture.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 local trial usability hardening; improves installed CLI trialability without provider calls, schema changes, formal writes, or publication behavior.
- Validation: 121 unit tests passed, `python3 -m compileall src tests` passed, `git diff --check` passed, and `PYTHONPATH=/home/yimg/code/DiamondDust/src python3 -m diamonddust local-trial-fixture --vault-root /tmp/diamonddust-portable-root-smoke --created-at 2026-05-14T00:00:00Z` passed from `/tmp`.
- Dependency impact: No production or development dependency was added; package data metadata was added for existing setuptools packaging.
- Follow-up: Run an installed CLI product-owner trial and select product-owner-approved golden essays.

## 2026-05-14 — Package Build Validation Completed

- Scope: Upgraded CI from editable install validation to wheel build/install validation.
- Outcome: GitHub Actions now builds a wheel, installs that wheel, runs `pip check`, then runs tests, compile checks, whitespace checks, and the non-repo-root local trial fixture smoke.
- Review: `docs/reviews/milestone-reviews/2026-05-14-package-build-validation.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 release-quality infrastructure; improves installed package confidence without changing runtime product behavior, schemas, provider behavior, formal writes, or publication.
- Validation: 121 unit tests passed, `python3 -m compileall src tests` passed, and `git diff --check` passed locally; remote CI must confirm wheel build/install because the current Codex shell lacks `pip`.
- Dependency impact: No production or development dependency was added; uses existing `pip`/setuptools behavior on GitHub-hosted runners.
- Follow-up: Confirm remote CI success, then later decide when versioning, release artifact upload, and publishing should become gates.

## 2026-05-14 — Local Trial Outcome JSON Completed

- Scope: Added a machine-readable local trial outcome artifact beside the Markdown feedback report.
- Outcome: Local trials now write `_ai_reports/local-trials/<trial_id>.json` for passed and safely failed runs, include it in CLI output, and preserve provider-free/no-formal-write boundaries.
- Review: `docs/reviews/milestone-reviews/2026-05-14-local-trial-outcome-json.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 local trial hardening; improves controlled product-owner trial summaries without adding provider calls, formal vault writes, external services, or public domain schema changes.
- Validation: 123 unit tests passed, `python3 -m compileall src tests` passed, `git diff --check` passed, and non-repo-root local trial fixture smoke passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Run a controlled product-owner trial and decide whether feedback fields should become typed user-input artifacts, release criteria, or golden fixture expectations.

## 2026-05-15 — Local Trial Report Verdict Status Completed

- Scope: Applied product-owner trial feedback to clarify local trial report status semantics and artifact reading order.
- Outcome: Local trial feedback reports now use `trial_pipeline_status`, include `product_owner_verdict: pending`, explain each artifact in the reading order, and keep feedback capture as structured free text without numeric scoring. Matching JSON outcome semantics are handled by the follow-up local trial outcome semantic consistency milestone.
- Review: `docs/reviews/milestone-reviews/2026-05-15-local-trial-report-verdict-status.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 local trial usability hardening; improves trial review clarity without implying full MVP readiness, real AI extraction quality, patch acceptance, formal writes, or publication approval.
- Validation: 123 unit tests passed, `python3 -m compileall src tests` passed, `git diff --check` passed, and non-repo-root local trial fixture smoke passed.
- Dependency impact: No production or development dependency was added; `.venv/` and `*.egg-info/` are now ignored to keep local trial install artifacts out of Git status.
- Follow-up: Keep feedback capture as structured free text until real product-owner feedback calibrates the rubric.

## 2026-05-15 — Local Trial Outcome Semantic Consistency Completed

- Scope: Aligned machine-readable local trial outcome JSON with Markdown feedback report semantics.
- Outcome: Local trial outcome JSON now uses `trial_pipeline_passed`, `trial_pipeline_status`, `product_owner_verdict`, and `pipeline_summary`, removes ambiguous top-level `passed`, `status`, and `summary`, and adds stage/scope plus `not_validated` and `quality_scope` limits.
- Review: `docs/reviews/milestone-reviews/2026-05-15-local-trial-outcome-semantic-consistency.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 local trial artifact hardening; improves machine-readable safety semantics without provider calls, formal vault writes, patch acceptance, publication, or full MVP completion claims.
- Validation: 123 unit tests passed, `python3 -m compileall src tests` passed, `git diff --check` passed, non-repo-root local trial fixture smoke passed, and the local `knowledge-vault/` trial artifacts were regenerated with matching Markdown/JSON semantics.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add compatibility handling only if older local trial outcome JSON import/replay becomes a supported workflow.

## 2026-05-15 — Local Trial Run Log Scope Completed

- Scope: Applied product-owner trial feedback to clarify provider-free fixture scope in AI run logs.
- Outcome: Local trial AI run logs now include `trial_id`, `stage_label`, `run_scope`, `real_provider_call`, `fixture_driven`, `prompt_used`, `metrics_scope`, `source_input_id`, `output_artifacts`, and run-specific `not_validated` fields while generic run logs remain provider-neutral.
- Review: `docs/reviews/milestone-reviews/2026-05-15-local-trial-run-log-scope.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 local trial artifact hardening; improves run log semantics without provider calls, formal vault writes, patch acceptance, publication, or full MVP completion claims.
- Validation: 125 unit tests passed, `python3 -m compileall src tests` passed, `git diff --check` passed, non-repo-root local trial fixture smoke passed, and the local `knowledge-vault/` trial artifacts were regenerated with run log scope fields.
- Dependency impact: No production or development dependency was added.
- Follow-up: Introduce a separate extraction output artifact only if replay/debug/product-owner feedback requires it.

## 2026-05-15 — AI Suggestions Artifact Semantics Completed

- Scope: Applied accepted `_ai_suggestions/` module audit feedback to candidate manifests and blog drafts.
- Outcome: Candidate manifests now include candidate preview boundary and raw KnowledgePatch source-of-truth sections, local trial manifests include fixture SourceRef scope, blog draft frontmatter marks review/provider-free fixture scope, and blog draft Claim Inventory includes supporting concepts with role labels.
- Review: `docs/reviews/milestone-reviews/2026-05-15-ai-suggestions-artifact-semantics.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 local trial artifact hardening; improves preview/review semantics without provider calls, formal vault writes, patch acceptance, publication, extraction artifacts, artifact groups, or path audit artifacts.
- Validation: 128 unit tests passed, `python3 -m compileall src tests` passed, `git diff --check` passed, non-repo-root local trial fixture smoke passed, and the local `knowledge-vault/` trial artifacts were regenerated with `_ai_suggestions/` semantic updates.
- Dependency impact: No production or development dependency was added.
- Follow-up: Revisit Claim Inventory naming only if supporting concept entries prove confusing in product-owner feedback.

## 2026-05-15 — Patch Review Report Semantics Completed

- Scope: Applied accepted `_ai_reports/patch-reviews/` module audit feedback to patch review reports.
- Outcome: Patch review reports now include YAML frontmatter with pending decision metadata, local trial review scope context, expanded risks, suggested review order, preview-level rollback note, and a non-binding Review Decision Prompt.
- Review: `docs/reviews/milestone-reviews/2026-05-15-patch-review-report-semantics.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 local trial artifact hardening; improves patch review semantics without provider calls, formal vault writes, real patch decision artifacts, accept/reject recording, publication, or scoring.
- Validation: 130 unit tests passed, `python3 -m compileall src tests` passed, `git diff --check` passed, non-repo-root local trial fixture smoke passed, and the local `knowledge-vault/` trial artifacts were regenerated with patch review report semantic updates.
- Dependency impact: No production or development dependency was added.
- Follow-up: Design a separate patch decision artifact before formal apply execution.

## 2026-05-16 — Blog Quality Report Semantics Completed

- Scope: Applied accepted `_ai_reports/blog-quality/` module audit feedback to blog quality reports.
- Outcome: Blog quality reports now include YAML frontmatter, `quality_status` summary wording, `requires_user_review: true`, and provider-free fixture context for local trials. Fixture-driven reports now state real AI generation, unsupported-claim detection, source-span accuracy, and publication approval limits.
- Review: `docs/reviews/milestone-reviews/2026-05-16-blog-quality-report-semantics.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 local trial artifact hardening; improves blog quality report semantics without provider calls, formal vault writes, publication decision artifacts, user acceptance, or scoring.
- Validation: 131 unit tests passed, `python3 -m compileall src tests` passed, `git diff --check` passed, and local trial fixture smoke passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Calibrate publication/editorial quality criteria only after real product-owner trial feedback.

## 2026-05-16 — Trial Feedback Cleanup Audit Completed

- Scope: Audited trial feedback implementation changes from `1bc6712` through current `origin/main`.
- Outcome: Removed ambiguous simulated patch-acceptance terminology from the local trial runtime flow, aligned blog quality report artifact object naming with persisted `quality_status`, centralized local trial semantic constants where they cross artifact families, and made empty candidate manifest risks explicit.
- Review: `docs/reviews/milestone-reviews/2026-05-16-trial-feedback-cleanup-audit.md`.
- Review decision: pass.
- Gate impact: Post-Gate 7 cleanup; improves readiness for real provider planning without changing persisted artifact boundaries or enabling provider calls, formal writes, patch decisions, publication, or scoring.
- Validation: 132 unit tests passed, `python3 -m compileall src tests` passed, `git diff --check` passed, and local trial fixture smoke passed.
- Dependency impact: No production or development dependency was added.
- Follow-up: Keep real provider execution context separate from provider-free fixture context during provider integration planning.

## 2026-05-16 — Provider Adapter Boundary Skeleton Completed

- Scope: Implemented provider-neutral request, response, error, model settings, usage, fake provider, and application handoff from provider envelopes into existing extraction validation.
- Outcome: Added a fake-provider-only skeleton for `extract_units` without real provider SDKs, API key reads, network calls, raw provider output persistence, formal apply, patch acceptance, publication, or provider-side tool execution.
- Review: `docs/reviews/milestone-reviews/2026-05-16-provider-adapter-boundary-skeleton.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 provider-readiness milestone; affects the Gate 4 AI extraction boundary but does not approve real provider integration.
- Validation: 139 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Escalate before choosing a real provider, adding SDK dependencies, reading API keys, making real network calls, setting cost limits, enabling fallback, or persisting real raw provider output.

## 2026-05-16 — Provider Run Log Metadata Completed

- Scope: Connected provider response/error envelope metadata to optional AI run-log artifact context.
- Outcome: AI run logs can now persist provider request id, retry count, and token usage through a typed storage context mapped by the application layer, while provider adapters remain side-effect free.
- Review: `docs/reviews/milestone-reviews/2026-05-16-provider-run-log-metadata.md`.
- Review decision: pass.
- Gate impact: Post-Gate 7 provider-readiness milestone; improves future real-provider traceability without approving real provider integration.
- Validation: 140 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Clarify latency units, cost limits, retry policy, fallback behavior, and raw output retention before real provider integration.

## 2026-05-16 — Model Policy Skeleton Completed

- Scope: Implemented the provider-neutral v0 model policy skeleton and request policy validation.
- Outcome: The application provider extraction handoff now validates model policy before provider execution. Defaults keep first provider undecided, only `extract_units` allowed, structured output required, real provider calls unapproved, fallback disabled, raw output persistence/logging disabled, and API key logging forbidden.
- Review: `docs/reviews/milestone-reviews/2026-05-16-model-policy-skeleton.md`.
- Review decision: pass.
- Gate impact: Post-Gate 7 provider-readiness milestone; prepares real provider planning without approving real provider integration.
- Validation: 150 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Escalate before choosing a real provider, adding SDK dependencies, reading API keys, making real network calls, setting cost limits, enabling fallback, or persisting real raw provider output.

## 2026-05-16 — Provider Request Builder Completed

- Scope: Implemented the provider-neutral `extract_units` request builder from ingested Markdown essays.
- Outcome: Application code can now build traceable provider requests containing source identity, source path, content hashes, body line range, frontmatter, body text, and source reference metadata while validating model policy before returning the request.
- Review: `docs/reviews/milestone-reviews/2026-05-16-provider-request-builder.md`.
- Review decision: pass.
- Gate impact: Post-Gate 7 provider-readiness milestone; prepares real provider request construction without approving real provider integration.
- Validation: 154 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Escalate before rendering provider prompts, choosing a real provider, adding SDK dependencies, reading API keys, making real network calls, setting cost limits, enabling fallback, or sending essay body text to an external provider.

## 2026-05-16 — Extraction Prompt Renderer Completed

- Scope: Implemented the provider-neutral `extract_units.v1` prompt renderer.
- Outcome: AI boundary code can now render deterministic prompt packages from provider requests, including source metadata, system prompt, user prompt, output instructions, and a stable prompt hash while validating model policy before rendering.
- Review: `docs/reviews/milestone-reviews/2026-05-16-extraction-prompt-renderer.md`.
- Review decision: pass.
- Gate impact: Post-Gate 7 provider-readiness milestone; prepares provider prompt construction without approving real provider integration.
- Validation: 159 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Escalate before choosing a real provider, adding SDK dependencies, reading API keys, making real network calls, setting cost limits, enabling fallback, persisting raw provider output, or sending rendered prompt text to an external provider.

## 2026-05-16 — Provider Extraction Orchestrator Completed

- Scope: Implemented the application-level provider extraction orchestration skeleton for `extract_units`.
- Outcome: Application code can now build provider-neutral requests, render prompt packages, execute a supplied provider boundary, validate structured output, and return run-log context with provider metadata plus prompt hash without persisting prompt text.
- Review: `docs/reviews/milestone-reviews/2026-05-16-provider-extraction-orchestrator.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 provider-readiness milestone; composes the provider skeleton without approving real provider integration.
- Validation: 164 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Escalate before choosing a real provider, adding SDK dependencies, reading API keys, making real network calls, setting cost limits, enabling fallback, persisting raw provider output, or sending rendered prompt text to an external provider.

## 2026-05-17 — Provider Execution Request Completed

- Scope: Implemented the prompt-aware provider execution request boundary for `extract_units`.
- Outcome: Concrete provider adapters now have a typed input shape that combines `ProviderRequest` and `RenderedPrompt`, validates metadata alignment, and supports provider-free fake execution tests without persisting prompt text.
- Review: `docs/reviews/milestone-reviews/2026-05-17-provider-execution-request.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 provider-readiness milestone; clarifies concrete provider adapter input without approving real provider integration.
- Validation: 168 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Escalate before choosing a real provider, adding SDK dependencies, reading API keys, making real network calls, setting cost limits, enabling fallback, persisting prompt/raw provider output, or sending rendered prompt text to an external provider.

## 2026-05-17 — Provider Integration Readiness Gate Completed

- Scope: Implemented an application-level readiness gate for first real-provider integration decisions.
- Outcome: The project can now report `blocked` until required provider, model, SDK, API key env var, network, prompt externalization, structured-output mechanism, cost, timeout, retry, raw-output retention, fallback, and task-scope decisions are explicit.
- Review: `docs/reviews/milestone-reviews/2026-05-17-provider-integration-readiness.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 provider-readiness milestone; improves real-provider integration safety without approving real provider integration.
- Validation: 173 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Use the readiness report as input to first-provider escalation; escalate before choosing a real provider, adding SDK dependencies, reading API keys, making real network calls, setting cost limits, enabling fallback, persisting prompt/raw provider output, or sending rendered prompt text to an external provider.

## 2026-05-17 — Provider Readiness Report Rendering Completed

- Scope: Added deterministic Markdown rendering for provider integration readiness reports.
- Outcome: Readiness status, blockers, provider decisions, approval checklist, safety boundaries, and next steps can now be reviewed without reading API key values, calling providers, or persisting prompt/raw provider output.
- Review: `docs/reviews/milestone-reviews/2026-05-17-provider-readiness-report.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 provider-readiness milestone; improves first-provider escalation reviewability without approving real provider integration.
- Validation: 176 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Use rendered readiness reports as planning/escalation input only; separately approve provider, model, SDK dependency, API key env var, network calls, cost, retry, fallback, raw-output retention, and prompt externalization before real-provider integration.

## 2026-05-17 — Provider Readiness CLI Command Completed

- Scope: Added `diamonddust provider-readiness-report` as a diagnostic CLI command for first-provider readiness review.
- Outcome: The CLI can render blocked or ready readiness reports from explicit command-line decision values, returns success for valid blocked diagnostics, keeps the first-provider task scope fixed to `extract_units`, and does not read API key values, call providers, or persist artifacts.
- Review: `docs/reviews/milestone-reviews/2026-05-17-provider-readiness-command.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 provider-readiness milestone; improves first-provider escalation usability without approving real provider integration.
- Validation: 178 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, provider readiness CLI smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Treat CLI output as review input only; record provider approvals separately before SDK, API key, network, cost, retry, fallback, raw-output retention, or prompt externalization behavior is implemented.

## 2026-05-17 — Provider Integration Escalation Request Draft Completed

- Scope: Added deterministic first-provider escalation request drafting from provider readiness reports and exposed it through `diamonddust provider-escalation-request`.
- Outcome: The application and CLI can now present blocked/ready readiness state, requested decisions, risks, affected rules, fallback, and exact user decision needs in the project escalation request shape without recording approval, reading API key values, calling providers, or persisting artifacts.
- Review: `docs/reviews/milestone-reviews/2026-05-17-provider-escalation-request.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 provider-readiness milestone; improves first-provider approval workflow without approving real provider integration.
- Validation: 182 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, provider escalation CLI smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Use the draft as review input only; separately approve provider, model, SDK dependency, API key env var, network calls, cost, retry, fallback, raw-output retention, and prompt externalization before implementation.

## 2026-05-17 — Provider Decisions JSON Input Completed

- Scope: Added strict JSON input parsing for provider integration decisions and wired `--decisions-json` into provider readiness and escalation CLI diagnostics.
- Outcome: Decision JSON maps are validated into typed `ProviderIntegrationDecisionSet` values, reject unknown fields, accept JSON arrays for `allowed_tasks`, and remain diagnostic input rather than approval records. CLI commands do not merge JSON with inline flags, read API key values, call providers, or persist artifacts.
- Review: `docs/reviews/milestone-reviews/2026-05-17-provider-decisions-json.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 provider-readiness milestone; improves first-provider approval package usability without approving real provider integration.
- Validation: 188 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, provider decisions JSON CLI smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Treat decision JSON as diagnostic input only; design a separate durable approval artifact if real provider approval records are later needed.

## 2026-05-17 — Provider Decisions JSON Template Completed

- Scope: Added a blocked-by-default provider decisions JSON template and exposed it through `diamonddust provider-decisions-template`.
- Outcome: The template contains every provider decision field, keeps all approvals false, keeps provider/model/SDK/API key env var unset, limits `allowed_tasks` to `extract_units`, parses back into typed decisions, and remains diagnostic input rather than an approval record.
- Review: `docs/reviews/milestone-reviews/2026-05-17-provider-decisions-template.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 provider-readiness milestone; improves first-provider decision drafting without approving real provider integration.
- Validation: 190 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, provider decisions template CLI smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Treat generated templates as editable diagnostic input only; design a separate durable approval artifact if approval records are later needed.

## 2026-05-18 — Provider Decision Package Completed

- Scope: Added deterministic provider decision package rendering and exposed it through `diamonddust provider-decision-package`.
- Outcome: The CLI can compose the readiness report and first-provider escalation request draft from the same inline or JSON decision input, while explicitly stating that the package records no approval, calls no provider, reads no API key values, adds no SDK dependency, persists no prompt/raw provider output, and authorizes no implementation.
- Review: `docs/reviews/milestone-reviews/2026-05-18-provider-decision-package.md`.
- Review decision: pass.
- Gate impact: Post-Gate 7 provider-readiness milestone; improves first-provider review packaging without approving real provider integration.
- Validation: 195 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, provider decision package CLI smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Treat decision packages as local review input only; create a separate durable approval artifact only after the product owner approves that workflow.

## 2026-05-18 — Extraction Output JSON Schema Completed

- Scope: Added generated machine-readable JSON Schema rendering for `extract_units` output and exposed it through `diamonddust extraction-output-schema`.
- Outcome: The schema is generated from current domain enum values, documents the structured output shape for future provider planning, and explicitly remains a contract aid rather than the authoritative runtime validator.
- Review: `docs/reviews/milestone-reviews/2026-05-18-extraction-output-schema.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 provider-readiness milestone; improves future provider structured-output planning without approving real provider integration.
- Validation: 201 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, extraction schema CLI smoke passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Decide later whether runtime JSON Schema validation, provider-specific schema transforms, or authoring helpers are needed after real provider integration begins.

## 2026-05-18 — Prompt Output Schema Package Completed

- Scope: Extended rendered `extract_units` prompt packages with output schema id, version, hash, and generated schema content.
- Outcome: Future provider adapters can receive the machine-readable structured-output contract through `RenderedPrompt`, and prompt identity now includes the output schema hash. Execution requests reject mismatched rendered prompt output schema versions.
- Review: `docs/reviews/milestone-reviews/2026-05-18-prompt-output-schema-package.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 provider-readiness milestone; strengthens the prompt-aware provider boundary without approving real provider integration.
- Validation: 202 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, focused prompt/execution tests passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add provider-specific schema mapping only after provider, model, SDK, structured-output mechanism, prompt externalization, and real network call decisions are approved.

## 2026-05-18 — Provider Execution Payload Completed

- Scope: Added provider-neutral execution payload types and a builder from `ProviderExecutionRequest`.
- Outcome: Future concrete provider adapters can start from a serializable internal payload containing provider/model settings, system/user messages, output instructions, output schema metadata/content, and safety boundary flags without receiving a provider-specific SDK payload.
- Review: `docs/reviews/milestone-reviews/2026-05-18-provider-execution-payload.md`.
- Review decision: pass with follow-up.
- Gate impact: Post-Gate 7 provider-readiness milestone; clarifies future adapter input without approving real provider integration.
- Validation: 206 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, focused provider execution payload tests passed, and domain architecture scan reported 0 violations.
- Dependency impact: No production or development dependency was added.
- Follow-up: Add provider-specific SDK request mapping only after first-provider, SDK, API key, network, prompt externalization, structured-output mechanism, cost, retry, and retention decisions are approved.
