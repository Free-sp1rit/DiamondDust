# Decisions

Record durable technical and governance decisions here.

## Current Governance Baseline Decisions

### 2026-05-10 — Separate runtime AI autonomy from development-agent autonomy

- Decision: Runtime AI inside DiamondDust may only generate candidates, relations, patches, drafts, and reports; the coding agent may autonomously plan, edit code/docs, test, review, and propose changes within the active task scope.
- Reason: The product safety boundary must prevent direct AI mutation of formal knowledge, while development work still needs agent autonomy to move efficiently.
- Alternatives: Treat all AI autonomy as forbidden until patch review is stable; allow runtime AI to mutate formal notes directly.
- Risks: The distinction must remain explicit so future product features do not inherit development-agent freedoms.
- Follow-up: Keep runtime AI write behavior behind validated patch review and user acceptance.

### 2026-05-10 — Use project docs as DiamondDust source of truth

- Decision: DiamondDust-specific product facts, architecture boundaries, schemas, review gates, and governance decisions live in `docs/`; `AGENTS.md` remains the navigation and operating-control plane.
- Reason: This keeps durable project context in the repository and avoids relying on chat history.
- Alternatives: Put all governance in `AGENTS.md`; encode project facts in reusable skills; rely on external issue history.
- Risks: Docs can drift from implementation if not updated during behavior, schema, or architecture changes.
- Follow-up: Update docs and repo memory whenever public behavior, schema, architecture, workflow, or policy changes.

### 2026-05-10 — Use skills for reusable workflows only

- Decision: Skills may define repeatable workflows such as planning, milestone review, debugging, PR review, and escalation, but must not duplicate or override DiamondDust product truth.
- Reason: Skills should improve agent process without becoming a competing authority for project-specific facts.
- Alternatives: Store project governance in skills; avoid skills entirely.
- Risks: A stale skill could conflict with project docs.
- Follow-up: Prefer project docs in conflicts and create an escalation request if following a skill would reduce delivery quality.

### 2026-05-10 — Require execution plans and repo memory for non-trivial tasks

- Decision: Non-trivial work requires an execution plan under `docs/exec-plans/active/`, durable context updates under `docs/context/`, and completed-plan compression under `docs/exec-plans/completed/`.
- Reason: The project needs continuity across context compression, review cycles, and future agent sessions.
- Alternatives: Use chat-only plans; use ad hoc notes outside the repo.
- Risks: Planning overhead can grow if plans include raw logs or speculative detail.
- Follow-up: Keep plans concise, revise them when evidence changes, and avoid persisting temporary debugging noise.

### 2026-05-10 — Keep implementation behind review gates

- Decision: Product implementation code should wait until startup governance and architecture docs are approved and the relevant review gates are satisfied.
- Reason: The MVP depends on safety-critical boundaries around schema validation, patch review, formal writes, and provider neutrality.
- Alternatives: Begin product code before Gate 0/Gate 1 approval; mark gates passed without review.
- Risks: Delaying implementation can slow visible progress.
- Follow-up: Ask the product owner to review startup docs and decide whether Gate 0 and Gate 1 can be marked passed.

### 2026-05-10 — Initialize minimal governance skills under `skills/`

- Decision: Create lightweight repo-local governance skills for planning, escalation, milestone review, PR review, and Git workflow under `skills/<skill-name>/SKILL.md`.
- Reason: The product owner approved initializing minimal governance skills, and the workspace `.codex/` and `.agents/` directories are read-only.
- Alternatives: Use hidden `.codex/skills/` or `.agents/skills/` directories; create scripts/assets/references; keep the workflows only in docs.
- Risks: `skills/` may require later wiring if the active Codex environment discovers only a different skill path.
- Follow-up: Confirm or document the skill discovery path when repo-local skill loading becomes necessary.

### 2026-05-10 — GitHub task-branch push and PR creation permission

- Decision: For future development, the coding agent may run GitHub PR workflow preflight, push the current task branch, and use `gh pr create`; the coding agent must not use `gh pr merge`, must not push `main`, and must not force push.
- Reason: The product owner explicitly approved task-branch push and PR creation while keeping merge and protected-branch authority with the product owner.
- Alternatives: Require approval for every push and PR creation; allow full PR merge automation.
- Risks: Local proxy or `gh` authentication can still fail even when the permission boundary is approved.
- Follow-up: Before PR creation, run preflight with `gh auth status --hostname github.com`, `gh repo view --json nameWithOwner,url`, `curl -I https://api.github.com`, `git status`, and `git branch --show-current`; if preflight fails, stop and output an escalation request.

