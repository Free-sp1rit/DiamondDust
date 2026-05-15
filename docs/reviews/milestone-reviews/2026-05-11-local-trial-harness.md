# Milestone Review: Local Trial Harness

## Scope Reviewed

Local trial harness implementation on branch `feat/local-trial-harness`.

Reviewed scope:

- `src/diamonddust/application/local_trial.py`
- `src/diamonddust/application/__init__.py`
- `src/diamonddust/cli.py`
- `tests/unit/test_local_trial.py`
- `docs/exec-plans/completed/2026-05-11-local-trial-harness.md`

## Product Goal Alignment

Aligned. The implementation gives the product owner a local trial path that turns one Markdown essay plus structured extraction JSON into inspectable AI working artifacts.

The workflow now supports:

- Markdown ingestion;
- structured extraction validation;
- AI run log persistence;
- review package persistence;
- non-persisted accepted review handoff for draft preview generation;
- blog draft package persistence;
- CLI output of written artifact paths and errors.

## Architecture Boundary Compliance

Compliant.

- Local trial orchestration lives in the application layer.
- Markdown and artifact writes remain in storage adapters.
- Provider-specific behavior is not introduced.
- The CLI is a thin interface wrapper over the application harness.
- No domain core dependency on provider SDKs, UI frameworks, storage engines, or external services was introduced.

## Cohesion Assessment

Good. The local trial module has one responsibility: orchestrate the current MVP skeleton for one trial run and report stage status.

## Coupling Assessment

Acceptable. Coupling is intentionally to existing application and storage boundaries. The harness does not introduce a new extraction engine or bypass typed validation.

## Data and Schema Safety

Compliant for this milestone.

- Structured extraction output enters through the existing provider-neutral validation boundary.
- Invalid extraction output fails safely and persists a failed AI run log.
- Source ID mismatches stop before review package and draft package writes.
- Written artifacts stay under existing AI working directories.
- No file is written under formal vault publication paths.

No public domain schema version change was introduced.

## AI Output Boundary

Compliant. The local trial requires structured extraction JSON and does not call an LLM provider. It may simulate patch acceptance only to produce downstream draft artifacts, and the result records `formal_write_performed: false` and `provider_called: false`.

## Tests and Evaluation

Validation run:

- `PYTHONPATH=src python3 -m unittest discover -s tests`: 85 tests passed.
- `python3 -m compileall src tests`: passed.
- `git diff --check`: passed.

Coverage added:

- successful local trial writes all inspectable artifacts;
- invalid extraction output persists a failed AI run log and stops safely;
- source ID mismatch stops before review and draft artifacts;
- CLI smoke test for the local-trial command.

## Dependency and Portability Impact

No production or development dependency was added. The CLI uses the Python standard library.

## Risks

- The local trial requires structured extraction JSON until provider integration is approved.
- Simulated patch acceptance could be misunderstood unless docs and CLI output keep formal write boundaries visible.
- The module-based CLI is not yet packaged as an installed console script.

## Required Changes Before Continuing

None.

## Optional Improvements

- Add example extraction JSON fixtures and user-facing schema notes.
- Add explicit artifact schema versioning before CLI/UI consumers depend on persisted artifact shapes.
- Add product-owner-approved golden essays for trial and regression evaluation.
- Add CI to run the validation suite automatically.

## Escalation Requests

None.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked

The local trial harness may be treated as complete for the current post-Gate 7 hardening stage. Follow-ups are not blockers for artifact versioning, golden fixtures, or CI planning.
