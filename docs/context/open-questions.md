# Open Questions

Record unresolved product, architecture, schema, dependency, or governance questions here.

Last updated: 2026-05-10

## Governance Approval

### 2026-05-10 — Are Gate 0 and Gate 1 startup documents approved?

- Context: `AGENTS.md`, `GOVERNANCE_REVIEW_NOTES.md`, and `docs/00` through `docs/14` now define the startup governance and architecture baseline.
- Needed decision: Product owner should review and approve, request changes, or explicitly defer parts of the governance set.
- Impact: Product implementation should not begin until the applicable gate state is clear.

## Tooling and Repository Shape

### 2026-05-10 — Should repo-local skills be wired into Codex discovery?

- Context: Minimal governance skills were created under `skills/` because `.codex/` and `.agents/` are read-only in this workspace.
- Needed decision: Confirm whether `skills/` is the desired durable repo-local path or whether a later install/discovery step should mirror them into the active Codex skill directory.
- Impact: Affects whether future sessions can trigger these skills automatically or must load them by path.

### 2026-05-10 — What minimal test/tooling setup should Gate 3 use?

- Context: Gate 2 uses standard-library unittest and no dependency metadata. Gate 3 may need Markdown parsing and fixtures.
- Needed decision: The coding agent can propose the smallest coherent tooling plan; escalation is needed if a production dependency or governance impact exceeds the approved boundary.
- Impact: Determines whether Gate 3 can read Markdown essays, parse optional frontmatter, preserve source refs, and compute content hashes.

## Fixtures

### 2026-05-10 — Which essays should become the MVP golden fixtures?

- Context: MVP success requires 5 real or semi-real Markdown essays passing the end-to-end flow.
- Needed decision: Identify or create fixture essays before golden and integration tests are finalized.
- Impact: Affects extraction quality evaluation and regression coverage.