### 2026-05-10 — Implement Gate 2 schema skeleton with Python standard library

- Decision: Implement the initial domain schema skeleton with Python standard-library dataclasses, enums, and explicit `from_mapping` validation boundaries.
- Reason: Gate 2 needs typed schema validation, but the current scope does not require a production validation dependency.
- Alternatives: Add Pydantic immediately; defer all schema implementation.
- Risks: Future schema complexity may require migrating to Pydantic or another structured validation library.
- Follow-up: Reconsider a validation dependency only when schema complexity or adapter integration warrants it.

### 2026-05-10 — Implement Gate 3 Markdown ingestion with a minimal standard-library parser

- Decision: Implement Markdown ingestion in a storage adapter using only the Python standard library, with a constrained frontmatter parser for flat key/value pairs and string lists.
- Reason: Gate 3 needs read-only Markdown ingestion, source refs, and content hashes, but current fixture evidence does not justify a production Markdown or YAML dependency.
- Alternatives: Add PyYAML or a Markdown parser immediately; defer frontmatter parsing until later.
- Risks: Real-world essays may need richer YAML or Markdown parsing, and changing generated source id strategy later may require migration notes.
- Follow-up: Reconsider parser dependencies after MVP fixture/golden tests show concrete parsing requirements.

### 2026-05-10 — Keep Gate 4 extraction provider-neutral

- Decision: Implement AI extraction proposal validation as a provider-neutral boundary that accepts already-structured output, validates it into domain candidates, and records typed run logs without calling an LLM provider.
- Reason: Gate 4 needs structured output validation and run logs, but real provider calls would introduce external service, cost, prompt, and dependency decisions before the patch review workflow is stable.
- Alternatives: Add a concrete provider SDK now; defer AI boundary code until provider integration.
- Risks: Extraction quality cannot be measured until prompts, provider adapters, and golden fixtures exist.
- Follow-up: Add durable `_ai_runs/` storage and provider adapter interfaces in future tasks before real model calls are enabled.

### 2026-05-10 — Keep Gate 5 patch review separate from formal vault apply

- Decision: Implement patch review in the application layer as patch generation, diff inspection, rollback instructions, and accept/reject handoff without writing formal vault files.
- Reason: Gate 5 needs user acceptance before formal writes, while actual file mutation belongs in a future storage adapter.
- Alternatives: Apply accepted patches to Markdown files immediately; defer patch review until storage apply exists.
- Risks: Diff output is a structured summary rather than a real file diff, and duplicate path/ID checks need a vault index later.
- Follow-up: Add patch persistence and storage apply/revert behavior in later tasks while reusing `validate_patch_review_safety`.

### 2026-05-10 — Keep Gate 6 blog drafting deterministic and provider-free

- Decision: Implement blog draft generation as deterministic application-layer scaffolding from accepted patch review results, with claim inventory, unsupported claim reporting, and quality reports.
- Reason: Gate 6 needs blog draft safety and evidence coverage before real LLM editorial generation, publishing, or draft persistence.
- Alternatives: Add provider-backed prose generation now; defer blog draft workflow until formal vault apply exists.
- Risks: Draft content is not final editorial prose, and accepted units are sourced from accepted patch review results until formal apply behavior exists.
- Follow-up: Add durable draft persistence/export and provider-backed editorial drafting only after fixtures, provider policy, and review UX are ready.

### 2026-05-10 — Validate Gate 7 with deterministic release readiness fixtures

- Decision: Implement Gate 7 release readiness as an application-layer harness that runs five deterministic Markdown fixtures through ingestion, structured extraction validation, patch review acceptance, and blog draft generation without provider calls or formal vault writes.
- Reason: Gate 7 needs an end-to-end safety check across the MVP skeleton while preserving provider neutrality and the formal write boundary.
- Alternatives: Add real LLM provider calls and formal vault apply behavior now; mark Gate 7 manually without a runnable harness.
- Risks: The fixtures prove orchestration and boundary safety, not real extraction quality or editorial quality.
- Follow-up: Add product-owner-approved golden essays, durable AI working artifacts, candidate Markdown rendering/export, and formal vault apply/revert only after their safety checks are designed.

