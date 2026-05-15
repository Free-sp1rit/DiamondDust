# Data and Schema Contract

## Purpose

This document defines how DiamondDust persists knowledge, validates schema, and separates formal knowledge from AI-generated proposals.

## Source of Truth

Markdown files are the source of truth.

The formal knowledge base must remain readable and editable without DiamondDust.

## Rebuildable Data

The following are rebuildable caches:

- SQLite metadata index
- SQLite FTS index
- vector index
- relation index
- compile cache
- model run cache

If a cache is deleted, the system should be able to rebuild it from Markdown files and run logs where possible.

## Formal Vault Directories

Formal knowledge files live under:

```text
knowledge-vault/
  00-inbox/
  10-sources/
  20-questions/
  30-evidence/
  40-concepts/
  50-synthesis/
  60-maps/
  70-publications/
  80-assets/
  90-archive/
```

## AI Working Directories

AI-generated proposals, intermediate outputs, and reports live under:

```text
knowledge-vault/
  _ai_suggestions/
  _ai_reports/
  _ai_runs/
  _registry/
```

Rules:

- AI may write suggestions, drafts, and reports to AI working directories.
- AI must not directly overwrite formal knowledge files.
- Formal writes require a validated KnowledgePatch and user acceptance.

## Formal Vault Apply Preflight

Before any future formal apply behavior writes a `KnowledgePatch` into formal vault directories, the patch must pass a read-only conflict preflight.

The current preflight checks:

- `create_note` target paths do not already exist in the formal vault.
- proposed unit IDs do not already exist in formal note frontmatter.
- one patch does not contain duplicate `create_note` target paths.
- one patch does not contain duplicate created unit IDs.
- AI working directories are ignored for formal path and ID conflict detection.

Rules:

- The preflight is read-only.
- The preflight is not user acceptance.
- A passing preflight is not permission to write formal files.
- Formal apply/revert behavior remains a separate reviewed milestone.
- Complex frontmatter parsing may require a richer parser if real vault fixtures need it.

## Formal Apply Dry-Run Plan

A formal apply dry-run plan may be generated only after a patch has passed conflict preflight.

The current dry-run plan records:

- patch ID
- vault root
- planned formal note target paths
- planned formal note content
- planned content hashes
- rollback steps
- the conflict preflight report used by the plan

Rules:

- The plan must not write, modify, or delete formal vault files.
- The plan must not create missing vault directories.
- The plan is not user acceptance.
- The plan is not permission to write formal files.
- The plan may cover `create_note` files and relations embedded in those created files.
- Updating existing formal notes for relation-only changes remains future work.
- Formal apply/revert execution remains a separate reviewed milestone.

## AI Working Artifact Schema Versioning

Persisted AI working artifacts must include:

```text
artifact_schema_version: 0.1.0
```

Rules:

- Artifact schema versioning is separate from formal note `schema_version`.
- The initial AI working artifact schema version is `0.1.0`.
- JSON artifacts should store `artifact_schema_version` as a top-level field.
- Markdown artifacts should expose `artifact_schema_version` in frontmatter or visible report metadata.
- Artifact readers should tolerate older artifacts without this field until migration/import behavior is introduced.
- Changing persisted artifact shapes for CLI/UI consumers requires a migration note or compatibility strategy.

## Minimum Frontmatter

Every formal knowledge note must include:

```yaml
id:
type:
status:
title:
domain:
topics:
source_refs:
relations:
confidence:
created_at:
updated_at:
schema_version:
```

## Recommended Frontmatter

