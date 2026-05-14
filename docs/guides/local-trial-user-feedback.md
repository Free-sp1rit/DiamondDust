# Local Trial User Feedback

Use this guide when you want to try the current provider-free DiamondDust flow and record feedback from the generated artifacts.

The local trial path uses structured extraction JSON instead of an LLM provider. It writes AI working artifacts only and must not write formal vault notes, publish content, or treat feedback as patch acceptance.

## Run The Fixture Trial

After a local editable install:

```bash
python3 -m pip install -e .
```

```bash
diamonddust local-trial \
  --trial-id trial_fixture_ab12cd \
  --essay tests/fixtures/local_trial/trial-essay.md \
  --extraction-json tests/fixtures/local_trial/extraction.json \
  --root . \
  --vault-root knowledge-vault \
  --title "Reviewable Local Trial Artifacts" \
  --mode explanation \
  --audience "product owner" \
  --reader-problem "inspecting generated artifacts before formal writes"
```

Development fallback without installation:

```bash
PYTHONPATH=src python3 -m diamonddust local-trial --help
```

## Review Order

Start from:

```text
knowledge-vault/_ai_reports/local-trials/trial_fixture_ab12cd.md
```

Then follow the artifact reading order listed inside that report.

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

- whether the trial is usable, needs changes, or is blocked
- whether the report was opened first
- which artifacts were inspected
- extraction quality concerns
- review package clarity concerns
- blog draft usefulness concerns
- safety or boundary concerns
- the next change that would most improve trial readiness

The feedback capture section is product feedback only. It is not patch acceptance, formal write approval, or publication approval.

## Safety Checks

After running the fixture trial, these should remain true:

- no files are written to formal vault directories such as `40-concepts/`, `50-synthesis/`, or `70-publications/`
- the report says `formal_write: false`
- the report says `provider_called: false`
- the report says `patch_acceptance: false`
- the report says `formal_write_approval: false`

## Using Your Own Essay

For a custom essay, provide a matching structured extraction JSON file. See `docs/guides/local-trial-extraction-json.md` for the accepted shape.

Custom trials are still provider-free unless a future provider adapter is explicitly added and approved.
