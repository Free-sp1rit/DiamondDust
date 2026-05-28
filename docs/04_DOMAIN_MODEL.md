# Domain Model

## Purpose

This document defines the shared domain language of DiamondDust.

The domain model is the stable contract shared by code, prompts, tests, storage, review reports, and future adapters.

## KnowledgeUnit

A `KnowledgeUnit` is a structured semantic unit derived from raw input or existing knowledge.

Allowed unit types:

- `raw_essay`
- `question`
- `evidence`
- `concept`
- `claim`
- `synthesis`
- `map`
- `article`

### KnowledgeUnit Minimum Fields

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

### KnowledgeUnit Language Policy

DiamondDust's default user-facing knowledge-base language is Simplified Chinese.

Rules:

- Generated `title` and `content` should be written in Simplified Chinese.
- Code, commands, identifiers, product names, API names, and file paths should
  preserve their original spelling.
- `id`, `type`, `status`, `confidence`, `schema_version`, JSON keys, and enum
  values remain machine-facing English/ASCII contract fields.
- Source reference metadata and copied evidence are not translated.

### Unit Type Meanings

#### raw_essay

Original user-authored input.

Rules:

- Must be preserved.
- Must not be overwritten by AI.
- May be referenced by derived units.
- In current provider-backed extraction output, article-level background and
  whole-note summaries should be represented by `source_context`, not by a
  generated `raw_essay` unit candidate.
- `raw_essay` remains in the domain vocabulary for source identity and legacy
  compatibility, but it is not counted as an ordinary reusable knowledge unit
  in current extraction quality review.

## SourceContext

`SourceContext` is source/article-level context produced by the AI extraction
boundary. It is not a `KnowledgeUnit`, not a formal knowledge graph node, and
not a relation quality target.

Minimum fields:

- `source_input_id`
- `source_shape`
- `knowledge_domains`
- `background`
- `main_content`
- `scope`
- `source_refs`

Rules:

- `SourceContext` captures the input note's knowledge domain, background, main
  content range, and applicability scope.
- Generated user-facing `background`, `main_content`, `scope`, and
  `knowledge_domains` should be Simplified Chinese.
- `source_shape`, JSON field names, and other machine-facing values remain
  English/ASCII contract fields.
- `source_refs` preserve original source reference metadata and copied
  evidence; copied evidence is not translated.
- Ordinary `KnowledgeUnit` candidates must not repeat `SourceContext` as a
  whole-note summary, but each unit still needs enough local context to be
  independently reviewed, cited, retrieved, and reused.

#### question

An open question extracted from an essay or created by the user.

Examples:

- "How should RAG quality be evaluated?"
- "What makes a note worth turning into a concept?"

#### evidence

A concrete observation, example, source excerpt, experiment, quote, or project experience that can support a claim.

Rules:

- Must have source references.
- Should not contain broad unsupported conclusions.

#### concept

A reusable knowledge object explaining one concept, mechanism, distinction, or mental model.

Rules:

- Should be atomic enough to be reused.
- May depend on other concepts.

#### claim

A statement or judgment that can be supported, challenged, or marked unsupported.

Rules:

- A formal claim must have source references or be explicitly marked unsupported.
- Claims are often used to build blog drafts.

#### synthesis

A higher-level conclusion or pattern produced by combining multiple concepts, claims, or evidence units.

Rules:

- Should reference supporting units.
- Should mark confidence.

#### map

A domain or topic map that organizes questions, concepts, evidence, synthesis, articles, and gaps.

Rules:

- Maps are navigational and may change over time.
- AI may propose map patches but must not rewrite maps without review.

#### article

A blog draft, published article, or publication-oriented artifact.

Rules:

- Must declare article mode where possible.
- Should include claim inventory and unsupported claim report.

## SourceRef

A `SourceRef` records where a unit came from.

Minimum fields:

- `source_id`
- `source_path`
- `source_span`
- `origin`

