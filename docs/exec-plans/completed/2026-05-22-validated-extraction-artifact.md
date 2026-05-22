# Execution Plan: Validated Extraction Output Artifact

## Product Goal

Persist a typed, reviewable extraction output artifact after `extract_units`
validation succeeds, so future provider-backed runs have a durable AI working
artifact for lineage, replay, and review without retaining raw provider output.

## Current Understanding

Provider output currently becomes an in-memory `ExtractionProposal` after source
binding and typed validation. Run logs store hashes and metadata, then local
trial artifacts continue directly into patch, candidate-note, review, and blog
artifacts. This leaves no durable extraction-level artifact between a run log
and downstream patch artifacts.

The new artifact must remain an AI working artifact. It must not be raw provider
output, formal knowledge, patch acceptance, formal apply, or publication.

## Assumptions

- Persist only successful typed extraction proposals.
- Failed or malformed provider output remains represented by run log hash and
  validation errors, not by raw output persistence.
- The initial storage location is `_ai_suggestions/extractions/`.
- The local trial fixture may write one additional AI working artifact when
  extraction validation succeeds.

## Non-goals

- Do not persist raw provider request or response bodies.
- Do not call providers, read API keys, or make network requests.
- Do not generate or accept patches from this artifact directly.
- Do not formal apply, record patch acceptance, or publish.
- Do not add scoring, artifact groups, or path-audit artifacts.

## Proposed Technical Approach

Add a storage adapter module that renders and writes
`validated_extraction_output` JSON from an `ExtractionProposal`. Include run
metadata, source input id, output hash, validated unit and relation candidates,
and explicit safety boundaries.

Integrate the artifact into the local trial success path only after extraction
validation and source-id consistency checks pass. Update AI run log
`output_artifacts` to point to the extraction artifact, then downstream local
trial report/outcome artifacts. The storage adapter remains responsible for
file writes; application orchestration only coordinates the sequence.

## Task Breakdown

- [x] Add validated extraction artifact storage module.
- [x] Export storage API.
- [x] Integrate local trial success lineage with the new artifact.
- [x] Update local trial report artifact reading order purpose text.
- [x] Add storage and local trial tests.
- [x] Update durable context docs and milestone review.
- [x] Run validation.

## Likely Files Changed

- `src/diamonddust/storage/extraction_artifact.py`
- `src/diamonddust/storage/__init__.py`
- `src/diamonddust/application/local_trial.py`
- `src/diamonddust/storage/local_trial_report.py`
- `tests/unit/test_extraction_artifact_persistence.py`
- `tests/unit/test_local_trial.py`
- `docs/06_AI_PIPELINE_CONTRACT.md`
- `docs/context/project-state.md`
- `docs/context/decisions.md`
- `docs/context/open-questions.md`
- `docs/context/completed-milestones.md`
- `docs/reviews/milestone-reviews/2026-05-22-validated-extraction-artifact.md`

## Validation Plan

- [x] focused extraction artifact persistence tests
- [x] focused local trial tests
- [x] full unit test suite
- [x] compile check
- [x] diff check
- [x] local trial fixture smoke
- [x] architecture boundary scan

## Review Gate Impact

Post-Gate 7 AI working artifact and storage format milestone. This introduces a
new persisted AI working artifact shape, so milestone review is required.

## Risks

- The artifact could be mistaken for formal knowledge unless boundaries are
  explicit.
- The artifact could be mistaken for raw provider output unless the renderer
  stores only typed validated proposal data.
- Local trial artifact counts and reading order change by one successful
  extraction artifact.

## Escalation Needed

Does this require user approval?

- [x] no: this is provider-free AI working artifact persistence and does not
  change formal schema or live-provider behavior.
- [ ] yes

## Definition of Done

- Successful local trial extraction writes a validated extraction artifact under
  `_ai_suggestions/extractions/`.
- AI run logs can point to that artifact as a downstream output artifact.
- Failed extraction paths do not persist raw or invalid output artifacts.
- Tests confirm no formal vault write, no provider call, and no raw provider
  output persistence.
