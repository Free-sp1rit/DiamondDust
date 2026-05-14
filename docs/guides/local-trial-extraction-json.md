# Local Trial Extraction JSON

This guide describes the structured extraction JSON file accepted by:

```bash
diamonddust local-trial --extraction-json <path>
```

Development fallback without installation:

```bash
PYTHONPATH=src python3 -m diamonddust local-trial --extraction-json <path>
```

The local trial path uses this JSON in place of a provider call. It validates the JSON, writes AI working artifacts, and keeps formal vault files untouched.

## Top-Level Shape

The JSON document must be an object with:

- `source_input_id`: the ingested essay source ID.
- `unit_candidates`: a list of proposed `KnowledgeUnit` objects.
- `relation_candidates`: a list of proposed `Relation` objects.

`source_input_id` must match the ID produced when the Markdown essay is ingested. For the checked-in fixture, the essay frontmatter provides this value:

```yaml
id: raw_essay_local_trial_fixture_ab12cd
```

## Unit Candidate Shape

Each `unit_candidates` item must include:

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

Allowed `type` values:

- `raw_essay`
- `question`
- `evidence`
- `concept`
- `claim`
- `synthesis`
- `map`
- `article`

Allowed `status` values:

- `seedling`
- `budding`
- `evergreen`
- `outdated`
- `superseded`

Allowed `confidence` values:

- `low`
- `medium`
- `high`

`source_refs` must not be empty for local trial unit candidates. At least one source reference on each unit must have `source_id` equal to the top-level `source_input_id`.

## Source Reference Shape

Each `source_refs` item must include:

- `source_id`
- `source_path`
- `source_span`
- `origin`

Allowed `origin` values:

- `user_text`
- `ai_inference`
- `mixed`

Optional fields:

- `line_start`
- `line_end`
- `block_id`
- `quote`
- `content_hash`
- `is_approximate`

Use `is_approximate: true` when the span is useful for review but not exact.

## Relation Candidate Shape

Each `relation_candidates` item must include:

- `source_id`
- `relation_type`
- `target_id`
- `confidence`
- `reason`

Allowed `relation_type` values:

- `related`
- `depends_on`
- `supports`
- `challenges`
- `example_of`
- `part_of`
- `contrasts_with`
- `supersedes`

The current validator checks relation field shape and allowed values. It does not yet prove that relation endpoints exist in the same JSON document, so keep relation IDs reviewable by hand.

## Minimal Example

The example below is intentionally small. It is validated by the test suite so the guide stays aligned with the current code.

<!-- extraction-json-example:start -->
```json
{
  "source_input_id": "raw_essay_doc_example_ab12cd",
  "unit_candidates": [
    {
      "id": "unit_doc_example_review_boundary_ab12cd",
      "type": "claim",
      "title": "Reviewable artifacts should precede formal writes",
      "content": "A local trial should produce reviewable artifacts before any formal vault write is possible.",
      "status": "seedling",
      "source_refs": [
        {
          "source_id": "raw_essay_doc_example_ab12cd",
          "source_path": "tests/fixtures/local_trial/trial-essay.md",
          "source_span": "lines 8-8",
          "origin": "user_text",
          "line_start": 8,
          "line_end": 8,
          "content_hash": "sha256:doc-example-line-8",
          "is_approximate": true
        }
      ],
      "relations": [],
      "confidence": "high",
      "created_at": "2026-05-12T00:00:00Z",
      "updated_at": "2026-05-12T00:00:00Z",
      "schema_version": "0.1.0"
    },
    {
      "id": "unit_doc_example_visible_outputs_cd34ef",
      "type": "concept",
      "title": "Visible local trial outputs",
      "content": "Visible run logs, patches, reports, and drafts make the local trial easier to inspect.",
      "status": "seedling",
      "source_refs": [
        {
          "source_id": "raw_essay_doc_example_ab12cd",
          "source_path": "tests/fixtures/local_trial/trial-essay.md",
          "source_span": "lines 6-10",
          "origin": "user_text",
          "line_start": 6,
          "line_end": 10,
          "content_hash": "sha256:doc-example-lines-6-10",
          "is_approximate": true
        }
      ],
      "relations": [],
      "confidence": "medium",
      "created_at": "2026-05-12T00:00:00Z",
      "updated_at": "2026-05-12T00:00:00Z",
      "schema_version": "0.1.0"
    }
  ],
  "relation_candidates": [
    {
      "source_id": "unit_doc_example_review_boundary_ab12cd",
      "relation_type": "supports",
      "target_id": "unit_doc_example_visible_outputs_cd34ef",
      "confidence": "medium",
      "reason": "Reviewable artifacts are one visible output that makes local trial inspection safer."
    }
  ]
}
```
<!-- extraction-json-example:end -->

## Common Validation Failures

- The JSON root is not an object.
- `source_input_id` is missing or blank.
- `unit_candidates` or `relation_candidates` is not a list.
- A unit is missing a required field.
- A unit source reference does not point back to `source_input_id`.
- An enum value is outside the allowed set.
- A claim has no `source_refs` and is not marked `unsupported: true`.
- A relation is missing its `reason`.

## Boundaries

This JSON file is input to a local trial, not permission to write formal knowledge files. A successful local trial may write `_ai_runs/`, `_ai_suggestions/`, and `_ai_reports/` artifacts. It must not write formal vault directories, publish content, or call a provider.

Use `tests/fixtures/local_trial/extraction.json` as the runnable reference fixture.