Allowed `origin` values:

- `user_text`
- `ai_inference`
- `mixed`

Optional fields:

- `quote`
- `line_start`
- `line_end`
- `block_id`
- `content_hash`

Rules:

- AI must not invent source references.
- If exact span is unknown, `source_span` must be marked approximate.
- Derived units should preserve the original raw essay reference where possible.
- `quote` should preserve the original source language and wording when copied.

## Relation

A `Relation` connects two knowledge units.

Allowed relation types:

- `related`
- `depends_on`
- `supports`
- `challenges`
- `example_of`
- `part_of`
- `contrasts_with`
- `supersedes`

### Relation Minimum Fields

- `source_id`
- `relation_type`
- `target_id`
- `confidence`
- `reason`

### Relation Rules

- AI may suggest relations.
- Suggested relations must be reviewable.
- Suggested relation `reason` text should be written in Simplified Chinese for
  user review, while relation type enum values remain unchanged.
- Formal relations must use allowed relation types.
- If a proposed relation does not fit the allowed set, it must be recorded as a candidate, not a formal relation.

## KnowledgePatch

A `KnowledgePatch` is a reviewable proposal for changing the knowledge base.

Allowed operations:

- `create_note`
- `update_frontmatter`
- `add_relation`
- `create_blog_draft`
- `create_review_report`

Optional future operations:

- `update_note_body`
- `merge_notes`
- `mark_superseded`
- `update_map`

These optional operations require explicit review gate approval before implementation.

### KnowledgePatch Minimum Fields

- `patch_id`
- `created_at`
- `source_input_ids`
- `operations`
- `risks`
- `requires_user_review`

### Patch Rules

- A KnowledgePatch must validate before review.
- A rejected patch must not modify the formal vault.
- A patch may write to suggestion or draft directories before acceptance.
- Formal vault changes require explicit acceptance.

## BlogDraft

A `BlogDraft` is an article-oriented output generated from accepted or candidate knowledge units.

Minimum fields:

- `id`
- `title`
- `mode`
- `audience`
- `reader_problem`
- `outline`
- `claim_inventory`
- `content`
- `unsupported_claims`
- `source_unit_ids`
- `quality_report_id`

Allowed modes:

- `explanation`
- `tutorial`
- `how_to`
- `reference`
- `case_study`
- `essay`

Rules:

- Blog drafts may include unsupported claims only if they are explicitly marked.
- Blog drafts must not invent sources.
- Blog drafts are not automatically published.

## ReviewReport

A `ReviewReport` explains the quality, risk, and validation status of an extraction, patch, or blog draft.

Minimum fields:

- `id`
- `target_id`
- `target_type`
- `summary`
- `validation_status`
- `risks`
- `unsupported_claims`
- `suggested_actions`

## CompileRun

A `CompileRun` records one pipeline execution.

Minimum fields:

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

Optional fields:

- `cost`
- `latency`
- `knowledge_base_snapshot_hash`
- `cache_key`
- `user_feedback`

## TagRegistry

A `TagRegistry` manages controlled and candidate vocabulary.

Tag statuses:

- `candidate`
- `accepted`
- `deprecated`
- `merged`

Rules:

- Unit types and relation types are closed for MVP.
- Domain and topic tags may be proposed by AI.
- Candidate tags must not silently become accepted tags.
- Tag merges or deprecations must be reviewable.

## Status

Allowed status values:

- `seedling`
- `budding`
- `evergreen`
- `outdated`
- `superseded`

Rules:

- AI must not mark a unit as `evergreen` without review.
- AI may propose status changes.
- `superseded` units should reference replacement units where possible.

## Invariants

- A formal claim must have `source_refs` or be marked unsupported.
- A KnowledgePatch must validate before review.
- AI-generated content must be distinguishable from user-authored content.
- No formal knowledge file may be overwritten directly by an LLM response.
- Original raw essays must be preserved.
- Public schema changes require migration notes and tests.
