# Execution Plan: Knowledge Language Policy

## Product Goal

Ensure provider-generated knowledge content is suitable for a Chinese-language
knowledge base while preserving stable machine contracts and original evidence.

## Current Understanding

The product owner wants notes presented to the user in Chinese. DiamondDust also
needs stable JSON keys, enum values, candidate ids, artifact metadata, and source
references that should not be translated or localized. The intended rule is:
knowledge content in Chinese, evidence in original language, machine structure in
English/ASCII.

## Assumptions

- The current knowledge-base presentation language is Simplified Chinese.
- Provider-neutral prompt/schema guidance is the right layer for this policy.
- Domain enum values and artifact keys must remain unchanged.

## Non-goals

- Do not change domain enum values, JSON field names, artifact metadata keys, or
  candidate id rules.
- Do not translate source reference metadata or source quotes.
- Do not add provider-specific language logic.
- Do not generate patches, formal apply, or publish.

## Proposed Technical Approach

Add provider-neutral language policy guidance to `extract_units.v1` prompt
instructions and the machine-readable extraction output schema descriptions.
The prompt tells providers to write user-facing generated fields in Simplified
Chinese while preserving code, commands, identifiers, product names, paths, and
copied evidence in original form. Tests assert the policy is present and schema
rendering remains stable and parseable.

## Task Breakdown

- [x] Add knowledge language policy to prompt output instructions.
- [x] Add schema descriptions for user-facing fields and original-language
      source quotes.
- [x] Update tests for prompt and schema policy.
- [x] Update AI pipeline/domain docs and durable context.
- [x] Run validation and milestone review.

## Files Changed

- `src/diamonddust/ai/prompt.py`
- `src/diamonddust/ai/extraction_schema.py`
- `tests/unit/test_prompt_renderer.py`
- `tests/unit/test_extraction_output_schema.py`
- `docs/04_DOMAIN_MODEL.md`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-26-knowledge-language-policy.md`

## Validation Plan

- [x] focused prompt/schema tests
- [x] full unit test suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan
- [x] milestone review

## Validation Results

- `PYTHONPATH=src .venv/bin/python -m unittest tests.unit.test_prompt_renderer tests.unit.test_extraction_output_schema`: 12 tests passed.
- `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests`: 263 tests passed.
- `.venv/bin/python -m compileall src tests`: passed.
- `git diff --check`: passed.
- `PYTHONPATH=src .venv/bin/python -m diamonddust local-trial-fixture`: passed; `provider_called: false`, `formal_write_performed: false`.
- Architecture boundary scan: 0 critical violations.

## Review Gate Impact

This updates the provider-neutral AI output contract and prompt behavior, so a
milestone review was completed.

## Risks

- The language instruction may reduce provider compliance on very mixed-language
  notes.
- Generated Chinese content may still need human quality review.
- Existing validated extraction artifacts are not migrated.

## Escalation Needed

Does this require user approval?

- [x] no: the product owner explicitly requested implementing the strategy.
- [ ] yes

## Definition of Done

- Prompt and schema contract state the language policy.
- Machine fields remain English/ASCII and unchanged.
- Tests pass and docs record the policy boundary.
