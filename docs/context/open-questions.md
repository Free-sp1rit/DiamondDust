# Open Questions

Record unresolved product, architecture, schema, dependency, or governance questions here.

Last updated: 2026-05-10

## Governance Approval

### 2026-05-10 — Are Gate 0 and Gate 1 startup documents approved?

- Context: `AGENTS.md`, `GOVERNANCE_REVIEW_NOTES.md`, and `docs/00` through `docs/14` now define the startup governance and architecture baseline.
- Needed decision: Product owner should review and approve, request changes, or explicitly defer parts of the governance set.
- Impact: Product implementation should not begin until the applicable gate state is clear.

## First Implementation Milestone

### 2026-05-10 — Should the next task be Gate 2 Schema Skeleton?

- Context: The docs point to `KnowledgeUnit`, `Relation`, and `KnowledgePatch` validation as the first implementation foundation.
- Needed decision: Confirm whether to start the schema skeleton next, or handle a governance review/milestone review first.
- Impact: Determines the first product-code branch and test scope.

## Tooling and Repository Shape

### 2026-05-10 — What concrete Python project layout and test tooling should be used?

- Context: The docs allow Python and Pydantic as core dependencies, but no package layout, dependency file, or test runner is present yet.
- Needed decision: The coding agent can propose the smallest coherent setup when implementation starts; user approval is only needed if production dependencies or project governance change.
- Impact: Affects initial files, validation commands, and CI readiness.

### 2026-05-10 — Should repo-local skills be wired into Codex discovery?

- Context: Minimal governance skills were created under `skills/` because `.codex/` and `.agents/` are read-only in this workspace.
- Needed decision: Confirm whether `skills/` is the desired durable repo-local path or whether a later install/discovery step should mirror them into the active Codex skill directory.
- Impact: Affects whether future sessions can trigger these skills automatically or must load them by path.

### 2026-05-10 — Is local `gh` authentication valid before first `gh pr create`?

- Context: `gh` is installed, but `gh auth status` reported an invalid token in the current shell on 2026-05-10.
- Needed decision: Re-authenticate or verify `gh auth status` before relying on `gh pr create`.
- Impact: Affects whether future task branches can create PRs directly from the CLI.

### 2026-05-10 — What minimal test/tooling setup should Gate 2 use?

- Context: Gate 2 planning can begin, but implementation needs a concrete package and test runner setup.
- Needed decision: The coding agent can propose the smallest coherent tooling plan; escalation is needed only if production dependency or governance impact exceeds the approved boundary.
- Impact: Determines whether Gate 2 can implement typed schema validation and run schema tests.

## Fixtures

### 2026-05-10 — Which essays should become the MVP golden fixtures?

- Context: MVP success requires 5 real or semi-real Markdown essays passing the end-to-end flow.
- Needed decision: Identify or create fixture essays before golden and integration tests are finalized.
- Impact: Affects extraction quality evaluation and regression coverage.
