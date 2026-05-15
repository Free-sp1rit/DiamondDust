# Project State

Last updated: 2026-05-15

## Current Stage

Post-Gate 7 patch review report semantic hardening complete with follow-up.

## Current Focus

Continue controlled local trials from aligned Markdown, JSON outcome, AI run log, candidate preview, patch review report, and blog draft artifacts that separate pipeline status from product-owner verdict and avoid implying real provider calls, real LLM quality, formal apply, user acceptance, publication quality, or full MVP completion.

Initialization acceptance is complete with a `pass with follow-up` decision. The governance initialization PR has been completed and merged by the product owner. Gate 2 through Gate 6 planning and implementation are complete.

## Repo-Local Skills

Minimal governance skills have been initialized under `skills/`:

- `skills/spec-to-plan/SKILL.md`
- `skills/constraint-escalation/SKILL.md`
- `skills/milestone-review/SKILL.md`
- `skills/pr-review/SKILL.md`
- `skills/git-workflow/SKILL.md`

Each skill is intentionally lightweight and contains only workflow guidance in `SKILL.md`. Project facts remain in `docs/`.

## Initialized Context Summary

DiamondDust is a local-first semantic knowledge compiler. Its MVP path is to turn Markdown essays into structured `KnowledgeUnit` candidates, candidate `Relation`s, validated `KnowledgePatch` files, review reports, blog drafts, and blog quality reports.

The current repository now contains the initial product implementation skeleton: typed domain schemas, a Markdown storage ingestion adapter, a provider-neutral AI extraction proposal boundary, AI run log persistence with provider-free local trial scope context, an application-layer patch review workflow, candidate Markdown export with explicit preview/source-of-truth boundaries, patch review reports with pending decision metadata and non-binding decision prompts, review package storage adapters, a deterministic blog draft workflow with review/scope frontmatter and supporting concept inventory, durable blog draft package persistence, artifact schema versioning, a local trial CLI with packaged `local-trial-fixture` assets, feedback reports and machine-readable outcome JSON artifacts that separate `trial_pipeline_status` from `product_owner_verdict`, explicit local trial quality-scope limits, and feedback capture fields, minimal Python packaging metadata with a `diamonddust` console script, formal vault conflict preflight checks, formal apply dry-run plans, a checked-in local trial fixture pair, user-facing local trial guides, a Gate 7 release readiness harness, five sample essay fixtures, unit tests, and GitHub Actions CI for wheel build/install, tests, compile checks, whitespace checks, and local trial fixture smoke. Real provider calls and formal vault patch apply execution are not present yet. Generated `knowledge-vault/` trial output is ignored. `目录结构.md` describes the intended target structure, not the fully materialized repository.

## Source-of-Truth Documents

- `AGENTS.md` is the navigation and operating-control plane for coding agents.
- `docs/00_PROJECT_CHARTER.md` through `docs/14_CONSTRAINT_ESCALATION_POLICY.md` hold DiamondDust product, architecture, schema, AI boundary, quality, dependency, Git, planning, and escalation truth.
- `docs/context/` holds durable development memory.
- `docs/exec-plans/` holds active, completed, and blocked task plans.
- `docs/reviews/milestone-reviews/` is reserved for milestone review records.

## Current Invariants

- Markdown files are the source of truth.
- SQLite, vector indexes, compile caches, and model run caches are rebuildable.
- Runtime AI may generate candidates, relations, patches, drafts, and reports, but must not directly overwrite formal knowledge files.
- Formal knowledge writes require a validated `KnowledgePatch` and explicit user acceptance.
- Domain core must not depend on provider SDKs, UI frameworks, storage engines, note-taking platforms, or MCP SDKs.
- All AI outputs must pass typed schema validation before becoming internal data.
- Unsupported claims must be explicitly marked, and source references must be preserved where possible.
- Public schema changes require schema versioning, migration notes, and tests.

## Review Gate Position

Current gate position:

- Gate 0: Direction Freeze is satisfied by merged startup governance docs.
- Gate 1: Architecture Freeze is satisfied by merged architecture, domain, data, and AI pipeline contracts.
- Gate 2: Schema Skeleton passed on 2026-05-10.
- Gate 3: Markdown Ingestion passed with follow-up on 2026-05-10.
- Gate 4: AI Extraction Proposal passed with follow-up on 2026-05-10.
- Gate 5: Patch Review passed with follow-up on 2026-05-10.
- Gate 6: Blog Draft passed with follow-up on 2026-05-10.
- Gate 7: MVP Release readiness passed with follow-up on 2026-05-10.
- Next likely stage: post-MVP hardening and release-quality infrastructure.

