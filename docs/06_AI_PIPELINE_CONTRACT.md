# AI Pipeline Contract

## Pipeline Steps

1. parse_input
2. extract_units
3. normalize_units
4. suggest_relations
5. generate_patch
6. validate_patch
7. generate_blog_outline
8. generate_blog_draft
9. review_blog_draft

## Rule

Every AI task must define:

- input schema
- output schema
- prompt version
- model policy
- validation rules
- failure behavior

## AI Output Boundary

LLM output may produce:

- candidates
- relations
- patches
- drafts
- review reports

LLM output must not:

- directly overwrite formal notes
- delete user content
- mark knowledge as evergreen without review
- publish content
- invent sources

## AI Run Log

Every AI run must record:

- run_id
- task
- provider
- model
- prompt_version
- schema_version
- input_hash
- output_hash
- cost if available
- latency if available
- validation_status

## Compile Cache

Cache key must include:

- input_hash
- knowledge_base_snapshot_hash
- schema_version
- prompt_version
- model_id
- model_params