### 2026-05-11 — Export candidate Markdown only under AI suggestions

- Decision: Render candidate Markdown notes from safe `KnowledgePatch` create-note operations and write them only under `_ai_suggestions/candidate-notes/<patch_id>/`.
- Reason: MVP output needs candidate Markdown notes, but formal vault mutation must remain behind explicit patch acceptance and future storage apply/revert safety checks.
- Alternatives: Write candidate notes directly to formal target paths; defer candidate Markdown output until formal apply exists.
- Risks: The current frontmatter renderer is minimal and candidate note format may change when review UI and formal apply/revert are implemented.
- Follow-up: Add durable patch persistence, review report rendering, duplicate target checks, and formal apply/revert in separate reviewed milestones.

### 2026-05-11 — Export patch review reports only under AI reports

- Decision: Render patch review reports from safe `KnowledgePatch` values and write them only under `_ai_reports/patch-reviews/<patch_id>.md`.
- Reason: The MVP needs review reports before formal writes, and reports should summarize diff, candidate note paths, risks, and rollback steps without acting as acceptance records.
- Alternatives: Treat patch acceptance as the review report; defer review reports until a UI exists; write reports beside formal notes.
- Risks: Report format may change once durable patch persistence, review UI, and formal apply/revert exist.
- Follow-up: Add a combined review package writer and raw patch persistence so reports, candidate notes, and patch files can be reviewed together.

### 2026-05-11 — Persist review packages only in AI working directories

- Decision: Persist raw patch JSON, candidate notes, and patch review reports together as a review package, constrained to `_ai_suggestions/` and `_ai_reports/`.
- Reason: Human review needs a coherent artifact package before formal apply/revert, but the package must not imply acceptance or mutate formal vault files.
- Alternatives: Persist only raw patch JSON; persist only report and candidate notes; write package artifacts beside formal target paths.
- Risks: The current package write is not transactional, and raw patch JSON may need explicit versioning once external consumers depend on it.
- Follow-up: Add AI run log and blog draft persistence, then add duplicate path/ID checks before formal apply/revert.

### 2026-05-11 — Persist AI run logs without raw AI output

- Decision: Persist typed AI run logs under `_ai_runs/<run_id>.json`, including run metadata, hashes, validation status, `created_at`, and optional cache metadata, while excluding raw model output.
- Reason: Traceability needs durable run artifacts, but raw AI output should remain outside durable run logs until retention and privacy behavior are explicitly designed.
- Alternatives: Do not persist run logs; persist raw model outputs with run logs; wait for real provider integration.
- Risks: The run artifact JSON shape may need versioning before CLI/UI consumers depend on it.
- Follow-up: Add explicit artifact schema versioning and provider-specific metadata only when real provider adapters are introduced.

### 2026-05-11 — Persist blog draft packages only in AI working directories

- Decision: Persist blog draft Markdown under `_ai_suggestions/blog-drafts/<draft_id>/draft.md` and blog quality reports under `_ai_reports/blog-quality/<draft_id>.md`.
- Reason: Local trial and review workflows need durable draft artifacts, while publishing and formal vault mutation must remain behind explicit future approval.
- Alternatives: Keep drafts in memory only; write drafts directly to `70-publications/`; defer draft persistence until a CLI exists.
- Risks: The artifact Markdown shape may need explicit versioning before CLI/UI consumers depend on it, and deterministic draft content is still scaffold-quality prose.
- Follow-up: Add a local trial harness or CLI that writes review packages, run logs, and draft packages together without formal vault mutation.

### 2026-05-11 — Local trial uses structured extraction JSON before provider integration

- Decision: Add a local trial harness and module-based CLI that accepts one Markdown essay plus structured extraction JSON, then writes AI run logs, review packages, and blog draft packages under AI working directories.
- Reason: The product owner needs a way to inspect current tool output, while real provider calls, prompt execution, auth, cost, and model policy are not approved yet.
- Alternatives: Add a real provider call now; generate fake extraction internally; wait until formal vault apply exists before exposing any local trial path.
- Risks: The trial still requires structured JSON, and simulated patch acceptance for draft generation must not be confused with user approval for formal vault apply.
- Follow-up: Add artifact schema versioning, product-owner-approved golden essays, and provider adapters only after the review boundary remains stable.

