# Execution Plan: Trial Client Product Feedback

## Product Goal

Make the small-user trial client practical for repeated real-note trials by
adding DeepSeek model presets, local API key setup, historical artifact
management, and clearer unit review UI.

## Current Understanding

The first trial-client pass can run DeepSeek extraction and show validated
artifacts, but product-owner testing found four usability gaps:

- model entry should be a preset selection rather than a free text field
- trial users should be able to write the DeepSeek API key into the local
  secrets file from the client
- previous artifacts should be loaded and managed without regenerating output
- unit cards need stronger visual separation and source refs should be
  expandable evidence, not primary review text

DeepSeek's current API docs list `deepseek-v4-pro` and `deepseek-v4-flash` as
the V4 API model names and note that `deepseek-chat`/`deepseek-reasoner` are
legacy aliases pending deprecation.

## Assumptions

- This remains a local-only client bound to `127.0.0.1` by default.
- API key setup may persist the key to the configured local secrets file, but
  the key value must not be returned by status APIs, feedback artifacts, or UI
  history.
- Deletion should be limited to trial-client generated run IDs and AI working
  artifacts, never formal vault files.
- Artifact history can group by note path from source refs and fall back to
  input hashes when source refs are unavailable.

## Non-goals

- Do not build a full note editor.
- Do not change domain schemas or extraction artifact schema.
- Do not enable patch acceptance, formal apply, or publication.
- Do not persist raw provider request or response bodies.
- Do not support arbitrary provider/model entry in the trial UI.

## Proposed Technical Approach

Keep the work inside the interface layer and docs. Add explicit model preset
metadata to the trial client service, validate requested models against those
presets, and make `deepseek-v4-flash` the default trial model.

Add a local-only POST endpoint that writes `DIAMONDDUST_DEEPSEEK_API_KEY` into
the configured secrets env file using restrictive permissions, preserving other
env file lines and never returning the key value.

Add artifact history APIs that scan validated extraction artifacts, group
versions by source note, load a selected run without invoking a provider, and
delete only trial-client generated run artifacts from AI working directories.

Update the embedded UI so notes show their saved versions, users can load or
delete versions, unit cards are visually distinct, and source refs are collapsed
as expandable evidence.

## Task Breakdown

- [x] Add DeepSeek model preset constants and model validation.
- [x] Add local secrets-file write endpoint and tests.
- [x] Add artifact version listing, loading, and safe deletion.
- [x] Update UI for preset model selection, local key setup, version management,
      and clearer unit cards.
- [x] Update docs/context and milestone review.
- [x] Run validation and update the existing trial-client PR.

## Likely Files Changed

- `src/diamonddust/interface/trial_client.py`
- `tests/unit/test_trial_client.py`
- `docs/guides/trial-client.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-27-trial-client.md`
- `docs/exec-plans/completed/2026-05-28-trial-client-product-feedback.md`

## Validation Plan

- [x] focused trial client tests
- [x] focused CLI entrypoint tests
- [x] full unit test suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan
- [x] manual client status smoke

## Validation Results

- `PYTHONPATH=src .venv/bin/python -m unittest tests.unit.test_trial_client tests.unit.test_cli_entrypoints`: 36 tests passed.
- `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests`: 275 tests passed.
- `.venv/bin/python -m compileall src tests`: passed.
- `git diff --check`: passed.
- `PYTHONPATH=src .venv/bin/python -m diamonddust local-trial-fixture`: passed with `provider_called: false` and `formal_write_performed: false`.
- Architecture boundary scan: 0 critical violations.
- Manual client status smoke: `/api/status` served from the restarted local client.

## Review Gate Impact

This touches an interface adapter and local secret handling, so it extends the
trial-client milestone review.

## Risks

- API key writing could accidentally expose secret values if status or errors
  echo request data.
- Artifact deletion could remove non-trial data if run ID scope is too broad.
- Historical grouping may be incomplete for older artifacts that lack source
  refs and cannot be matched by input hash.

## Escalation Needed

Does this require user approval?

- [x] no: the product owner explicitly requested this usability and local key
      setup stage.
- [ ] yes

## Definition of Done

- Trial users can choose only DeepSeek-V4-Pro or DeepSeek-V4-Flash from the UI.
- Trial users can save the DeepSeek API key into the local secrets file without
  the key being returned or logged by the client.
- Existing artifact versions can be loaded without a model call.
- Trial-client generated versions can be deleted from AI working directories.
- Unit review cards are visually distinct and source refs are expandable.
