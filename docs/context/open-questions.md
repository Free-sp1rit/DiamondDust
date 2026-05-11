# Open Questions

Record unresolved product, architecture, schema, dependency, or governance questions here.

Last updated: 2026-05-11

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

- Context: Gate 7 now has five deterministic Markdown fixtures for readiness tests, but they are not yet product-owner-approved golden essays.
- Needed decision: Identify or create real or semi-real fixture essays before golden quality evaluation is finalized.
- Impact: Affects extraction quality evaluation, regression coverage, and release confidence.

### 2026-05-11 — When should candidate Markdown export use a richer serializer?

- Context: Candidate Markdown export now uses a minimal standard-library YAML-like renderer.
- Needed decision: Reconsider a serializer dependency only if review fixtures need richer frontmatter or round-trip parsing.
- Impact: Affects candidate note fidelity, dependency posture, and future migration surface.

## AI Pipeline

### 2026-05-11 — Should AI run log artifacts get an explicit schema version?

- Context: AI run logs are now persisted under `_ai_runs/`, but the artifact JSON does not yet have a separate artifact schema version.
- Needed decision: Add explicit artifact schema versioning before external CLI/UI consumers depend on the JSON shape.
- Impact: Affects traceability, debugging, replay, and future cache migrations.

### 2026-05-10 — Which provider adapter should be implemented first?

- Context: Gate 4 is provider-neutral and does not call an LLM.
- Needed decision: Choose provider adapter and model policy only when the patch review workflow is ready for real model output.
- Impact: Affects dependencies, cost, auth, prompt design, and run log fields.

## Patch Review

### 2026-05-11 — Should raw patch JSON get an explicit artifact schema version?

- Context: Review package persistence now writes raw patch JSON under `_ai_suggestions/patches/`, but the artifact format currently mirrors existing domain schema values without a separate artifact schema version.
- Needed decision: Add explicit artifact schema versioning before external CLI/UI consumers depend on the JSON shape.
- Impact: Affects traceability, replay, auditability, and future migration behavior.

### 2026-05-11 — Should review package writes become transactional?

- Context: Review package persistence writes raw patch JSON, candidate notes, and review report together, but does not yet provide transaction or rollback behavior if one artifact write fails.
- Needed decision: Decide whether filesystem transaction semantics are needed before real CLI/UI review flows.
- Impact: Affects review artifact consistency, replay, and failure recovery.

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

## Release Automation

### 2026-05-10 — When should CI become a required PR gate?

- Context: Gate 7 validation is currently local: unit tests, compile check, and diff check.
- Needed decision: Decide when to add CI and which checks should block PR merge.
- Impact: Affects review reliability, merge safety, and future contributor workflow.
