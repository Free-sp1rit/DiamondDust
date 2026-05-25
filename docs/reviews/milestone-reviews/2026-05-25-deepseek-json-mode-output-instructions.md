# Milestone Review: DeepSeek JSON Mode Output Instructions

## Scope Reviewed

- `src/diamonddust/ai/adapters/deepseek.py`
- `src/diamonddust/cli.py`
- DeepSeek adapter mapping, safety, and CLI tests
- DeepSeek provider design/context docs
- Controlled DeepSeek fixture live-smoke result

## Product Goal Alignment

Pass. The change addresses the observed DeepSeek JSON mode failure where the
provider returned valid JSON with provider-chosen keys such as `units` or
`candidates` instead of DiamondDust's typed `unit_candidates` and
`relation_candidates` fields.

## Architecture Boundary Compliance

Pass. DeepSeek-specific JSON mode shaping remains inside
`src/diamonddust/ai/adapters/deepseek.py`. Domain schemas, application
orchestration, storage adapters, formal vault code, and artifact contracts do
not import DeepSeek or OpenAI SDK-specific types.

## Cohesion Assessment

Pass. The adapter now owns the provider-specific task of placing
provider-neutral output instructions into DeepSeek Chat Completions messages.
The provider-neutral prompt renderer still owns instructions and schema
identity, while the adapter owns DeepSeek JSON mode message shape.

## Coupling Assessment

Pass with follow-up. The adapter depends on the provider-neutral
`ProviderExecutionPayload` and `ProviderExecutionRequest`, which is the intended
boundary. The new helper does not require downstream validation or storage to
know about DeepSeek JSON mode.

## Data and Schema Safety

Pass. The implementation does not add schema aliases or accept provider-chosen
field names. Typed runtime validation remains fail-closed and authoritative
before provider output can become a validated extraction artifact.

## AI Output Boundary

Pass. The controlled live smoke persisted only hash/metadata run information
and the typed validated extraction artifact. Raw provider request and response
bodies were not persisted. No formal vault write, patch acceptance, or
publication occurred.

## Tests and Evaluation

- Focused DeepSeek adapter/CLI tests: 31 tests passed.
- Full unit suite: 262 tests passed.
- Compile check: passed.
- `git diff --check`: passed.
- Provider-free local trial fixture smoke: passed with 12 artifacts.
- Architecture scan: 0 violations.
- Controlled DeepSeek fixture live smoke: passed typed validation and wrote:
  - `_ai_suggestions/extractions/run_deepseek_live_smoke_codex_after_json_mode_20260525T145000Z.json`
  - `_ai_runs/run_deepseek_live_smoke_codex_after_json_mode_20260525T145000Z.json`

## Dependency and Portability Impact

No dependency was added or changed. The existing OpenAI SDK dependency remains
isolated to AI adapter modules for OpenAI and DeepSeek's OpenAI-compatible API
path.

## Risks

- Fixture validation does not prove product quality on real notes.
- The DeepSeek system message is larger because it now includes output
  instructions and a compact JSON example.
- `max_tokens=4096` improves output headroom but can increase per-call cost.

## Required Changes Before Continuing

- None for this hardening stage.

## Optional Improvements

- Add a product-owner-approved non-sensitive real-note evaluation.
- Add sanitized validation-shape diagnostics to run logs for failed provider
  validation without persisting raw provider output.
- Revisit `max_tokens` after observing real-note extraction length and cost.

## Escalation Requests

None.

## Review Decision

- [x] pass with follow-up
- [ ] pass
- [ ] blocked
