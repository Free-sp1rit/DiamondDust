# Execution Plan: Trial Client Secret Trim And DeepSeek Truncation Message

## Product Goal

Fix a Win11 alpha trial blocker where a locally saved DeepSeek API key with
leading or trailing whitespace is passed to the provider unchanged, causing
401 authentication failures despite a valid key.

## Current Understanding

The trial client can save and read a package-local
`.diamonddust-trial/secrets/provider-secrets.env` file. The current parser
strips shell syntax but preserves whitespace inside quoted values. A user can
therefore persist `DIAMONDDUST_DEEPSEEK_API_KEY='  sk-...'`, and the backend
will pass the whitespace-prefixed key into the provider subprocess.

DeepSeek responses can also fail as malformed JSON when the provider output is
truncated. The adapter should report that condition clearly when
`finish_reason == "length"`.

## Assumptions

- API keys are opaque single-line secrets and should be normalized by trimming
  surrounding whitespace before persistence and before provider env injection.
- Trimming only surrounding whitespace is safe; interior characters are
  preserved.
- No real provider call is required for this fix.

## Non-goals

- Do not read or commit a real API key.
- Do not make a provider call.
- Do not persist provider raw request or response bodies.
- Do not change provider retry behavior.
- Do not bundle secrets or generated trial artifacts.

## Proposed Technical Approach

Normalize trial-client API key values at all boundaries:

- Trim the API key received from the client before saving.
- Trim parsed values returned by `load_provider_secret_env()` so old broken
  local files are repaired at read time.
- Trim values inside `save_provider_secret_env()` before validation and
  persistence.
- Trim the frontend API key input before POST.

For DeepSeek malformed responses, detect the first choice finish reason and
surface a specific fail-closed malformed-response message when it is `length`.

## Task Breakdown

- [x] Normalize key save/read paths in the trial client backend.
- [x] Normalize the browser API key input before submit.
- [x] Add regression tests for quoted whitespace keys and save/read trimming.
- [x] Add DeepSeek adapter test for `finish_reason == "length"`.
- [x] Update docs/context and run auth boundary review.
- [x] Run focused and full validation.
- [x] Commit and open PR.

## Likely Files Changed

- `src/diamonddust/interface/trial_client.py`
- `src/diamonddust/ai/adapters/deepseek.py`
- `tests/unit/test_trial_client.py`
- `tests/unit/test_deepseek_adapter_errors.py`
- `docs/context/project-state.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/<date>-trial-client-secret-trim.md`

## Validation Plan

- [x] focused trial client tests
- [x] focused DeepSeek adapter error tests
- [x] full unit test suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan
- [x] milestone review

## Review Gate Impact

This touches trial-client secret handling and provider error reporting, so a
milestone review is required before completion.

## Risks

- Over-normalizing secrets could alter unusual key values. The implementation
  only trims surrounding whitespace and leaves interior characters unchanged.
- A clearer truncation message does not fix long-note extraction by itself; it
  only makes the failure actionable.

## Escalation Needed

Does this require user approval?

- [x] no
- [ ] yes: describe

The user has provided the confirmed root cause and requested a project fix.

## Definition of Done

- Whitespace-padded quoted keys load as trimmed values.
- Whitespace-padded saved keys persist as trimmed values.
- The browser submits trimmed key values.
- DeepSeek length truncation maps to a clear malformed-response error.
- No secrets or trial artifacts are committed.
