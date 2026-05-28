# Open Questions

Record unresolved product, architecture, schema, dependency, or governance questions here.

Last updated: 2026-05-28

## Tooling and Repository Shape

### 2026-05-10 — Should repo-local skills be wired into Codex discovery?

- Context: Minimal governance skills were created under `skills/` because `.codex/` and `.agents/` are read-only in this workspace.
- Needed decision: Confirm whether `skills/` is the desired durable repo-local path or whether a later install/discovery step should mirror them into the active Codex skill directory.
- Impact: Affects whether future sessions can trigger these skills automatically or must load them by path.

### 2026-05-10 — When should Markdown/frontmatter parsing move beyond the minimal subset?

- Context: Gate 3 was implemented with a standard-library parser for flat frontmatter key/value pairs and string lists.
- Needed decision: Reconsider a Markdown or YAML dependency only after fixture evidence shows the minimal parser is insufficient.
- Impact: Affects parsing fidelity, dependency posture, portability, and future migration notes.

## Fixtures

### 2026-05-10 — Which essays should become the MVP golden fixtures?

- Context: Gate 7 now has five deterministic Markdown fixtures for readiness tests, but they are not yet product-owner-approved golden essays.
- Needed decision: Identify or create real or semi-real fixture essays before golden quality evaluation is finalized.
- Impact: Affects extraction quality evaluation, regression coverage, and release confidence.

### 2026-05-11 — When should candidate Markdown export use a richer serializer?

- Context: Candidate Markdown export now uses a minimal standard-library YAML-like renderer.
- Needed decision: Reconsider a serializer dependency only if review fixtures need richer frontmatter or round-trip parsing.
- Impact: Affects candidate note fidelity, dependency posture, and future migration surface.

### 2026-05-14 — Which local trial feedback fields should become release criteria?

- Context: Local trial runs now write `_ai_reports/local-trials/<trial_id>.md` with prompts, `trial_pipeline_status`, pending `product_owner_verdict`, and structured free-text feedback capture, plus `_ai_reports/local-trials/<trial_id>.json` with matching pipeline/verdict semantics and explicit quality-scope limits. The rubric and outcome shape have not yet been validated by repeated real product-owner trials.
- Needed decision: After the first controlled trial, decide which feedback fields should become durable acceptance criteria or test fixtures.
- Impact: Affects whether the next phase should prioritize golden essays, report quality, formal apply safety, or provider-backed extraction.

### 2026-05-15 — When should local trial feedback become a typed artifact?

- Context: Product-owner feedback is intentionally structured free text for now, and numeric scoring is deferred until the rubric is calibrated.
- Needed decision: Decide whether to add a typed feedback artifact only after enough real trial feedback exists to stabilize field names and allowed values.
- Impact: Affects future aggregation, release criteria, and whether feedback capture should stay in Markdown or become a separate JSON artifact.

## AI Pipeline

### 2026-05-15 — Which extraction output artifact fields should grow after v0?

- Context: On 2026-05-22, DiamondDust introduced `validated_extraction_output` artifacts under `_ai_suggestions/extractions/` for successful typed extraction proposals. Local trial run logs now point to that artifact when one exists, then downstream trial report/outcome artifacts. Run logs and extraction artifacts intentionally do not persist raw model/provider output.
- Needed decision: Decide later whether real provider runs need additional extraction artifact fields for evaluation, replay, source-span auditing, or product-owner feedback aggregation.
- Impact: Affects artifact lineage clarity, raw output retention policy, privacy posture, and future provider-backed quality evaluation.

### 2026-05-12 — When should extraction JSON get a machine-readable schema?

- Context: The local trial CLI now has a checked-in example extraction JSON fixture and a user-facing guide with a validated embedded example. On 2026-05-18, a generated provider-neutral JSON Schema and CLI printer were added for `extract_units` output.
- Needed decision: Decide later whether to add runtime JSON Schema validation, provider-specific schema transforms, or external authoring helpers after real provider integration begins.
- Impact: Affects validation clarity, compatibility guarantees, provider structured-output compatibility, and future schema migration surface.

### 2026-05-11 — When should artifact versions diverge by artifact type?

- Context: Persisted AI working artifacts now share `artifact_schema_version: 0.1.0`.
- Needed decision: Introduce per-artifact versioning only if run logs, patch packages, review reports, or draft packages evolve independently enough that one shared version becomes misleading.
- Impact: Affects migration strategy, compatibility checks, and future artifact import/replay behavior.

### 2026-05-10 — When should the approved OpenAI live smoke be executed?

- Context: Gate 4 is provider-neutral and does not call an LLM. On 2026-05-20, OpenAI was selected as the first provider target, the product owner adopted the OpenAI official SDK as the first-provider integration style, and `DIAMONDDUST_OPENAI_API_KEY` was approved as the API key environment variable name. On 2026-05-21, the pre-live-smoke OpenAI adapter implementation was completed with sanitized preview, dry-run, fail-closed real-run guard, fake/mock tests, and provider-free CI defaults. On 2026-05-22, `openai-live-smoke-readiness` was added to make the remaining live-smoke decisions explicit without reading keys or calling providers. On 2026-05-23, the product owner approved exactly one future manual OpenAI `extract_units` fixture smoke using `gpt-5.5`, 60-second timeout, zero retries, no fallback, USD 1.00 per-run cost limit, and hash/metadata-only raw output retention. The controlled `openai-extract-units` live path is now implemented but unrun.
- Needed decision: Explicitly ask Codex to execute the blocked one-manual-live-smoke plan when ready.
- Impact: Affects external provider cost, secret handling, prompt/source/schema externalization for the fixture, run logs, validated extraction artifacts, and live-smoke milestone review.

