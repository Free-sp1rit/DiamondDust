# DiamondDust

DiamondDust is a local-first semantic knowledge compiler that turns scattered essays into structured knowledge dust, then recomposes them into durable knowledge artifacts such as blog drafts, maps, and reviewable knowledge patches.

DiamondDust 是一个本地优先的语义知识编译器：它将零散随笔拆解为更小粒度的结构化知识单元，再将这些知识单元重组为可审阅、可维护、可发布的知识产物。

## Current Stage

The project has completed the Gate 7 MVP release readiness skeleton.

The current implementation includes typed domain schemas, read-only Markdown ingestion, provider-neutral structured extraction validation, provider readiness reporting, AI run log persistence, patch review, candidate Markdown export, patch review report rendering, review package persistence, deterministic blog draft generation, durable blog draft package persistence, a local trial CLI with packaged fixture assets and feedback reports, formal vault conflict preflight checks, formal apply dry-run plans, a five-sample release readiness harness, and GitHub Actions CI for package install, tests, compile checks, whitespace checks, and local trial fixture smoke. Real provider calls, formal vault apply/revert execution, publishing, and UI flows remain future work behind the existing review boundaries.

## Local Trial

The current local trial path uses structured extraction JSON instead of calling an LLM provider.

From the repository root, install locally:

```bash
python3 -m pip install -e .
```

Then run from any working directory:

```bash
diamonddust local-trial-fixture
```

The fixture shortcut uses packaged provider-free fixture assets and writes output to `knowledge-vault/` unless `--vault-root` is provided.

Development fallback from the repository root without installation:

```bash
PYTHONPATH=src python3 -m diamonddust local-trial-fixture
```

For custom essays, use `diamonddust local-trial` with explicit essay, extraction JSON, title, audience, and vault-root arguments.

The command writes AI working artifacts only. It does not write formal vault notes or publish content.

Start review from `_ai_reports/local-trials/<trial-id>.md`. That report lists the trial pipeline status, pending product-owner verdict, safety boundary, artifact reading order with purpose notes, errors, unsupported claims, and feedback prompts.

For machine-readable summaries, each run also writes `_ai_reports/local-trials/<trial-id>.json` with trial pipeline status, pending product-owner verdict, artifact paths, errors, unsupported claim counts, quality-scope limits, and explicit no-provider/no-formal-write boundaries.

The matching `_ai_runs/<run-id>.json` records extraction validation hashes plus provider-free fixture scope, non-applicable cost/latency metrics, and lineage pointers to the downstream local trial report/outcome.

Candidate manifests and blog drafts under `_ai_suggestions/` keep preview/review boundaries visible: candidate manifests point back to the raw KnowledgePatch as operation source of truth, and blog draft frontmatter marks review requirement plus provider-free fixture scope when produced by the local trial.

Patch review reports under `_ai_reports/patch-reviews/` include pending decision metadata, suggested review order, and a non-binding decision prompt; formal patch acceptance remains a separate future decision artifact.

See `docs/guides/local-trial-user-feedback.md` for the safe local trial review flow and feedback capture rubric.

See `docs/guides/local-trial-extraction-json.md` for the extraction JSON shape and a validated minimal example.

To print the machine-readable `extract_units` output schema used for local review and future provider structured-output planning:

```bash
diamonddust extraction-output-schema
```

The schema is a contract aid. Typed runtime validation remains authoritative before extraction output becomes internal domain data.

## Provider Readiness

Before real provider integration, render the current approval checklist:

```bash
diamonddust provider-readiness-report
```

The default report is expected to be `blocked` until provider, model, SDK, API key environment variable, network, prompt externalization, structured output, cost, retry, timeout, raw output retention, and fallback decisions are explicit.

This command does not read API key values, call providers, persist prompt/raw provider output, or approve real provider integration.

To draft a first-provider escalation request from the same decision inputs:

```bash
diamonddust provider-escalation-request
```

The escalation draft is review input only. It does not record approval or authorize implementation by itself.

To render one local review package containing both the readiness report and escalation request draft:

```bash
diamonddust provider-decision-package
```

The package is review input only. It does not record approval, call providers, read API key values, add SDK dependencies, persist prompt/raw provider output, or authorize implementation by itself.

Provider-readiness commands can load decision values from JSON:

```bash
diamonddust provider-decisions-template > provider-decisions.json
diamonddust provider-readiness-report --decisions-json provider-decisions.json
diamonddust provider-escalation-request --decisions-json provider-decisions.json
diamonddust provider-decision-package --decisions-json provider-decisions.json
```

