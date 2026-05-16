# Milestone Review: Provider Request Builder

## Scope Reviewed

Provider-neutral `extract_units` request builder from ingested Markdown essays, including typed build spec, traceable payload fields, model-policy validation before returning a request, tests, AI pipeline documentation, and repo memory updates.

## Product Goal Alignment

Aligned. The change prepares DiamondDust for future real-provider extraction by creating a deterministic Markdown-to-provider-request handoff without enabling provider execution.

## Architecture Boundary Compliance

Compliant.

- The request builder lives in the application layer.
- Domain core does not import provider, storage, or application modules.
- Provider adapters remain envelope-only and side-effect free.
- Storage ingestion remains responsible for Markdown parsing and source hashes.
- No provider SDK, API key read, network call, formal vault mutation, patch acceptance, or publication behavior was introduced.

## Cohesion Assessment

Good. The builder owns only the request construction boundary and leaves provider execution, extraction validation, run-log persistence, and patch generation to existing modules.

## Coupling Assessment

Acceptable. The builder depends on `IngestedMarkdownEssay`, provider-neutral request/settings types, and model policy validation. It does not depend on concrete providers, SDKs, HTTP clients, or storage persistence.

## Data and Schema Safety

Pass with follow-up. The request payload preserves source identity, source path, content hashes, body line range, frontmatter, body text, and source reference mapping. It is not a persisted artifact schema.

## AI Output Boundary

Compliant. The builder produces provider input, not AI output. It does not generate candidates, patches, drafts, reports, or formal writes. Provider output still must pass typed extraction validation before becoming domain data.

## Tests and Evaluation

Validation run:

- 154 unit tests passed.
- `python3 -m compileall src tests` passed.
- `git diff --check` passed.
- Local trial fixture smoke passed.
- Domain architecture scan reported 0 violations.

## Dependency and Portability Impact

No dependency was added. The builder uses existing standard-library and project types.

## Risks

- Request payload field names may become a compatibility surface before prompt/config interfaces are designed.
- Payload includes essay body text; sending it to a real provider still requires explicit user approval.
- Future prompt rendering may require additional prompt-specific payload fields.

## Required Changes Before Continuing

None for the provider request builder.

Before real provider integration, user approval is still required for provider, model, SDK dependency, API key environment variable, network calls, cost limit, retry policy, raw output retention, fallback behavior, and sending user essay text to the provider.

## Optional Improvements

- Add prompt template rendering only after first-provider decisions and prompt review criteria are approved.
- Add a request payload compatibility note if payloads become persisted or user-facing.

## Escalation Requests

None for this milestone.

Real provider integration will still require escalation before SDK dependencies, API key reads, network calls, cost-bearing behavior, fallback behavior, raw provider output persistence, or sending user text to an external provider.

## Review Decision

- [x] pass
- [ ] pass with follow-up
- [ ] blocked
