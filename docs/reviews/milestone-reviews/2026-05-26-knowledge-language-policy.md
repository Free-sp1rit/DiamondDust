# Milestone Review: Knowledge Language Policy

## Scope Reviewed

- `src/diamonddust/ai/prompt.py`
- `src/diamonddust/ai/extraction_schema.py`
- Prompt/schema tests
- Domain and AI pipeline documentation
- Durable context updates

## Product Goal Alignment

Pass. The change implements the product-owner strategy that knowledge content
shown to the user should be Chinese, while evidence and machine contracts remain
stable and unlocalized.

## Architecture Boundary Compliance

Pass. The policy lives in provider-neutral prompt/schema contracts and docs. No
provider-specific adapter, domain enum, storage adapter, or formal vault code was
changed to encode language-specific behavior.

## Cohesion Assessment

Pass. User-facing generated language guidance is colocated with the extraction
prompt and schema descriptions that providers consume. The domain model records
the product rule without changing runtime data structures.

## Coupling Assessment

Pass. The implementation does not couple language policy to DeepSeek, OpenAI, or
any provider SDK. Machine keys, enum values, ids, schema versions, and artifact
metadata stay unchanged.

## Data and Schema Safety

Pass. The JSON Schema remains parseable and keeps the same required fields and
enum values. New descriptions clarify generated text language without changing
typed validation semantics.

## AI Output Boundary

Pass. The prompt instructs providers to use Simplified Chinese for generated
`title`, `content`, and relation `reason`, while preserving source refs and
quoted evidence. No provider call, patch generation, formal apply, or
publication was performed.

## Tests and Evaluation

- Focused prompt/schema tests: 12 tests passed.
- Full unit suite: 263 tests passed.
- Compile check: passed.
- `git diff --check`: passed.
- Local trial fixture smoke: passed; `provider_called: false`,
  `formal_write_performed: false`.
- Architecture boundary scan: 0 critical violations.

## Dependency and Portability Impact

No dependency was added or changed.

## Risks

- Mixed-language notes may still need manual wording review.
- Existing generated artifacts are not migrated.
- Providers may imperfectly follow language instructions, so real-note quality
  evaluation remains necessary.

## Required Changes Before Continuing

- None.

## Optional Improvements

- Add an explicit `content_language` field only if future review shows the
  language policy needs machine-readable tracking.
- Add evaluation checks for Chinese title/content/reason quality after more
  real-note trials.

## Escalation Requests

None.

## Review Decision

- [ ] pass
- [x] pass with follow-up
- [ ] blocked