The generated template is blocked by default and must be edited before it can represent real decisions. Decision JSON is diagnostic input, not an approval artifact. It may contain the API key environment variable name, but must not contain API key values.

## Development Validation

CI runs on pull requests and task-branch pushes through GitHub Actions.

The CI baseline is:

```bash
python -m pip wheel . --no-deps --wheel-dir <temporary-wheelhouse>
python -m pip install --force-reinstall --no-deps <built-wheel>
python -m pip check
python -m unittest discover -s tests
python -m compileall src tests
git diff --check
diamonddust local-trial-fixture --vault-root <temporary-vault-root>
```

Local development should run the same checks before PR review when practical.

## MVP Goal

Given a Markdown essay, DiamondDust should produce:

1. Knowledge unit candidates
2. Relation candidates
3. A validated KnowledgePatch
4. A review report
5. A blog draft
6. A blog quality report

All formal writes to the knowledge base must go through a reviewable patch.

## Core Principles

- Markdown files are the source of truth.
- SQLite, vector indexes, and caches are rebuildable.
- AI outputs must pass typed schema validation.
- AI outputs must become proposals, patches, drafts, or reports before any formal write.
- AI must not directly overwrite formal knowledge files.
- The system must remain model-provider neutral and portable.
- Architecture must separate domain core, application pipeline, AI adapters, storage adapters, and interface adapters.
- All development should use branch-based PR workflow when Git remote access is available.
- Coding agents may plan and implement autonomously within approved boundaries.
- High-impact changes require escalation and user approval.

## Development Agent Model

The user acts as product owner. The coding agent acts as development owner.

The agent should own technical planning, task decomposition, implementation, tests, documentation updates, and self-review.

The agent should request user approval only when a decision affects product behavior, public schema, security, permissions, cost, deployment, external services, production dependencies, or project governance rules.

See:

- `docs/11_AGENT_OPERATING_MODEL.md`
- `docs/12_SKILL_USAGE_POLICY.md`
- `docs/13_EXECUTION_PLAN_AND_MEMORY_POLICY.md`
- `docs/14_CONSTRAINT_ESCALATION_POLICY.md`

## Documentation Map

Read these files before implementation:

- `AGENTS.md` — persistent rules for Codex / coding agents
- `docs/00_PROJECT_CHARTER.md` — mission, non-goals, invariants
- `docs/01_MVP_SCOPE.md` — MVP boundary and done conditions
- `docs/02_PRODUCT_SPEC.md` — product flow and review points
- `docs/03_ARCHITECTURE_BOUNDARY.md` — architecture layers and dependency rules
- `docs/04_DOMAIN_MODEL.md` — core domain language
- `docs/05_DATA_AND_SCHEMA_CONTRACT.md` — storage, frontmatter, ID, migration rules
- `docs/06_AI_PIPELINE_CONTRACT.md` — AI task and output boundary
- `docs/07_QUALITY_AND_TEST_POLICY.md` — tests, evaluation, merge blockers
- `docs/08_DEPENDENCY_AND_PORTABILITY_POLICY.md` — dependency and replacement rules
- `docs/09_REVIEW_GATES.md` — phase review gates
- `docs/10_GIT_WORKFLOW.md` — branch and PR workflow
- `docs/11_AGENT_OPERATING_MODEL.md` — agent autonomy and ownership boundaries
- `docs/12_SKILL_USAGE_POLICY.md` — skill vs docs boundary
- `docs/13_EXECUTION_PLAN_AND_MEMORY_POLICY.md` — planning and repo memory
- `docs/14_CONSTRAINT_ESCALATION_POLICY.md` — escalation requests and permission changes

## Development Rule

Before every non-trivial task:

1. Read `AGENTS.md`.
2. Read the relevant docs.
3. Create or update an execution plan.
4. Start from latest `main` and create a task branch when Git is available.
5. Make the smallest coherent change.
6. Add or update tests.
7. Run relevant validation.
8. Update docs if behavior, schema, architecture, workflow, or policy changes.
9. Prepare a PR when remote access is available.
10. Do not push directly to `main`.

## Skill Rule

Skills are reusable workflows. Project docs are the source of truth.

A skill may guide how the agent plans, reviews, debugs, or escalates. A skill must not replace product, architecture, schema, or AI boundary docs.

If skill guidance conflicts with project docs, follow the project docs and create an escalation request if the conflict reduces delivery quality.