### 2026-05-11 — Version AI working artifacts separately from domain schemas

- Decision: Add a shared `artifact_schema_version` value of `0.1.0` to persisted AI working artifacts.
- Reason: Local trial outputs are now user-visible files, and version markers make future replay, migration, and CLI/UI compatibility safer without changing formal domain schemas.
- Alternatives: Leave artifacts unversioned; bump formal domain `schema_version`; assign independent versions to every artifact type immediately.
- Risks: Future artifact formats may diverge and require per-artifact versioning or tolerant readers for older unversioned artifacts.
- Follow-up: Add compatibility handling when artifact import/replay is introduced and document any future artifact schema bumps.

### 2026-05-11 — Provide a checked-in local trial fixture pair

- Decision: Add a small Markdown essay fixture and matching structured extraction JSON fixture under `tests/fixtures/local_trial/`.
- Reason: The product owner needs a ready-to-run local trial without manually authoring extraction JSON before provider integration exists.
- Alternatives: Keep only synthetic unit-test fixtures; generate extraction JSON dynamically; wait for a provider adapter before adding trial fixtures.
- Risks: The fixture proves orchestration and artifact output, not real extraction quality or editorial quality.
- Follow-up: Promote or replace fixtures with product-owner-approved golden essays and add user-facing extraction JSON schema notes.

### 2026-05-12 — Document local trial extraction JSON without changing runtime schema

- Decision: Add a standalone guide for the existing local trial extraction JSON input shape and validate the guide's embedded example through the current extraction validator.
- Reason: Product-owner trial runs need a concise authoring reference before provider integration exists, but this stage should not change runtime schema or introduce a machine-readable schema dependency.
- Alternatives: Keep only the checked-in fixture; add a JSON Schema document now; implement a provider adapter before documenting hand-authored JSON.
- Risks: The guide can drift if extraction validation changes, and hand-authored JSON still does not measure real extraction quality.
- Follow-up: Add machine-readable schema or richer authoring helpers only when external trial users or provider adapters require them.

### 2026-05-12 — Add read-only formal vault conflict checks before apply behavior

- Decision: Add a storage adapter preflight that checks `KnowledgePatch` create-note operations for existing formal target paths, existing formal note IDs, and duplicate patch target IDs/paths without writing vault files.
- Reason: Formal apply/revert needs path and ID safety before mutation can be reviewed, but enabling writes now would cross the formal vault boundary too early.
- Alternatives: Implement formal apply immediately; keep conflicts as review-report prose only; wait for a full vault index.
- Risks: The minimal frontmatter ID reader may miss complex YAML forms, and path/ID checks are necessary but not sufficient for future rollback safety.
- Follow-up: Add explicit apply/revert boundaries, rollback/write-failure tests, and richer frontmatter parsing only when fixtures prove the need.

### 2026-05-12 — Add formal apply dry-run plans before write execution

- Decision: Add a storage adapter dry-run plan that converts a conflict-free `KnowledgePatch` into planned formal note files, content hashes, and rollback steps without writing vault files.
- Reason: Future formal apply/revert needs an explicit, reviewable execution boundary before mutation is implemented.
- Alternatives: Implement formal apply immediately; keep only candidate Markdown artifacts; wait until a UI exists.
- Risks: The planned note renderer may need richer formatting before real apply, and dry-run plans do not prove write atomicity or rollback execution.
- Follow-up: Add explicit user acceptance handoff, write-failure tests, and revert execution before enabling formal vault mutation.

### 2026-05-14 — Write local trial feedback reports as the trial entrypoint

- Decision: Each local trial should write a Markdown feedback report under `_ai_reports/local-trials/<trial_id>.md` and include it in CLI output.
- Reason: Product-owner trials need one starting artifact that explains status, safety boundaries, reading order, errors, unsupported claims, and feedback prompts without adding provider calls or formal vault writes.
- Alternatives: Keep trial output only as scattered paths; build a UI first; write reports beside formal notes.
- Risks: The report format may need adjustment after real trial feedback, and the report must not be mistaken for user acceptance of a patch.
- Follow-up: Use the report in controlled trial review, then decide whether a richer feedback rubric, JSON summary, or UI surface is warranted.

### 2026-05-14 — Capture local trial feedback in the report artifact