```yaml
id: unit_20260428_rag_prompt_stuffing_ab12cd
type: concept
status: seedling
title: RAG is not prompt stuffing
domain: AI
topics:
  - RAG
  - retrieval
source_refs:
  - source_id: raw_essay_20260428_rag_thinking
    source_path: 00-inbox/2026-04-28-rag-thinking.md
    source_span: paragraphs 3-4
    origin: mixed
relations:
  - source_id: unit_20260428_rag_prompt_stuffing_ab12cd
    relation_type: depends_on
    target_id: unit_20260428_retrieval_quality_cd34ef
    confidence: high
    reason: The concept depends on the idea that retrieval quality affects RAG output.
confidence: medium
created_at: 2026-04-28T00:00:00Z
updated_at: 2026-04-28T00:00:00Z
schema_version: 0.1.0
```

## KnowledgeUnit Required Fields

- `id`
- `type`
- `title`
- `content`
- `status`
- `source_refs`
- `relations`
- `confidence`
- `created_at`
- `updated_at`
- `schema_version`

## Allowed Unit Types

- `raw_essay`
- `question`
- `evidence`
- `concept`
- `claim`
- `synthesis`
- `map`
- `article`

## Allowed Status Values

- `seedling`
- `budding`
- `evergreen`
- `outdated`
- `superseded`

## Allowed Confidence Values

- `low`
- `medium`
- `high`

## SourceRef Schema

Minimum fields:

```yaml
source_id:
source_path:
source_span:
origin:
```

Allowed `origin` values:

- `user_text`
- `ai_inference`
- `mixed`

Optional fields:

```yaml
line_start:
line_end:
block_id:
quote:
content_hash:
is_approximate:
```

Rules:

- AI must not invent source references.
- If exact span is unavailable, set `is_approximate: true`.
- Derived units should preserve a path back to original raw input.

## Relation Schema

Minimum fields:

```yaml
source_id:
relation_type:
target_id:
confidence:
reason:
```

Allowed relation types:

- `related`
- `depends_on`
- `supports`
- `challenges`
- `example_of`
- `part_of`
- `contrasts_with`
- `supersedes`

Rules:

- Formal relations must use allowed relation types.
- Candidate relations may be stored in suggestions before review.
- Relations should include a reason whenever generated by AI.

## ID Rule

IDs must be stable after creation.

Recommended format:

```text
unit_<yyyymmdd>_<slug>_<short_hash>
```

Examples:

```text
unit_20260428_rag_prompt_stuffing_ab12cd
patch_20260428_extract_rag_essay_ef56gh
run_20260428_extract_units_ij78kl
```

Rules:

- Do not derive identity only from title.
- Title changes must not change IDs.
- IDs must be unique within the vault.
- Short hashes should be based on stable input content or generated UUID-like values.

## File Path Rule

Formal files should be placed according to unit type:

```text
raw_essay   -> 00-inbox/
question    -> 20-questions/
evidence    -> 30-evidence/
concept     -> 40-concepts/
claim       -> 50-synthesis/claims/
synthesis   -> 50-synthesis/
map         -> 60-maps/
article     -> 70-publications/
```

AI outputs should be placed under:

```text
_ai_suggestions/
_ai_reports/
_ai_runs/
```

## Candidate Markdown Export

Candidate Markdown notes rendered from a `KnowledgePatch` are AI working artifacts, not formal vault writes.

They should be exported under:

```text
_ai_suggestions/candidate-notes/<patch_id>/
```

Rules:

- Candidate notes may mirror intended formal target paths inside the candidate export directory.
- Candidate exports must preserve source references where available.
- Candidate exports must include `artifact_schema_version`.
- Candidate exports must include patch metadata and mark `formal_write: false`.
- Candidate manifests must state that candidate notes are previews under `_ai_suggestions/`, not formal vault notes or accepted knowledge.
- Candidate manifests must state that raw KnowledgePatch JSON is the source of truth for patch operations.
- Local trial candidate manifests may include a fixture SourceRef scope note when source references are fixture-level and do not validate real parser source-span accuracy.
- Candidate exports must not write files to formal vault directories.
- Formal writes still require a validated patch and explicit user acceptance.

## Review Report Export

Patch review reports are AI working artifacts, not acceptance records and not formal vault writes.

They should be exported under:

```text
_ai_reports/patch-reviews/<patch_id>.md
```

Rules:

- Review reports must include patch diff summaries, risks, rollback steps, and review boundaries.
- Review reports should link candidate Markdown notes when candidate notes exist.
- Review reports must include `artifact_type: patch_review_report` and `artifact_schema_version`.
- Review reports must mark `formal_write: false`.
- Review reports must mark `patch_acceptance: false` and `decision_status: pending` until a separate patch decision artifact exists.
- Review reports should include suggested review order, preview-level rollback notes, and a review decision prompt that does not record formal acceptance.
- Review reports must not mark patches as accepted or rejected.
- Local trial review reports may include `trial_id` and `review_scope: provider_free_fixture` plus fixture-specific risks for real LLM quality and parser source-span accuracy.
- Formal writes still require a validated patch and explicit user acceptance.

## Review Package Persistence

A review package groups the artifacts needed for human patch review.

The package may write:

- raw patch JSON under `_ai_suggestions/patches/<patch_id>.json`
- candidate Markdown notes under `_ai_suggestions/candidate-notes/<patch_id>/`
- patch review report under `_ai_reports/patch-reviews/<patch_id>.md`

Rules:

- Review package persistence must validate patch safety before writing artifacts.
- Review package persistence must write only to AI working directories.
- Review package artifacts must include `artifact_schema_version`.
- Review package persistence must mark `formal_write_allowed: false`.
- Review package persistence must not record accept/reject decisions.
- Formal writes still require explicit user acceptance and a separate storage apply step.

## Blog Draft Package Persistence

Blog draft packages are AI working artifacts, not publication records and not formal vault writes.

The package may write:

- blog draft Markdown under `_ai_suggestions/blog-drafts/<draft_id>/draft.md`
- blog quality report under `_ai_reports/blog-quality/<draft_id>.md`

Rules:

- Blog draft package persistence must write only to AI working directories.
- Blog draft artifacts must preserve source unit IDs and unsupported claim IDs.
- Blog quality reports must preserve validation status, risks, unsupported claims, evidence coverage, and suggested actions.
- Blog draft package artifacts must include `artifact_schema_version`.
- Blog draft artifacts must mark `formal_write: false`, `publication_ready: false`, and `requires_user_review: true`.
- Local trial blog drafts may include `draft_scope` and `real_ai_generation_validated` markers to prevent provider-free fixture drafts from being mistaken for real AI generation quality validation.
- Blog draft Claim Inventory may include supporting concepts as well as claims, but entries must expose a role so supporting context is not mistaken for an asserted claim.
- Blog draft persistence must not write files to `70-publications/`.
- Publishing still requires separate user approval and a future publication workflow.

## Local Trial Feedback Reports

Local trial feedback reports are AI working/report artifacts, not acceptance records and not formal vault writes.

They should be exported under:

```text
_ai_reports/local-trials/<trial_id>.md
```

Rules:

- Local trial feedback reports must include `artifact_schema_version`.
- Local trial feedback reports must mark `formal_write: false` and `provider_called: false`.
- Local trial feedback reports should summarize `trial_pipeline_status`, `product_owner_verdict`, artifact reading order, errors, unsupported claims, feedback prompts, and feedback capture fields.
- Local trial feedback reports must keep pipeline success separate from product-owner acceptance.
- Local trial feedback reports may be written for both passed and failed local trials when the vault report path is writable.
- Local trial feedback reports must not mark a patch as user-accepted and must not write files to formal vault directories.
- Feedback capture fields are product feedback only, not patch acceptance, formal write approval, or publication approval.
- Formal writes still require explicit user acceptance and a separate storage apply step.

## Local Trial Outcome JSON

Local trial outcome JSON files are machine-readable AI report artifacts for the same trial represented by the Markdown feedback report.

They should be exported under:

```text
_ai_reports/local-trials/<trial_id>.json
```

Rules:

- Local trial outcome JSON must include `artifact_type: local_trial_outcome` and `artifact_schema_version`.
- Local trial outcome JSON must use `trial_pipeline_passed`, `trial_pipeline_status`, `product_owner_verdict`, and `pipeline_summary` instead of ambiguous top-level `passed`, `status`, or `summary`.
- Local trial outcome JSON must keep `product_owner_verdict: pending` until product-owner feedback is explicitly captured.
- Local trial outcome JSON must include no-provider and no-formal-write boundary fields.
- Local trial outcome JSON should include `stage_label`, `stage_scope`, `not_validated`, and `quality_scope` to prevent fixture-driven runs from being mistaken for real LLM quality validation, formal apply validation, user acceptance, publication approval, or full MVP completion.
- Local trial outcome JSON must not record patch acceptance, formal vault apply, provider calls, or publication approval.

## Schema Versioning

Every persisted formal note must include:

```yaml
schema_version:
```

Rules:

- Public schema changes must update the schema version.
- Breaking schema changes require a migration note.
- Migration logic must be tested before applying to existing notes.

## Migration Rule

Any breaking schema change must include:

- migration reason
- old schema example
- new schema example
- migration strategy
- rollback strategy
- tests

## Patch Persistence

KnowledgePatch files should be persisted as JSON or YAML under:

```text
_ai_suggestions/patches/
```

Patch files must include:

- `patch_id`
- `source_input_ids`
- `operations`
- `validation_status`
- `risks`
- `requires_user_review`

## AI Run Persistence

AI run records should be persisted under:

```text
_ai_runs/
```

Each run must include:

- `artifact_type`
- `artifact_schema_version`
- `run_id`
- `task`
- `provider`
- `model`
- `prompt_version`
- `schema_version`
- `input_hash`
- `output_hash`
- `validation_status`
- `created_at`

Optional:

- `cost`
- `latency`
- `knowledge_base_snapshot_hash`
- `cache_key`
- `trial_id`
- `stage_label`
- `run_scope`
- `real_provider_call`
- `fixture_driven`
- `prompt_used`
- `metrics_scope`
- `source_input_id`
- `output_artifacts`
- `not_validated`

Rules:

- AI run artifacts may record both passed and failed validation runs.
- AI run artifacts must not persist raw model output.
- AI run artifacts must stay under `_ai_runs/`.
- Provider-free local trial run artifacts should mark `run_scope: provider_free_fixture`, `real_provider_call: false`, `fixture_driven: true`, and `prompt_used: false` while preserving the task contract `prompt_version`.
- When provider metrics are not produced, local trial run artifacts should keep `cost` and `latency` unset and include `metrics_scope` explaining that cost and latency are not applicable.
- Local trial run artifacts should preserve `source_input_id`, point `output_artifacts` at the generated downstream trial report/outcome artifacts, and list run-specific `not_validated` limits such as real LLM extraction quality, real parser source-span accuracy, provider latency, and provider cost.
- Run log `output_artifacts` must point only to AI working artifacts, not formal vault paths.

## Formal Write Rule

Formal knowledge files may be changed only after:

1. AI or system generates a KnowledgePatch.
2. KnowledgePatch passes schema validation.
3. User reviews and accepts the patch.
4. Storage adapter applies the patch.
5. Git diff remains inspectable.

## Cache Rebuild Rule

The system must treat these as disposable:

- SQLite metadata index
- SQLite FTS index
- vector index
- relation index

The system must not treat these as disposable:

- user-authored raw essays
- formal Markdown knowledge notes
- accepted patches
- migration records

## Validation Rule

Before any formal write, validate:

- frontmatter schema
- unit type
- status
- source references
- relations
- path safety
- duplicate ID
- schema version

## Path Safety Rule

Storage code must reject:

- absolute paths outside the vault
- `..` traversal
- attempts to overwrite formal files without patch acceptance
- attempts to write provider logs into formal knowledge directories
