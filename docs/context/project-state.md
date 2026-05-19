# Project State

Last updated: 2026-05-18

## Current Stage

Provider output source binding is complete.

## Current Focus

Prepare the escalation and execution plan for the first real provider integration from a provider-neutral skeleton baseline. The current skeleton keeps real provider calls disabled, avoids SDK dependencies, avoids API key reads, and limits future first-provider scope to `extract_units`. Provider adapters return typed response/error envelopes; concrete provider adapters now have a typed provider execution request carrying both the provider-neutral request and rendered prompt package; provider-neutral execution payloads can be built from execution requests for future adapter mapping and previewed through `diamonddust provider-payload-preview` for local review without provider calls or persistence; rendered prompt packages carry output schema id, version, hash, and schema content for future structured-output provider adapters; application pipelines can build provider-neutral requests from ingested Markdown, render provider-neutral prompt packages, orchestrate prompt-aware provider-boundary execution, validate provider requests against model policy before execution, require provider structured output `source_input_id` to match the request payload `source_input_id`, validate structured output, map provider request id, retry count, token usage, and prompt hash into typed run-log context, parse provider decision JSON into typed readiness decisions, provide a blocked-by-default provider decision JSON template, assess whether required real-provider integration decisions are complete before implementation, render readiness reports, escalation request drafts, and combined provider decision packages for review without reading API keys or calling providers, print a machine-readable `extract_units` output schema generated from domain enums, and expose those diagnostics through CLI commands; storage adapters persist `_ai_runs`, `_ai_suggestions`, and `_ai_reports`; and formal vault mutation remains out of scope.

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

The current repository now contains the initial product implementation skeleton: typed domain schemas, a Markdown storage ingestion adapter, a provider-neutral AI extraction proposal boundary, generated `extract_units` output JSON Schema rendering, provider-neutral request/response/error/model-settings envelopes with fake provider skeletons for `extract_units`, a prompt-aware provider execution request boundary, provider-neutral execution payloads for future adapter mapping and a local payload preview CLI, a provider integration readiness gate with strict JSON decision parsing, a blocked-by-default decision JSON template, deterministic Markdown report rendering, escalation request draft rendering, combined provider decision package rendering, and diagnostic CLI commands, a conservative v0 model policy skeleton, an application-level provider request builder for ingested Markdown essays, a provider-neutral extraction prompt renderer that carries output schema metadata/content in the rendered prompt package, an application-level provider extraction orchestrator that composes request building, prompt rendering, prompt-aware provider envelopes, source binding, typed validation, and run-log context, provider envelope metadata handoff into typed AI run-log context, AI run log persistence with provider-free local trial scope context, an application-layer patch review workflow, candidate Markdown export with explicit preview/source-of-truth boundaries, patch review reports with pending decision metadata and non-binding decision prompts, review package storage adapters, a deterministic blog draft workflow with review/scope frontmatter and supporting concept inventory, durable blog draft package persistence, blog quality reports with precise report validation/publication boundary semantics, artifact schema versioning, a local trial CLI with packaged `local-trial-fixture` assets, feedback reports and machine-readable outcome JSON artifacts that separate `trial_pipeline_status` from `product_owner_verdict`, explicit local trial quality-scope limits, feedback capture fields, and a cleaned local trial draft-generation handoff that does not expose patch-acceptance terminology. It also includes minimal Python packaging metadata with a `diamonddust` console script, formal vault conflict preflight checks, formal apply dry-run plans, a checked-in local trial fixture pair, user-facing local trial guides, a Gate 7 release readiness harness, five sample essay fixtures, unit tests, and GitHub Actions CI for wheel build/install, tests, compile checks, whitespace checks, and local trial fixture smoke. Real provider calls and formal vault patch apply execution are not present yet. Generated `knowledge-vault/` trial output is ignored. `目录结构.md` describes the intended target structure, not the fully materialized repository.

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
- Next likely stage: first real provider integration planning and escalation from the prompt-aware provider boundary skeleton.

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

Blog quality report semantics review:

- `docs/reviews/milestone-reviews/2026-05-16-blog-quality-report-semantics.md`
- decision: pass with follow-up
- tests: 131 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed

Trial feedback cleanup audit review:

- `docs/reviews/milestone-reviews/2026-05-16-trial-feedback-cleanup-audit.md`
- decision: pass
- tests: 132 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed

Provider adapter boundary skeleton review:

- `docs/reviews/milestone-reviews/2026-05-16-provider-adapter-boundary-skeleton.md`
- decision: pass with follow-up
- tests: 139 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, architecture scan reported 0 violations

Provider run log metadata review:

- `docs/reviews/milestone-reviews/2026-05-16-provider-run-log-metadata.md`
- decision: pass
- tests: 140 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, architecture scan reported 0 violations

Model policy skeleton review:

- `docs/reviews/milestone-reviews/2026-05-16-model-policy-skeleton.md`
- decision: pass
- tests: 150 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, architecture scan reported 0 violations

Provider request builder review:

- `docs/reviews/milestone-reviews/2026-05-16-provider-request-builder.md`
- decision: pass
- tests: 154 unit tests passed, compile check passed, diff check passed, local trial fixture smoke passed, architecture scan reported 0 violations

## Immediate Next Development Path

Gate 7 readiness and the current one-command local trial fixture path are complete for the current skeleton. Trial runs now produce a human-first Markdown report and machine-readable JSON outcome under `_ai_reports/local-trials/`, AI run logs that explicitly mark provider-free fixture scope under `_ai_runs/`, `_ai_suggestions/` preview artifacts with clearer preview/review/source-of-truth boundaries, and patch review reports with pending decision metadata that do not record formal acceptance. The provider boundary now has a fake-provider-only envelope skeleton, conservative model policy validation, application-level provider request construction, and run-log metadata handoff for future real-provider traceability.

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
