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

## Template

### YYYY-MM-DD — <decision title>

- Decision:
- Reason:
- Alternatives:
- Risks:
- Follow-up:
