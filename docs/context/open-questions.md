# Open Questions

Record unresolved product, architecture, schema, dependency, or governance questions here.

Last updated: 2026-05-14

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

### 2026-05-14 — Which local trial feedback fields should become release criteria?

- Context: Local trial runs now write `_ai_reports/local-trials/<trial_id>.md` with prompts and a human-fillable feedback capture rubric, plus `_ai_reports/local-trials/<trial_id>.json` for machine-readable trial outcome summaries. The rubric and JSON shape have not yet been validated by a real product-owner trial.
- Needed decision: After the first controlled trial, decide which feedback fields should become durable acceptance criteria or test fixtures.
- Impact: Affects whether the next phase should prioritize golden essays, report quality, formal apply safety, or provider-backed extraction.

## AI Pipeline

### 2026-05-12 — When should extraction JSON get a machine-readable schema?

- Context: The local trial CLI now has a checked-in example extraction JSON fixture and a user-facing guide with a validated embedded example, but no JSON Schema or generated authoring helper exists.
- Needed decision: Add machine-readable schema only if broader trial usage, provider adapter handoff, or external tooling needs it.
- Impact: Affects validation clarity, compatibility guarantees, and future schema migration surface.

### 2026-05-11 — When should artifact versions diverge by artifact type?

- Context: Persisted AI working artifacts now share `artifact_schema_version: 0.1.0`.
- Needed decision: Introduce per-artifact versioning only if run logs, patch packages, review reports, or draft packages evolve independently enough that one shared version becomes misleading.
- Impact: Affects migration strategy, compatibility checks, and future artifact import/replay behavior.

### 2026-05-10 — Which provider adapter should be implemented first?

- Context: Gate 4 is provider-neutral and does not call an LLM.
- Needed decision: Choose provider adapter and model policy only when the patch review workflow is ready for real model output.
- Impact: Affects dependencies, cost, auth, prompt design, and run log fields.

## Patch Review

### 2026-05-11 — Should review package writes become transactional?

- Context: Review package persistence writes raw patch JSON, candidate notes, and review report together, but does not yet provide transaction or rollback behavior if one artifact write fails.
- Needed decision: Decide whether filesystem transaction semantics are needed before real CLI/UI review flows.
- Impact: Affects review artifact consistency, replay, and failure recovery.

### 2026-05-10 — When should storage apply/revert behavior be implemented?

- Context: Gate 5 models accepted patch handoff but does not mutate formal vault files. Patch persistence, read-only path/ID conflict checks, and dry-run apply plans now exist.
- Needed decision: Implement storage adapter apply/revert execution only after explicit user acceptance handoff, rollback behavior, and write-failure tests are designed.
- Impact: Affects formal write safety, rollback guarantees, and Git diff inspection.

## Blog Draft

### 2026-05-10 — When should provider-backed editorial drafting be introduced?

- Context: Gate 6 uses deterministic scaffolding from accepted units and does not call an LLM.
- Needed decision: Introduce provider-backed prose generation only after provider policy, prompt versions, fixtures, and quality thresholds are ready.
- Impact: Affects dependencies, cost, evidence coverage, unsupported claim risk, and quality evaluation.

## Release Automation

### 2026-05-14 — When should release publishing and versioning become gated?

- Context: CI now validates wheel build/install and the `diamonddust local-trial-fixture` smoke path, but no release workflow uploads build artifacts, checks version tags, or publishes distributions.
- Needed decision: Decide when versioning policy, artifact upload, and package publishing should become blocking release gates.
- Impact: Affects future distribution, changelog/version discipline, and whether users can install DiamondDust outside local source checkouts.

### 2026-05-14 — Should GitHub branch protection require CI before merge?

- Context: Repository-file CI now runs install, unit tests, compile checks, whitespace checks, and local trial fixture smoke on pull requests and pushes. GitHub branch protection is not configured by repository files.
- Needed decision: Decide whether to require the CI check through GitHub branch protection before merging PRs.
- Impact: Affects review reliability, merge safety, and future contributor workflow.
