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