- Decision: Add a human-fillable `Feedback Capture` section to local trial reports and document the safe trial review flow in `docs/guides/local-trial-user-feedback.md`.
- Reason: Product-owner trials need a durable place to record usability feedback while keeping feedback separate from patch acceptance, formal write approval, and publication approval.
- Alternatives: Keep feedback in chat only; create a separate feedback file; build a UI before collecting structured feedback.
- Risks: The rubric may need tuning after real trial use, and report edits are not machine-readable yet.
- Follow-up: After a controlled trial, decide which feedback fields should become release criteria, golden fixture expectations, or a structured feedback artifact.

### 2026-05-14 — Add minimal package metadata for CLI trial entrypoint

- Decision: Add `pyproject.toml`, expose `diamonddust = "diamonddust.cli:main"`, and add `python3 -m diamonddust` as a module entrypoint.
- Reason: Product-owner trial runs should have a standard command after editable install, while development can still use the module fallback.
- Alternatives: Keep only `PYTHONPATH=src python3 -m diamonddust.cli`; add a shell wrapper; wait until CI/release packaging exists.
- Risks: Packaging metadata may need expansion for real releases, and editable install behavior depends on local Python packaging tooling.
- Follow-up: Add CI and release/versioning checks before treating the package metadata as a release contract.

### 2026-05-14 — Add a one-command local trial fixture shortcut

- Decision: Add `diamonddust local-trial-fixture` as a shortcut for the checked-in fixture essay and extraction JSON, defaulting output to `knowledge-vault/`.
- Reason: Product-owner trial feedback should start from a simple safe command before custom essay extraction JSON is required.
- Alternatives: Keep only the full `local-trial` command; add a shell script; move fixtures into package data before adding a shortcut.
- Risks: The shortcut is repo-root oriented and proves fixture orchestration, not real provider extraction quality.
- Follow-up: Use the shortcut for controlled trial feedback, then decide whether fixture command behavior should become package-data-backed or CI-gated.

### 2026-05-14 — Add GitHub Actions as the CI validation baseline

- Decision: Add a GitHub Actions workflow that runs on pull requests and pushes, covering editable install, unit tests, compile checks, whitespace checks, and the `diamonddust local-trial-fixture` smoke path on Python 3.11 and 3.12.
- Reason: Local trial work is now user-visible enough that PR review should have automated validation instead of relying only on local milestone checks.
- Alternatives: Keep validation local only; add a shell script without remote CI; add heavier lint/typecheck tooling immediately.
- Risks: The first remote runner execution still needs to be observed after push, and branch protection must be configured separately if CI should block merges.
- Follow-up: Confirm the first remote CI run and decide whether GitHub branch protection should require the workflow before merge.

### 2026-05-14 — Package the provider-free local trial fixture assets

- Decision: Include the local trial essay and extraction JSON as package data under `diamonddust.fixtures.local_trial`, and load the `local-trial-fixture` shortcut from package resources instead of repository-relative test fixture paths.
- Reason: Product-owner trial runs should work after editable install from any working directory, not only from the repository root.
- Alternatives: Keep the shortcut repo-root oriented; require users to pass explicit fixture paths; move all test fixtures into package data.
- Risks: Packaged fixture assets can drift from repository fixture assets if parity tests are removed, and the fixture still validates artifact UX rather than real provider extraction quality.
- Follow-up: Run a controlled installed-CLI product-owner trial, then decide which real or semi-real essays should become golden fixtures.

### 2026-05-14 — Validate CI from a built wheel

- Decision: CI builds a DiamondDust wheel with `pip wheel`, installs that wheel with `pip install --force-reinstall --no-deps`, runs `pip check`, and then executes tests and local trial fixture smoke against the installed package.
- Reason: The packaged local trial fixture assets must be verified inside installable artifacts, not only editable source checkouts.
- Alternatives: Keep editable install validation only; add a release publishing workflow immediately; add an external build tool dependency.
- Risks: The current local Codex shell cannot reproduce wheel build/install because `pip` is unavailable, so remote GitHub Actions remains the source of truth for this gate.
- Follow-up: Confirm the first remote CI run, then decide later when versioning, artifact upload, and publishing should become release gates.

## Template

### YYYY-MM-DD — <decision title>

- Decision:
- Reason:
- Alternatives:
- Risks:
- Follow-up:
