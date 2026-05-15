# Local Trial User Feedback

Use this guide when you want to try the current provider-free DiamondDust flow and record feedback from the generated artifacts.

The local trial path uses structured extraction JSON instead of an LLM provider. It writes AI working artifacts only and must not write formal vault notes, publish content, or treat feedback as patch acceptance.

## Run The Fixture Trial

From the repository root, install locally:

```bash
python3 -m pip install -e .
```

Then run from any working directory:

```bash
diamonddust local-trial-fixture
```

The shortcut uses packaged provider-free fixture assets mirrored from the repository's local trial fixture pair.

Development fallback from the repository root without installation:

```bash
PYTHONPATH=src python3 -m diamonddust local-trial-fixture
```

## Review Order

Start from:

```text
knowledge-vault/_ai_reports/local-trials/trial_fixture_ab12cd.md
```

Then follow the artifact reading order listed inside that report. Each listed artifact includes a one-line purpose note.

The same run also writes a machine-readable outcome summary:

```text
knowledge-vault/_ai_reports/local-trials/trial_fixture_ab12cd.json
```

Use the Markdown report for human review and the JSON outcome for lightweight comparison, aggregation, or follow-up issue creation.

The Markdown report and JSON outcome should agree on `trial_pipeline_status` and `product_owner_verdict`. The JSON outcome also records stage scope and quality-scope limits so automation does not treat a fixture-driven provider-free run as real LLM quality validation.

The AI run log should also make the same provider-free fixture scope visible. For the fixture shortcut, `_ai_runs/run_trial_fixture_ab12cd_local_trial.json` should include `run_scope: "provider_free_fixture"`, `real_provider_call: false`, `fixture_driven: true`, `prompt_used: false`, non-applicable cost/latency `metrics_scope`, and lineage pointers back to the source input and downstream trial report/outcome.

Expected artifact families:

- `_ai_reports/local-trials/`
- `_ai_runs/`
- `_ai_suggestions/patches/`
- `_ai_suggestions/candidate-notes/`
- `_ai_reports/patch-reviews/`
- `_ai_suggestions/blog-drafts/`
- `_ai_reports/blog-quality/`

## Feedback Capture

Use the `Feedback Capture` section in the local trial report to record:

- your product-owner verdict as structured free text
- whether the report was opened first, if relevant
- which artifacts were inspected
- extraction quality concerns
- review package clarity concerns
- blog draft usefulness concerns
- safety or boundary concerns
- the next change that would most improve trial readiness

The feedback capture section is product feedback only. It is not patch acceptance, formal write approval, or publication approval.

Do not add numeric scores until the trial rubric has been calibrated against real product-owner feedback.

## Safety Checks

After running the fixture trial, these should remain true:

- no files are written to formal vault directories such as `40-concepts/`, `50-synthesis/`, or `70-publications/`
- the report says `trial_pipeline_status: "passed"` or `trial_pipeline_status: "failed"`
- the report says `product_owner_verdict: "pending"` before product-owner review
- the report says `formal_write: false`
- the report says `provider_called: false`
- the JSON outcome says `trial_pipeline_status: "passed"` or `trial_pipeline_status: "failed"`
- the JSON outcome says `product_owner_verdict: "pending"` before product-owner review
- the JSON outcome lists `real_llm_extraction_quality`, `formal_vault_apply`, `user_acceptance`, and `blog_publication_quality` under `not_validated`
- the AI run log says `run_scope: "provider_free_fixture"`
- the AI run log says `real_provider_call: false`, `fixture_driven: true`, and `prompt_used: false`
- the AI run log keeps `cost` and `latency` unset and explains metric non-applicability under `metrics_scope`
- the candidate notes manifest states that candidate notes are previews, raw KnowledgePatch JSON is the operation source of truth, and fixture SourceRefs do not validate real parser source-span accuracy
- the blog draft frontmatter says `requires_user_review: true`, `draft_scope: "provider_free_fixture"`, and `real_ai_generation_validated: false`
- the blog draft Claim Inventory includes supporting concepts with an explicit supporting concept role
- the report says `patch_acceptance: false`
- the report says `formal_write_approval: false`
- the JSON outcome has `boundaries.formal_write_performed` set to `false`
- the JSON outcome has `boundaries.provider_called` set to `false`

## Using Your Own Essay

For a custom essay, use `diamonddust local-trial` and provide a matching structured extraction JSON file. See `docs/guides/local-trial-extraction-json.md` for the accepted shape.

Custom trials are still provider-free unless a future provider adapter is explicitly added and approved.
