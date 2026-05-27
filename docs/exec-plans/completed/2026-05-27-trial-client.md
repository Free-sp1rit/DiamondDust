# Execution Plan: Trial Client

## Product Goal

Provide a simple local client for a small number of real users to run real-note
`extract_units` trials, inspect extraction artifacts, and record feedback before
DiamondDust continues building more core capabilities.

## Current Understanding

The core provider pipeline can call DeepSeek and persist run logs plus validated
extraction artifacts, but recent real-note testing showed an empty extraction
can pass schema validation. The next product need is rapid real-use feedback,
not more downstream core functionality.

## Assumptions

- The client is local-first and runs on `127.0.0.1`.
- DeepSeek is the first provider exposed in the trial client.
- The local secrets file path is `~/.config/diamonddust/provider-secrets.env`.
- Trial users can place Markdown notes under the configured input directory.
- Trial artifacts remain under ignored `knowledge-vault/` working directories.

## Non-goals

- Do not build a full note editor.
- Do not add frontend or web framework dependencies.
- Do not expose API key values in UI, logs, or persisted feedback.
- Do not persist raw provider request or response bodies.
- Do not generate patches, formal apply, record patch acceptance, or publish.
- Do not support provider-side tools, web search, file search, or MCP.

## Proposed Technical Approach

Add a small standard-library HTTP client under the interface layer and expose it
through `diamonddust trial-client`. The web client calls the existing
`diamonddust deepseek-extract-units` command through a subprocess boundary so
provider SDK imports stay in AI adapter modules and the existing CLI safety
flags remain authoritative.

The client will:

- list Markdown notes from a configured input directory
- load provider secrets into the subprocess environment without returning values
- run DeepSeek extraction with explicit approval flags and controlled defaults
- read the generated run log and validated extraction artifact
- render unit candidates as structured field groups instead of prose-only cards
- compute a trial quality status, including `failed_empty_extraction`
- write small feedback Markdown and JSON files under manual-trial directories
- show safety boundaries and artifact paths for review

## Task Breakdown

- [x] Add trial client execution plan.
- [x] Add local trial client module with service, HTTP handler, and embedded UI.
- [x] Add `diamonddust trial-client` CLI command.
- [x] Add focused tests for secret handling, command construction, empty output
      quality status, feedback persistence, and CLI help.
- [x] Address review feedback that Units output looked unstructured by rendering
      unit fields, source refs, relations, and expandable structured JSON.
- [x] Update docs/context and milestone review.
- [x] Run validation.

## Likely Files Changed

- `docs/guides/trial-client.md`
- `src/diamonddust/interface/__init__.py`
- `src/diamonddust/interface/trial_client.py`
- `src/diamonddust/cli.py`
- `tests/unit/test_trial_client.py`
- `tests/unit/test_cli_entrypoints.py`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-27-trial-client.md`

## Validation Plan

- [x] focused trial client tests
- [x] focused CLI entrypoint test
- [x] full unit test suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan
- [x] manual client start smoke

## Validation Results

- `PYTHONPATH=src .venv/bin/python -m unittest tests.unit.test_trial_client tests.unit.test_cli_entrypoints`: 29 tests passed.
- `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests`: 269 tests passed.
- `.venv/bin/python -m compileall src tests`: passed.
- `git diff --check`: passed.
- `PYTHONPATH=src .venv/bin/python -m diamonddust local-trial-fixture`: passed with `provider_called: false` and `formal_write_performed: false`.
- Architecture boundary scan: 0 critical violations.
- Manual client smoke: `diamonddust trial-client --port 8766` served `/api/status`; the smoke server was stopped after validation.

## Review Gate Impact

This introduces a new interface adapter and real-provider trial workflow, so a
milestone review is required.

## Risks

- The client could make real provider calls easier than intended; keep explicit
  local-only scope, visible boundaries, and no formal write behavior.
- Empty extractions may still pass typed schema; the client must surface them as
  quality failures.
- A subprocess wrapper can drift from CLI flags; tests should pin the command
  construction.

## Escalation Needed

Does this require user approval?

- [x] no: the product owner explicitly requested this trial-client stage.
- [ ] yes

## Definition of Done

- `diamonddust trial-client` starts a local browser client.
- A tester can select a Markdown note, run DeepSeek extraction, inspect units,
  relations, safety boundaries, and artifact paths, and save feedback.
- Empty real-note extractions are visibly marked as failed quality, not useful
  output.
- No API key value is displayed or persisted by the client.
- No formal vault write, patch acceptance, or publication is possible from the
  client.
