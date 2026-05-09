# Milestone Review: Initialization Acceptance

## Scope Reviewed

This review validates the DiamondDust context initialization and minimal governance skills.

Reviewed inputs:

- `AGENTS.md`
- `GOVERNANCE_REVIEW_NOTES.md`
- `README.md`
- `docs/00_PROJECT_CHARTER.md` through `docs/14_CONSTRAINT_ESCALATION_POLICY.md`
- `docs/context/*`
- `docs/exec-plans/completed/*`
- `skills/spec-to-plan/SKILL.md`
- `skills/constraint-escalation/SKILL.md`
- `skills/milestone-review/SKILL.md`
- `skills/pr-review/SKILL.md`
- `skills/git-workflow/SKILL.md`

This review did not inspect or create product implementation code.

## 1. Context Understanding

DiamondDust is a local-first semantic knowledge compiler. It turns Markdown essays into structured knowledge units, then recomposes those units into reviewable patches, knowledge-base artifacts, and blog drafts.

MVP scope:

- read a Markdown essay
- extract `KnowledgeUnit` candidates
- generate `Relation` candidates
- generate and validate `KnowledgePatch`
- output a review report
- write to Markdown vault only after user acceptance
- generate a blog draft and blog quality report from accepted knowledge

Non-goals:

- full note editor
- automatic blog publishing
- model training
- Obsidian plugin, Notion sync, or MCP server
- PDF, image, LaTeX, or code project parsing
- graph visualization
- complex runtime agent autonomy

Architecture invariants:

- Markdown is the source of truth.
- SQLite, vector indexes, and caches are rebuildable.
- Domain Core must not depend on provider SDKs, UI frameworks, storage engines, note-taking platforms, or MCP SDKs.
- AI adapters handle provider calls, structured output, retry, and model routing.
- Storage adapters handle Markdown, SQLite, vector index, and Git behavior.
- UI or interface adapters must not contain domain rules.

AI output boundaries:

- LLM output may produce candidates, relations, patches, drafts, and reports.
- LLM output must not directly overwrite formal notes, delete user content, mark knowledge as evergreen without review, publish content, or invent sources.
- Formal knowledge writes require a validated `KnowledgePatch` and explicit user acceptance.

Git workflow:

- Development must use branch-based PR workflow when Git and remote access are available.
- Do not work, commit, push, or merge directly on `main`.
- Use one coherent task branch per task.
- Push and PR readiness must follow `docs/10_GIT_WORKFLOW.md`.
- Current branch during this review: `chore/context-initialization`.
- This review did not push or merge.

Runtime AI autonomy and coding agent development autonomy are distinct:

- Runtime AI is product behavior and must remain behind the patch review workflow.
- The coding agent may autonomously plan, edit code or docs, test, review, and propose changes inside the approved task scope.
- High-impact coding-agent actions require escalation.

## 2. Skill Boundary Check

Responsibility boundaries:

- `docs/` holds DiamondDust product facts, architecture, schema, AI boundary, review gates, dependency rules, Git workflow, planning policy, and escalation policy.
- `AGENTS.md` is the coding-agent navigation and operating-control plane.
- `skills/` holds reusable process guidance only.
- `tests/lint/CI` should hold executable hard constraints once project tooling exists.

Current governance skill triggers:

- `spec-to-plan`: turn a request, issue, rough feature brief, or ambiguous task into an execution plan.
- `constraint-escalation`: respond when a rule, instruction, dependency limit, architecture boundary, permission model, tool limitation, or user request blocks quality or requires high-impact behavior.
- `milestone-review`: run a review at stable or risky boundaries such as module, API, schema, storage, AI task, adapter, dependency, permission, formal write behavior, or review gate state.
- `pr-review`: inspect branch scope, diff, tests, docs, risks, unresolved escalations, and PR notes before PR readiness.
- `git-workflow`: guide branch, dirty worktree, commit, sync, push, and PR workflow without mixing unrelated changes.

Product implementation skills that should not be created yet:

- `markdown-ingestion`
- `knowledge-unit-extraction`
- `knowledge-patch-apply`
- `formal-vault-writer`
- `blog-draft-generation`
- provider-specific AI skills such as `ai-provider-openai`
- `vector-index`
- `obsidian-plugin`
- `notion-sync`
- `mcp-server`

Reason: these would prematurely encode product implementation workflows before the patch review workflow and early gates are stable.

## 3. Planning Dry Run: Gate 2 Schema Skeleton

Execution Plan: Gate 2 Schema Skeleton

Product goal:

Implement the minimum domain schema skeleton needed for typed validation of `KnowledgeUnit`, `Relation`, and `KnowledgePatch`, satisfying Gate 2 conditions.

Affected docs:

