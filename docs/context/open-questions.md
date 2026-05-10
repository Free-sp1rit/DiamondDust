# Open Questions

Record unresolved product, architecture, schema, dependency, or governance questions here.

Last updated: 2026-05-10

## Tooling and Repository Shape

### 2026-05-10 — Should repo-local skills be wired into Codex discovery?

- Context: Minimal governance skills were created under `skills/` because `.codex/` and `.agents/` are read-only in this workspace.
- Needed decision: Confirm whether `skills/` is the desired durable repo-local path or whether a later install/discovery step should mirror them into the active Codex skill directory.
- Impact: Affects whether future sessions can trigger these skills automatically or must load them by path.

### 2026-05-10 — When should Markdown/frontmatter parsing move beyond the minimal subset?

- Context: Gate 3 was implemented with a standard-library parser for flat frontmatter key/value pairs and string lists.
- Needed decision: Reconsider a Markdown or YAML dependency only after fixture evidence shows the minimal parser is insufficient.
- Impact: Affects parsing fidelity, dependency posture, portability, and future migration notes.

## Fixtures

### 2026-05-10 — Which essays should become the MVP golden fixtures?

- Context: MVP success requires 5 real or semi-real Markdown essays passing the end-to-end flow.
- Needed decision: Identify or create fixture essays before golden and integration tests are finalized.
- Impact: Affects extraction quality evaluation and regression coverage.

## AI Pipeline

### 2026-05-10 — When should AI run logs become durable files?

- Context: Gate 4 returns typed run logs for extraction validation, but does not yet write `_ai_runs/` files.
- Needed decision: Add durable run log storage before real provider calls are introduced.
- Impact: Affects traceability, debugging, replay, and future cache keys.

### 2026-05-10 — Which provider adapter should be implemented first?

- Context: Gate 4 is provider-neutral and does not call an LLM.
- Needed decision: Choose provider adapter and model policy only when the patch review workflow is ready for real model output.
- Impact: Affects dependencies, cost, auth, prompt design, and run log fields.

## Patch Review

### 2026-05-10 — When should KnowledgePatch files become durable suggestions?

- Context: Gate 5 generates typed patches and review results, but does not write `_ai_suggestions/patches/`.
- Needed decision: Add patch persistence before integrating a review UI or real provider outputs.
- Impact: Affects traceability, replay, auditability, and rollback workflows.

### 2026-05-10 — When should storage apply/revert behavior be implemented?

- Context: Gate 5 models accepted patch handoff but does not mutate formal vault files.
- Needed decision: Implement storage adapter apply/revert only after patch persistence and path/ID conflict checks are ready.
- Impact: Affects formal write safety, rollback guarantees, and Git diff inspection.

## Blog Draft

### 2026-05-10 — When should blog drafts become durable files?

- Context: Gate 6 returns typed draft packages and quality reports, but does not write draft files under `knowledge-vault/`.
- Needed decision: Add draft persistence/export after the desired draft directory and review UX are clear.
- Impact: Affects traceability, review flow, and publication workflow.

### 2026-05-10 — When should provider-backed editorial drafting be introduced?

- Context: Gate 6 uses deterministic scaffolding from accepted units and does not call an LLM.
- Needed decision: Introduce provider-backed prose generation only after provider policy, prompt versions, fixtures, and quality thresholds are ready.
- Impact: Affects dependencies, cost, evidence coverage, unsupported claim risk, and quality evaluation.