Initialization acceptance review:

- `docs/reviews/milestone-reviews/2026-05-10-initialization-acceptance.md`
- score: 18/20
- decision: pass with follow-up
- Gate 2 planning readiness: yes
- Gate 2 implementation readiness: not yet recommended

Gate 2 review:

- `docs/reviews/milestone-reviews/2026-05-10-gate-2-schema-skeleton.md`
- decision: pass
- tests: 12 unit tests passed, compile check passed, diff check passed

Gate 3 review:

- `docs/reviews/milestone-reviews/2026-05-10-gate-3-markdown-ingestion.md`
- decision: pass with follow-up
- tests: 19 unit tests passed, compile check passed, diff check passed

Gate 4 review:

- `docs/reviews/milestone-reviews/2026-05-10-gate-4-ai-extraction-proposal.md`
- decision: pass with follow-up
- tests: 27 unit tests passed, compile check passed, diff check passed

Gate 5 review:

- `docs/reviews/milestone-reviews/2026-05-10-gate-5-patch-review.md`
- decision: pass with follow-up
- tests: 38 unit tests passed, compile check passed, diff check passed

Gate 6 review:

- `docs/reviews/milestone-reviews/2026-05-10-gate-6-blog-draft.md`
- decision: pass with follow-up
- tests: 46 unit tests passed, compile check passed, diff check passed

Gate 7 review:

- `docs/reviews/milestone-reviews/2026-05-10-gate-7-mvp-release-readiness.md`
- decision: pass with follow-up
- tests: 53 unit tests passed, compile check passed, diff check passed

Candidate Markdown export review:

- `docs/reviews/milestone-reviews/2026-05-11-candidate-markdown-export.md`
- decision: pass with follow-up
- tests: 59 unit tests passed, compile check passed, diff check passed

Review report rendering review:

- `docs/reviews/milestone-reviews/2026-05-11-review-report-rendering.md`
- decision: pass with follow-up
- tests: 65 unit tests passed, compile check passed, diff check passed

Review package persistence review:

- `docs/reviews/milestone-reviews/2026-05-11-review-package-persistence.md`
- decision: pass with follow-up
- tests: 70 unit tests passed, compile check passed, diff check passed

AI run log persistence review:

- `docs/reviews/milestone-reviews/2026-05-11-ai-run-log-persistence.md`
- decision: pass with follow-up
- tests: 76 unit tests passed, compile check passed, diff check passed

Blog draft package persistence review:

- `docs/reviews/milestone-reviews/2026-05-11-blog-draft-persistence.md`
- decision: pass with follow-up
- tests: 81 unit tests passed, compile check passed, diff check passed

Local trial harness review:

- `docs/reviews/milestone-reviews/2026-05-11-local-trial-harness.md`
- decision: pass with follow-up
- tests: 85 unit tests passed, compile check passed, diff check passed

Artifact schema versioning review:

- `docs/reviews/milestone-reviews/2026-05-11-artifact-schema-versioning.md`
- decision: pass with follow-up
- tests: 89 unit tests passed, compile check passed, diff check passed

Local trial fixtures review:

- `docs/reviews/milestone-reviews/2026-05-11-local-trial-fixtures.md`
- decision: pass with follow-up
- tests: 91 unit tests passed, compile check passed, diff check passed

Local trial extraction JSON notes review:

- `docs/reviews/milestone-reviews/2026-05-12-local-trial-extraction-json-notes.md`
- decision: pass with follow-up
- tests: 93 unit tests passed, compile check passed, diff check passed

Formal vault conflict checks review:

- `docs/reviews/milestone-reviews/2026-05-12-vault-conflict-checks.md`
- decision: pass with follow-up
- tests: 99 unit tests passed, compile check passed, diff check passed

Formal apply dry-run plan review:

- `docs/reviews/milestone-reviews/2026-05-12-formal-apply-plan.md`
- decision: pass with follow-up
- tests: 105 unit tests passed, compile check passed, diff check passed

Local trial feedback report review:

- `docs/reviews/milestone-reviews/2026-05-14-local-trial-feedback-report.md`
- decision: pass with follow-up
- tests: 108 unit tests passed, compile check passed, diff check passed