- `docs/04_DOMAIN_MODEL.md`
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md`
- `docs/07_QUALITY_AND_TEST_POLICY.md`
- `docs/09_REVIEW_GATES.md`
- `docs/context/*`
- `docs/exec-plans/active/<gate-2-schema-skeleton>.md`

Likely implementation files:

- project package or module for domain schemas
- domain validation tests
- patch validation tests
- project tooling metadata only if needed to run tests

Required tests:

- allowed unit types, status values, confidence values, and relation types validate
- `KnowledgeUnit` required fields validate
- `SourceRef` required fields validate
- `Relation` required fields validate
- `KnowledgePatch` required fields validate
- invalid relation type fails
- patch missing user review requirement fails
- domain layer does not pass untyped JSON across its boundary

Risks:

- Python package and test tooling are not materialized yet.
- Adding Pydantic or tooling may require dependency notes or escalation if treated as production dependency impact.
- Gate 2 introduces public schema behavior and requires milestone review before marking the gate passed.

Review gate impact:

- Directly targets Gate 2: Schema Skeleton.
- Must not be marked passed until schema implementation exists, validation tests pass, blockers are absent or waived, and milestone review is complete.

Escalation needs:

- No escalation for planning.
- Escalate before adding unapproved production dependencies.
- Escalate before changing public schema beyond the current docs baseline.
- Escalate before weakening patch validation or allowing untyped JSON through the domain layer.

This review does not create the Gate 2 active execution plan.

## 4. Constraint Escalation Test

Scenario: the user asks to skip `KnowledgePatch` and let the LLM write directly to the formal vault.

Correct response:

Refuse direct execution. Explain that the request conflicts with AI output boundary, data contract, review gates, quality policy, and `AGENTS.md` forbidden rules. Do not silently bypass the constraints and do not change formal write behavior without escalation.

Escalation request:

```text
# Escalation Request: Direct LLM Formal Vault Write

## Blocked Goal

Accelerate writing from LLM output into the formal vault.

## Conflicting Constraint

LLM output must not directly overwrite formal notes. Formal writes require a validated KnowledgePatch and user acceptance.

## Why Following It Reduces Quality

Direct LLM formal writes would break reviewability, rollback, traceability, source preservation, schema safety, and formal-vault integrity.

## Recommended Change

Do not approve direct writes. Keep KnowledgePatch and improve patch generation or review UX instead.

## Affected Files or Rules

AGENTS.md, docs/05_DATA_AND_SCHEMA_CONTRACT.md, docs/06_AI_PIPELINE_CONTRACT.md, docs/07_QUALITY_AND_TEST_POLICY.md, docs/09_REVIEW_GATES.md.

## Risks If Approved

Formal knowledge pollution, user content overwrite, source fabrication, schema drift, broken review gates, and loss of MVP safety invariants.

## Safe Fallback If Denied

Write LLM output only to _ai_suggestions/, _ai_reports/, or draft areas; generate a validated patch and diff; wait for explicit user acceptance before formal write.

## Exact User Decision Needed

Approve or deny changing formal write behavior. Recommended decision: deny direct writes and use the safe fallback.
```

## 5. Git Workflow Test

Before Gate 2 implementation:

1. Confirm whether `chore/context-initialization` has been reviewed, committed, pushed, and prepared as PR.
2. Do not mix Gate 2 product implementation into the current dirty initialization branch.
3. Start from latest `main` and create a new branch such as `feat/schema-skeleton` or `test/schema-skeleton`.
4. Create the Gate 2 execution plan on that branch.
5. Implement schema and tests.
6. Run validation.
7. Run milestone review.
8. Commit, push the task branch, and prepare a PR when allowed. Do not merge.

Git operations requiring user approval or explicit permission:

- push to remote when network or credential approval is needed
- merge PRs
- push or merge to `main`
- destructive operations such as reset, checkout-overwrite, or deleting uncommitted work
- force-like operations, including force-with-lease when necessary after rebase
- stash, revert, or otherwise hide existing user or prior-agent changes when it would affect current work

## 6. Memory Persistence Test

After a planning-only Gate 2 stage, update:

- `docs/exec-plans/active/<gate-2-schema-skeleton>.md` if the plan is actually created
- `docs/context/project-state.md` to show focus entering Gate 2 planning
- `docs/context/open-questions.md` for tooling, dependency, and schema uncertainties
- `docs/context/decisions.md` only if a technical decision is made
- `docs/context/completed-milestones.md` only when the planning stage is completed and compressed

Do not modify fact-source docs or `AGENTS.md` unless a governance change is approved.

If a Gate 2 plan is actually created, proposed changed files:

- `docs/exec-plans/active/2026-05-10-gate-2-schema-skeleton.md`
- `docs/context/project-state.md`
- `docs/context/open-questions.md`
- optionally `docs/context/decisions.md` if tooling or schema implementation decisions are locked

This initialization acceptance review does not create those Gate 2 files.

## 7. Final Initialization Score

Score: 18/20

Passed checks:

- Project mission, MVP, AI boundary, architecture, and Git workflow are recoverable from `docs/` and `AGENTS.md`.
- Runtime AI autonomy and coding-agent development autonomy are clearly separated.
- Governance skills are lightweight and do not copy project facts.
- Governance skill triggers are clear.
- Repo memory records current state, decisions, open questions, and completed milestones.
- Gate 2 planning can begin.

Governance gaps:

- `skills/` is repo-local, but automatic Codex discovery is not verified.
- Current governance docs and skills remain uncommitted and have not entered PR review.
- Gate 0 and Gate 1 are not recorded as passed.
- Gate 2 package and test tooling are not chosen.
- `debug-failure` is recommended in policy but was not in the approved skill creation list and should remain uncreated until separately approved.

Recommended fixes:

- Review, commit, push, and prepare PR for the current governance initialization branch.
- Confirm repo-local `skills/` discovery or install strategy.
- Run governance or milestone review for Gate 0 and Gate 1 and record whether they pass.
- During Gate 2 planning, choose minimal package/test tooling and record dependency impact.
- Create `debug-failure` only after explicit approval.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked

Can enter Gate 2 planning: yes.

Can enter Gate 2 implementation: not yet recommended. Complete governance initialization review, PR readiness, Gate 0/Gate 1 state confirmation, and a Gate 2 execution plan first.