### 2026-05-17 — How should provider execution requests map to the first provider SDK?

- Context: Concrete provider adapters now receive a typed provider execution request containing both `ProviderRequest` and `RenderedPrompt`. A provider integration readiness gate now reports blocked until all required decisions are explicit. A first-provider adapter design, product-owner decision package template, completed pre-live-smoke OpenAI adapter implementation, and OpenAI live-smoke readiness report now exist. OpenAI SDK request mapping is implemented behind fail-closed gates, and one future manual fixture smoke is approved and has a controlled CLI execution path but has not been run. DeepSeek mapping now exists as a second provider path using OpenAI-compatible Chat Completions JSON Output mode and the existing OpenAI SDK dependency.
- Needed decision: After the first manual smoke, decide whether the OpenAI request mapping, structured-output mechanism, cost metadata, source binding, and validated extraction artifact shape are sufficient for follow-up real-provider evaluation.
- Impact: Affects provider SDK coupling, privacy posture, replayability, prompt traceability, cost control, and extraction quality evaluation.

### 2026-05-23 — What should DeepSeek use for schema-constrained extraction?

- Context: DeepSeek adapter code, sanitized preview, dry-run, fail-closed extract path, fake/mock tests, and controlled fixture smoke commands now exist. On 2026-05-25, controlled fixture smokes reached DeepSeek and returned provider request ids, but typed validation still failed after prompt hardening: first top-level source identity, then missing unit id, then non-string enum, then non-array `unit_candidates`. DeepSeek JSON Output mode uses `response_format={"type": "json_object"}` and does not provide the same strict JSON Schema enforcement expected from stronger structured-output mechanisms.
- Needed decision: Decide whether to keep iterating prompt guidance, try a different DeepSeek model or API mechanism, add a narrow safe normalization layer for common JSON-mode shape drift, or prioritize providers with strict schema output before testing real notes.
- Impact: Affects external provider cost, privacy, provider comparison, extraction quality evaluation, and whether DeepSeek becomes a durable alternative to OpenAI.

## Patch Review

### 2026-05-11 — Should review package writes become transactional?

- Context: Review package persistence writes raw patch JSON, candidate notes, and review report together, but does not yet provide transaction or rollback behavior if one artifact write fails.
- Needed decision: Decide whether filesystem transaction semantics are needed before real CLI/UI review flows.
- Impact: Affects review artifact consistency, replay, and failure recovery.

### 2026-05-10 — When should storage apply/revert behavior be implemented?

- Context: Gate 5 models accepted patch handoff but does not mutate formal vault files. Patch persistence, read-only path/ID conflict checks, and dry-run apply plans now exist.
- Needed decision: Implement storage adapter apply/revert execution only after explicit user acceptance handoff, rollback behavior, and write-failure tests are designed.
- Impact: Affects formal write safety, rollback guarantees, and Git diff inspection.

## Blog Draft

### 2026-05-10 — When should provider-backed editorial drafting be introduced?

- Context: Gate 6 uses deterministic scaffolding from accepted units and does not call an LLM.
- Needed decision: Introduce provider-backed prose generation only after provider policy, prompt versions, fixtures, and quality thresholds are ready.
- Impact: Affects dependencies, cost, evidence coverage, unsupported claim risk, and quality evaluation.

## Release Automation

### 2026-05-28 — When should the alpha package become a native or published release?

- Context: A source-based trial-client alpha package can now be generated for a
  small user group. It is intentionally not a stable release, signed installer,
  GitHub Release, or package-publishing workflow.
- Needed decision: After enough real-user trial feedback, decide whether to
  invest in a native Win11 installer, checksums/signing, version tags, and
  release publishing.
- Impact: Affects distribution polish, support burden, user trust, and release
  governance.

### 2026-05-14 — When should release publishing and versioning become gated?

- Context: CI now validates wheel build/install and the `diamonddust local-trial-fixture` smoke path, but no release workflow uploads build artifacts, checks version tags, or publishes distributions.
- Needed decision: Decide when versioning policy, artifact upload, and package publishing should become blocking release gates.
- Impact: Affects future distribution, changelog/version discipline, and whether users can install DiamondDust outside local source checkouts.

### 2026-05-14 — Should GitHub branch protection require CI before merge?

- Context: Repository-file CI now runs install, unit tests, compile checks, whitespace checks, and local trial fixture smoke on pull requests and pushes. GitHub branch protection is not configured by repository files.
- Needed decision: Decide whether to require the CI check through GitHub branch protection before merging PRs.
- Impact: Affects review reliability, merge safety, and future contributor workflow.