Local trial feedback capture review:

- `docs/reviews/milestone-reviews/2026-05-14-local-trial-feedback-capture.md`
- decision: pass with follow-up
- tests: 111 unit tests passed, compile check passed, diff check passed

CLI trial entrypoint review:

- `docs/reviews/milestone-reviews/2026-05-14-cli-trial-entrypoint.md`
- decision: pass with follow-up
- tests: 113 unit tests passed, compile check passed, diff check passed

Local trial fixture command review:

- `docs/reviews/milestone-reviews/2026-05-14-local-trial-fixture-command.md`
- decision: pass with follow-up
- tests: 114 unit tests passed, compile check passed, diff check passed

CI validation review:

- `docs/reviews/milestone-reviews/2026-05-14-ci-validation.md`
- decision: pass with follow-up
- tests: 119 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed

Portable local trial fixture review:

- `docs/reviews/milestone-reviews/2026-05-14-portable-local-trial-fixture.md`
- decision: pass with follow-up
- tests: 121 unit tests passed, compile check passed, diff check passed, non-repo-root fixture smoke passed

Package build validation review:

- `docs/reviews/milestone-reviews/2026-05-14-package-build-validation.md`
- decision: pass with follow-up
- tests: 121 unit tests passed, compile check passed, diff check passed; remote CI must confirm wheel build/install

Local trial outcome JSON review:

- `docs/reviews/milestone-reviews/2026-05-14-local-trial-outcome-json.md`
- decision: pass with follow-up
- tests: 123 unit tests passed, compile check passed, diff check passed, non-repo-root fixture smoke passed

Local trial run log scope review:

- `docs/reviews/milestone-reviews/2026-05-15-local-trial-run-log-scope.md`
- decision: pass with follow-up
- tests: 125 unit tests passed, compile check passed, diff check passed, non-repo-root fixture smoke passed

AI suggestions artifact semantics review:

- `docs/reviews/milestone-reviews/2026-05-15-ai-suggestions-artifact-semantics.md`
- decision: pass with follow-up
- tests: 128 unit tests passed, compile check passed, diff check passed, non-repo-root fixture smoke passed

Patch review report semantics review:

- `docs/reviews/milestone-reviews/2026-05-15-patch-review-report-semantics.md`
- decision: pass with follow-up
- tests: 130 unit tests passed, compile check passed, diff check passed, non-repo-root fixture smoke passed

## Immediate Next Development Path

Gate 7 readiness and the current one-command local trial fixture path are complete for the current skeleton. Trial runs now produce a human-first Markdown report and machine-readable JSON outcome under `_ai_reports/local-trials/`, AI run logs that explicitly mark provider-free fixture scope under `_ai_runs/`, `_ai_suggestions/` preview artifacts with clearer preview/review/source-of-truth boundaries, and patch review reports with pending decision metadata that do not record formal acceptance.

Expected next product implementation focus:

- run a controlled product-owner trial using installed `diamonddust local-trial-fixture` and `_ai_reports/local-trials/<trial_id>.md` as the first review artifact
- replace or supplement deterministic fixtures with product-owner-approved golden essays
- add formal vault apply/revert execution only after rollback/write-failure tests and explicit user acceptance handoff exist
- decide whether GitHub branch protection should require the CI check before merge
- keep provider calls, formal writes, and publishing behind their existing approval and review gates

## Git State Notes

Governance initialization branch: `chore/context-initialization`.

The governance initialization branch was pushed, reviewed through PR, and merged by the product owner.

Future development workflow permissions:

- The coding agent may run GitHub PR preflight in ordinary workspace-write mode.
- The coding agent may push the current task branch.
- The coding agent may run `gh pr create`.
- The coding agent must not run `gh pr merge`.
- The coding agent must not push `main`.
- The coding agent must not force push.

Allowed PR preflight commands include:

- `gh auth status --hostname github.com`
- `gh repo view --json nameWithOwner,url`
- `curl -I https://api.github.com`
- `git status`
- `git branch --show-current`

Proxy and auth note:

- Network access may require the host proxy on port 7890.
- Do not assume `127.0.0.1:7890` is always the host proxy; run proxy preflight first.
- On 2026-05-10, full-permission proxy preflight found `127.0.0.1:7890` reachable, `gh auth status` successful, `gh repo view` successful, branch push successful, and PR creation successful.
- If future preflight fails, stop and output an escalation request instead of trying to bypass the failure.
