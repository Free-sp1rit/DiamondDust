# Decisions

Record durable technical and governance decisions here.

## Current Governance Baseline Decisions

### 2026-05-28 — Split trial client into local Python backend and maintainable React frontend

- Decision: Keep the Python trial-client service as the local backend for
  provider execution, artifact loading, workspace import, feedback persistence,
  and safety boundaries, while introducing a React/Vite/TypeScript frontend as
  the maintainable UI surface for broader alpha trials.
- Reason: Real-note provider trials need a simpler client for small-scale user
  feedback, but frontend complexity should not leak into domain validation,
  provider adapters, storage adapters, or formal vault behavior.
- Alternatives: Continue expanding the embedded HTML string only; build a full
  desktop app immediately; move trial orchestration into frontend code.
- Risks: The frontend dependency surface introduces new maintenance and
  distribution work. The client must remain local-first and must not turn AI
  output into formal knowledge without the existing review boundaries.
- Follow-up: Use the alpha client to collect real-note quality feedback before
  adding more core knowledge features or richer graph visualization.

### 2026-05-25 — Harden extraction prompt guidance for candidate ids and enums

- Decision: The `extract_units.v1` prompt now includes a request-derived `unit_id_prefix`, explicit instructions that every `unit_candidates` item must include a non-empty id, and explicit guidance that enum-valued fields must be JSON strings. The embedded output schema also describes the candidate id expectation, and extraction validation errors identify the failing candidate index.
- Reason: DeepSeek JSON Output mode reached the provider but returned incomplete or wrongly typed unit candidate fields. Prompt-guided providers need more explicit candidate identity and enum-string instructions, while typed validation must remain fail-closed.
- Alternatives: Auto-fill missing ids in application code; require a schema version change; persist raw provider output for manual patching.
- Risks: Prompt guidance may still not guarantee compliance for JSON-mode providers, and id/enum convention tuning may be needed after more provider samples.
- Follow-up: Re-run a controlled DeepSeek fixture smoke and review whether the provider can now produce a validated extraction artifact.

### 2026-05-25 — Bind top-level provider source identity from request context

- Decision: The application provider extraction handoff treats the request payload `source_input_id` as authoritative top-level lineage and binds that value into structured provider output before typed validation.
- Reason: Real provider JSON output can treat `source_input_id` as generated text, but DiamondDust already owns the source identity through the ingested Markdown request. Binding only the top-level lineage field avoids rejecting otherwise source-preserving output while keeping source-reference validation authoritative.
- Alternatives: Keep failing immediately when top-level provider `source_input_id` differs; let provider adapters rewrite all source refs; persist raw provider output for manual repair.
- Risks: The run-log `output_hash` tracks the validation payload rather than a full raw response body; raw provider request/response persistence remains intentionally disabled.
- Follow-up: Keep unit `source_refs` strict. If providers keep producing wrong or incomplete source refs, improve prompt/schema/evaluation before broadening live provider use.

### 2026-05-23 — Add DeepSeek adapter using OpenAI-compatible SDK boundary

- Decision: Implement DeepSeek as a second concrete provider adapter for `extract_units` using DeepSeek's documented OpenAI-compatible API through the existing OpenAI SDK dependency, with base URL `https://api.deepseek.com` and API key env var name `DIAMONDDUST_DEEPSEEK_API_KEY`.
- Reason: The product owner requested DeepSeek API-key call support, and DeepSeek's official docs support OpenAI SDK-compatible access. Reusing the existing SDK avoids adding another production dependency while keeping provider-specific behavior isolated to the AI adapter layer.
- Alternatives: Add a separate DeepSeek SDK or use direct HTTP. Both would increase dependency or locally maintained protocol surface before DeepSeek quality is validated.
- Risks: DeepSeek JSON Output mode is prompt-guided and weaker than provider-side strict JSON Schema, so DiamondDust typed runtime validation remains the acceptance boundary before output can become domain data.
- Follow-up: Do not run DeepSeek live calls until model, cost, key reading, network call, and prompt/source/schema externalization scope are explicitly approved for the run. Consider a DeepSeek-specific readiness package if it becomes a durable provider option.

### 2026-05-23 — Approve one manual OpenAI fixture live smoke, not recurring live use

- Decision: Record the product-owner decision package for exactly one future manual OpenAI `extract_units` live smoke using `gpt-5.5`, `DIAMONDDUST_OPENAI_API_KEY`, one small fixture essay, timeout 60 seconds, zero retries, no fallback, USD 1.00 per-run cost limit, and hash/metadata-only raw output retention.
- Reason: The OpenAI adapter, safety valves, readiness report, and validated extraction artifact path are now sufficient to prepare a controlled first live smoke without widening scope to real user essays or recurring provider use.
- Alternatives: Keep live smoke blocked until more evaluation tooling exists; approve recurring live smoke; approve a broader real-user essay smoke.
- Risks: A one-smoke approval could be mistaken for general provider authorization, so the decision package keeps recurring live smoke, real user essay externalization, provider-side tools, raw request/response persistence, patch acceptance, formal apply, and publication explicitly unapproved.
- Follow-up: Do not run the live smoke until the product owner explicitly asks to execute the blocked live-smoke plan. During execution, read the approved key only inside the live-smoke path, perform exactly one provider/network call, persist only hashes/metadata and typed validated extraction artifacts, and verify no formal vault write occurred.

### 2026-05-23 — Implement controlled OpenAI live-smoke execution path

- Decision: Extend `openai-extract-units` from a fail-closed safety valve into a controlled one-smoke execution path that remains blocked by default and only reaches key reading/provider execution when all approved live-smoke flags, model, fixture, timeout, cost, and retention constraints are present.
- Reason: The project needs an executable path for the first manual provider smoke, but preview, dry-run, readiness, tests, and CI must remain provider-free and secret-free.
- Alternatives: Keep the live smoke blocked until manual scripting; run OpenAI directly outside DiamondDust; broaden the command into a general provider execution CLI.
- Risks: A live CLI path can be mistaken for recurring provider approval, so the command enforces the approved fixture, `gpt-5.5`, 60-second timeout, zero retries, USD 1.00 cost limit, and hash/metadata-only retention.
- Follow-up: Run the blocked live-smoke plan only when explicitly requested. After the smoke, review provider output quality before expanding beyond the fixture.

### 2026-05-20 — Use OpenAI official SDK for the first provider adapter

- Decision: Adopt the OpenAI official SDK as the future first-provider adapter integration style for `extract_units`.
- Reason: The first real-provider task is structured extraction, and the official SDK should reduce provider-specific mapping burden while DiamondDust keeps provider types isolated behind the AI adapter boundary.
- Alternatives: Direct HTTP remains the fallback if SDK boundary risk, dependency footprint, or long-term maintenance concerns later outweigh SDK benefits.
- Risks: The SDK introduces a production dependency surface and must not leak provider-specific types into domain core, application orchestration, storage adapters, formal vault code, or artifact contracts.
- Follow-up: Do not modify dependency files, implement the real adapter, read API key values, make network calls, run live smoke, persist raw provider output, or enable non-`extract_units` provider tasks until those actions are separately approved.

### 2026-05-20 — Approve OpenAI API key environment variable name only

- Decision: Approve `DIAMONDDUST_OPENAI_API_KEY` as the environment variable name for the future OpenAI adapter path.
- Reason: The future adapter needs one explicit, reviewable secret lookup name, while preview/readiness commands must remain key-free.
- Alternatives: Leave the env var name pending; use provider-default SDK lookup behavior; allow multiple fallback env var names.
- Risks: Env var name approval can be mistaken for permission to read or persist the key value, so key reading remains disabled until a separately approved real provider run or live smoke.
- Follow-up: Do not read, log, persist, or request the key value until live-run approval explicitly permits key reading. Keep preview commands key-free.

### 2026-05-20 — Approve First OpenAI Adapter implementation up to pre-live-smoke ready

- Decision: Approve the First OpenAI Adapter Implementation, Pre-Live-Smoke Ready stage, including dependency file changes, OpenAI SDK installation, OpenAI adapter implementation, provider request/response/error mapping, structured output implementation, CLI payload preview, dry-run, real-run safety valves, fake/mock SDK tests, secret redaction tests, no-real-call-by-default tests, and provider-free CI protections.
- Reason: The project is ready to implement the adapter boundary and safety harness before any API key value is read or any live provider call is made.
- Alternatives: Keep implementation blocked until live-smoke approval; skip the pre-live-smoke stage and approve live provider integration directly.
- Risks: Real-run CLI flags or SDK dependency presence may be mistaken for permission to call OpenAI, so the implementation must fail closed before key reads or network calls until separately approved.
- Follow-up: Product owner must approve the active implementation plan before code starts. Default model, API key value reading, real provider calls, network calls, prompt/source/schema externalization, cost limit, live smoke, raw provider output persistence, patch acceptance, formal apply, and publication remain separately unapproved.

### 2026-05-16 — Keep provider adapters envelope-only in the v0 skeleton

- Decision: Provider Adapter Boundary Skeleton introduces provider-neutral request, response, error, settings, usage, and fake-provider envelopes for `extract_units` only. Provider adapters return typed envelopes and do not persist artifacts by default.
- Reason: DiamondDust needs a testable boundary for future real-provider extraction without adding SDKs, reading API keys, making network calls, or mixing provider execution with storage/formal vault behavior.
- Alternatives: Let provider adapters write `_ai_runs` directly; let provider output produce `KnowledgePatch` directly; introduce a real provider SDK immediately.
- Risks: Future implementation must preserve ownership boundaries: application records run log data, storage persists artifacts, and provider adapters only execute/return envelopes.
- Follow-up: Escalate before adding provider SDK dependencies, reading API keys, making real network calls, enabling provider-side tools, enabling cost-bearing behavior, or persisting real raw provider output.

### 2026-05-16 — Record provider envelope metadata through run-log context

- Decision: Provider request ids, retry counts, and token usage are recorded as optional typed AI run-log artifact context, mapped by the application layer from provider response/error envelopes and persisted by the storage adapter under `_ai_runs`.
- Reason: Future real-provider extraction needs traceable run metadata, but provider adapters should remain side-effect free and raw provider output should remain outside durable run logs.
- Alternatives: Store provider metadata directly in provider adapters; add provider fields to domain extraction models; defer trace metadata until after real provider integration.
- Risks: Run-log artifact consumers may treat optional provider metadata as a stable compatibility contract before replay/import requirements are designed.
- Follow-up: Clarify latency units and raw output retention policy before recording production provider metrics.

### 2026-05-16 — Keep model policy conservative before real provider integration

- Decision: Add a provider-neutral v0 model policy skeleton that defaults to `first_provider: undecided`, allows only `extract_units`, requires structured output, rejects unapproved real-provider calls before provider execution, disables fallback, and forbids raw provider output persistence/logging and API key logging.
- Reason: Future provider work needs an executable policy boundary before SDK, auth, cost, retry, fallback, or raw-output decisions are approved.
- Alternatives: Keep policy only in docs; add a real provider SDK immediately; let provider adapters decide policy internally.
- Risks: Policy fields can become a compatibility surface before CLI/config usage is designed.
- Follow-up: Create an explicit provider integration escalation before choosing the first provider, model, SDK, API key env var, cost limit, retry policy, raw output retention, or fallback behavior.

### 2026-05-16 — Build provider requests from ingestion before provider execution

- Decision: Add an application-layer builder that converts `IngestedMarkdownEssay` values into provider-neutral `extract_units` requests with source identity, source path, content hashes, body line range, frontmatter, body text, and source reference payload fields.
- Reason: Real-provider extraction needs a deterministic, testable Markdown-to-provider-request handoff before prompt rendering or provider SDK integration.
- Alternatives: Let provider adapters read Markdown directly; build request payloads ad hoc in CLI code; wait until real provider integration to define the payload.
- Risks: Request payload field names may become a compatibility surface, and the payload contains essay body text that must not be sent to an external provider without explicit approval.
- Follow-up: Add prompt rendering only after first-provider, prompt review, API key, network, and cost decisions are approved.

### 2026-05-16 — Render extraction prompts before provider execution

- Decision: Add a provider-neutral `extract_units.v1` prompt renderer that converts typed provider requests into deterministic prompt packages with source metadata, output instructions, and stable prompt hashes.
- Reason: Future real-provider extraction needs a testable request-to-prompt handoff before SDK, auth, network, and model-quality decisions are approved.
- Alternatives: Let provider adapters render prompts internally; keep prompts only in docs; wait until real provider integration to define prompt packages.
- Risks: Prompt text and prompt package fields may become compatibility surfaces, and rendered prompts contain essay body text that must not be sent externally without explicit approval.
- Follow-up: Add prompt review and golden-output evaluation only after first-provider, API key, network, and cost decisions are approved.

### 2026-05-16 — Compose provider extraction in the application layer

- Decision: Add an application-level `extract_units` provider orchestration boundary that builds provider requests, renders prompts, executes a supplied provider boundary, validates structured output, and returns run-log context with prompt hash.
- Reason: Future real-provider extraction needs one testable orchestration seam while preserving the separation between application flow, provider adapters, domain validation, and storage persistence.
- Alternatives: Let provider adapters build requests and persist run logs; call provider clients directly from CLI code; defer orchestration until real provider integration.
- Risks: The orchestration result may become an application API surface, and prompt hash traceability must not be mistaken for prompt text persistence.
- Follow-up: Escalate before deciding how rendered prompts are passed into concrete provider SDK calls, and before enabling real network calls, API key value reads, costs, fallback, or raw output retention.

### 2026-05-17 — Pass rendered prompts through typed provider execution requests

- Decision: Add a prompt-aware `ProviderExecutionRequest` boundary that combines `ProviderRequest` and `RenderedPrompt`, validates metadata alignment, and is the v0 input shape for concrete provider adapters.
- Reason: Concrete provider adapters should not re-render prompts internally or infer prompt data from ad hoc payloads; they need a typed, testable handoff before real SDK mapping is approved.
- Alternatives: Keep provider adapters request-only; let adapters re-render prompts; pass loose dictionaries or SDK-specific message objects through application code.
- Risks: The execution request becomes part of the adapter contract, and prompt text remains in memory even though it is not persisted by default.
- Follow-up: Escalate before mapping `ProviderExecutionRequest` into a provider SDK request body, reading API keys, making network calls, or retaining prompt/raw output text.

### 2026-05-17 — Gate real-provider integration with explicit readiness decisions

- Decision: Add an application-level readiness gate that reports blocked until all required real-provider decisions are explicit and the first-provider task scope remains `extract_units` only.
- Reason: The project needs a fail-closed guard before SDK, auth, network, cost, retry, fallback, prompt externalization, or raw-output retention behavior can enter implementation.
- Alternatives: Keep readiness only in docs; ask for decisions ad hoc during provider implementation; start real-provider code before all approvals are explicit.
- Risks: The decision set may become a planning contract and may need new fields after the first provider is chosen.
- Follow-up: Use the readiness report as input to the first-provider escalation and implementation plan; it does not replace user approval, PR review, or milestone review.

### 2026-05-17 — Render provider readiness reports for review

- Decision: Add deterministic Markdown rendering for typed provider integration readiness reports.
- Reason: The product owner needs a readable review artifact before first-provider escalation, but rendering must not read API key values, call providers, persist prompt text, or imply implementation approval.
- Alternatives: Inspect readiness only through tests/code; persist readiness reports as storage artifacts immediately; include provider-specific SDK request details now.
- Risks: The rendered report format may become a review interface and could be mistaken for approval unless its boundaries stay explicit.
- Follow-up: Use rendered readiness output as planning/escalation input only; separately approve provider, model, SDK dependency, API key env var, network calls, cost, retry, fallback, and raw-output retention before real-provider integration.

### 2026-05-17 — Expose provider readiness as a diagnostic CLI command

- Decision: Add `diamonddust provider-readiness-report` to render readiness reports from CLI-provided decision values.
- Reason: First-provider escalation needs a product-owner-visible checklist, but the command must remain diagnostic and must not read API key values, call providers, persist artifacts, or record approval.
- Alternatives: Keep readiness reports code-only; write readiness reports to `_ai_reports/`; start real provider integration directly.
- Risks: CLI approval flags can be mistaken for durable approval records, and future automation may need an explicit fail-on-blocked mode.
- Follow-up: Treat CLI output as review input only; record real provider approvals separately before SDK, API key, network, cost, fallback, or raw-output behavior is implemented.

### 2026-05-17 — Draft provider integration escalation requests from readiness state

- Decision: Add deterministic escalation request drafting from typed provider readiness reports and expose it through `diamonddust provider-escalation-request`.
- Reason: Real provider integration requires explicit product-owner decisions, and the project needs a repeatable way to present those decisions without recording approval or enabling provider behavior.
- Alternatives: Hand-write escalation requests; persist approval artifacts immediately; start real provider implementation directly.
- Risks: The draft may be mistaken for approval if copied without review, and requested decision fields may need expansion after the first provider is chosen.
- Follow-up: Treat escalation drafts as review input only; separately record user approval before SDK dependencies, API key value reads, network calls, cost behavior, fallback, prompt externalization, or raw-output retention.

### 2026-05-17 — Load provider decision diagnostics from JSON input

- Decision: Add strict JSON mapping input for provider integration decisions and allow readiness/escalation CLI commands to load it through `--decisions-json`.
- Reason: Provider approval packages need a reviewable decision input shape that is less error-prone than long command lines, while still becoming typed decisions before assessment.
- Alternatives: Keep flags only; merge JSON and flags with override rules; persist decision JSON as an approval artifact.
- Risks: Decision JSON field names may become a user-facing contract, and JSON files can be mistaken for durable approval records.
- Follow-up: Treat decision JSON as diagnostic input only; design a separate approval artifact if durable approval records are later needed.

### 2026-05-17 — Provide a blocked provider decisions JSON template

- Decision: Add a blocked-by-default provider decision JSON template and expose it through `diamonddust provider-decisions-template`.
- Reason: The product owner needs an easy way to start a decision JSON file without copying field names from code, but the template must not select a provider, record approval, or include secrets.
- Alternatives: Keep JSON input undocumented by example; check in a provider-specific example; make the template a durable approval artifact.
- Risks: A copied template file can still be mistaken for an approval record, and field names remain a user-facing input contract.
- Follow-up: Treat generated templates as editable diagnostic input only; design a separate durable approval artifact if approval records are needed later.

### 2026-05-10 — Separate runtime AI autonomy from development-agent autonomy

- Decision: Runtime AI inside DiamondDust may only generate candidates, relations, patches, drafts, and reports; the coding agent may autonomously plan, edit code/docs, test, review, and propose changes within the active task scope.
- Reason: The product safety boundary must prevent direct AI mutation of formal knowledge, while development work still needs agent autonomy to move efficiently.
- Alternatives: Treat all AI autonomy as forbidden until patch review is stable; allow runtime AI to mutate formal notes directly.
- Risks: The distinction must remain explicit so future product features do not inherit development-agent freedoms.
- Follow-up: Keep runtime AI write behavior behind validated patch review and user acceptance.

### 2026-05-10 — Use project docs as DiamondDust source of truth

- Decision: DiamondDust-specific product facts, architecture boundaries, schemas, review gates, and governance decisions live in `docs/`; `AGENTS.md` remains the navigation and operating-control plane.
- Reason: This keeps durable project context in the repository and avoids relying on chat history.
- Alternatives: Put all governance in `AGENTS.md`; encode project facts in reusable skills; rely on external issue history.
- Risks: Docs can drift from implementation if not updated during behavior, schema, or architecture changes.
- Follow-up: Update docs and repo memory whenever public behavior, schema, architecture, workflow, or policy changes.

### 2026-05-10 — Use skills for reusable workflows only

- Decision: Skills may define repeatable workflows such as planning, milestone review, debugging, PR review, and escalation, but must not duplicate or override DiamondDust product truth.
- Reason: Skills should improve agent process without becoming a competing authority for project-specific facts.
- Alternatives: Store project governance in skills; avoid skills entirely.
- Risks: A stale skill could conflict with project docs.
- Follow-up: Prefer project docs in conflicts and create an escalation request if following a skill would reduce delivery quality.

### 2026-05-10 — Require execution plans and repo memory for non-trivial tasks

- Decision: Non-trivial work requires an execution plan under `docs/exec-plans/active/`, durable context updates under `docs/context/`, and completed-plan compression under `docs/exec-plans/completed/`.
- Reason: The project needs continuity across context compression, review cycles, and future agent sessions.
- Alternatives: Use chat-only plans; use ad hoc notes outside the repo.
- Risks: Planning overhead can grow if plans include raw logs or speculative detail.
- Follow-up: Keep plans concise, revise them when evidence changes, and avoid persisting temporary debugging noise.

### 2026-05-10 — Keep implementation behind review gates

- Decision: Product implementation code should wait until startup governance and architecture docs are approved and the relevant review gates are satisfied.
- Reason: The MVP depends on safety-critical boundaries around schema validation, patch review, formal writes, and provider neutrality.
- Alternatives: Begin product code before Gate 0/Gate 1 approval; mark gates passed without review.
- Risks: Delaying implementation can slow visible progress.
- Follow-up: Ask the product owner to review startup docs and decide whether Gate 0 and Gate 1 can be marked passed.

### 2026-05-10 — Initialize minimal governance skills under `skills/`

- Decision: Create lightweight repo-local governance skills for planning, escalation, milestone review, PR review, and Git workflow under `skills/<skill-name>/SKILL.md`.
- Reason: The product owner approved initializing minimal governance skills, and the workspace `.codex/` and `.agents/` directories are read-only.
- Alternatives: Use hidden `.codex/skills/` or `.agents/skills/` directories; create scripts/assets/references; keep the workflows only in docs.
- Risks: `skills/` may require later wiring if the active Codex environment discovers only a different skill path.
- Follow-up: Confirm or document the skill discovery path when repo-local skill loading becomes necessary.

### 2026-05-10 — GitHub task-branch push and PR creation permission

- Decision: For future development, the coding agent may run GitHub PR workflow preflight, push the current task branch, and use `gh pr create`; the coding agent must not use `gh pr merge`, must not push `main`, and must not force push.
- Reason: The product owner explicitly approved task-branch push and PR creation while keeping merge and protected-branch authority with the product owner.
- Alternatives: Require approval for every push and PR creation; allow full PR merge automation.
- Risks: Local proxy or `gh` authentication can still fail even when the permission boundary is approved.
- Follow-up: Before PR creation, run preflight with `gh auth status --hostname github.com`, `gh repo view --json nameWithOwner,url`, `curl -I https://api.github.com`, `git status`, and `git branch --show-current`; if preflight fails, stop and output an escalation request.

### 2026-05-10 — Implement Gate 2 schema skeleton with Python standard library

- Decision: Implement the initial domain schema skeleton with Python standard-library dataclasses, enums, and explicit `from_mapping` validation boundaries.
- Reason: Gate 2 needs typed schema validation, but the current scope does not require a production validation dependency.
- Alternatives: Add Pydantic immediately; defer all schema implementation.
- Risks: Future schema complexity may require migrating to Pydantic or another structured validation library.
- Follow-up: Reconsider a validation dependency only when schema complexity or adapter integration warrants it.

### 2026-05-10 — Implement Gate 3 Markdown ingestion with a minimal standard-library parser

- Decision: Implement Markdown ingestion in a storage adapter using only the Python standard library, with a constrained frontmatter parser for flat key/value pairs and string lists.
- Reason: Gate 3 needs read-only Markdown ingestion, source refs, and content hashes, but current fixture evidence does not justify a production Markdown or YAML dependency.
- Alternatives: Add PyYAML or a Markdown parser immediately; defer frontmatter parsing until later.
- Risks: Real-world essays may need richer YAML or Markdown parsing, and changing generated source id strategy later may require migration notes.
- Follow-up: Reconsider parser dependencies after MVP fixture/golden tests show concrete parsing requirements.

### 2026-05-10 — Keep Gate 4 extraction provider-neutral

- Decision: Implement AI extraction proposal validation as a provider-neutral boundary that accepts already-structured output, validates it into domain candidates, and records typed run logs without calling an LLM provider.
- Reason: Gate 4 needs structured output validation and run logs, but real provider calls would introduce external service, cost, prompt, and dependency decisions before the patch review workflow is stable.
- Alternatives: Add a concrete provider SDK now; defer AI boundary code until provider integration.
- Risks: Extraction quality cannot be measured until prompts, provider adapters, and golden fixtures exist.
- Follow-up: Add durable `_ai_runs/` storage and provider adapter interfaces in future tasks before real model calls are enabled.

### 2026-05-10 — Keep Gate 5 patch review separate from formal vault apply

- Decision: Implement patch review in the application layer as patch generation, diff inspection, rollback instructions, and accept/reject handoff without writing formal vault files.
- Reason: Gate 5 needs user acceptance before formal writes, while actual file mutation belongs in a future storage adapter.
- Alternatives: Apply accepted patches to Markdown files immediately; defer patch review until storage apply exists.
- Risks: Diff output is a structured summary rather than a real file diff, and duplicate path/ID checks need a vault index later.
- Follow-up: Add patch persistence and storage apply/revert behavior in later tasks while reusing `validate_patch_review_safety`.

### 2026-05-10 — Keep Gate 6 blog drafting deterministic and provider-free

- Decision: Implement blog draft generation as deterministic application-layer scaffolding from accepted patch review results, with claim inventory, unsupported claim reporting, and quality reports.
- Reason: Gate 6 needs blog draft safety and evidence coverage before real LLM editorial generation, publishing, or draft persistence.
- Alternatives: Add provider-backed prose generation now; defer blog draft workflow until formal vault apply exists.
- Risks: Draft content is not final editorial prose, and accepted units are sourced from accepted patch review results until formal apply behavior exists.
- Follow-up: Add durable draft persistence/export and provider-backed editorial drafting only after fixtures, provider policy, and review UX are ready.

### 2026-05-10 — Validate Gate 7 with deterministic release readiness fixtures

- Decision: Implement Gate 7 release readiness as an application-layer harness that runs five deterministic Markdown fixtures through ingestion, structured extraction validation, patch review acceptance, and blog draft generation without provider calls or formal vault writes.
- Reason: Gate 7 needs an end-to-end safety check across the MVP skeleton while preserving provider neutrality and the formal write boundary.
- Alternatives: Add real LLM provider calls and formal vault apply behavior now; mark Gate 7 manually without a runnable harness.
- Risks: The fixtures prove orchestration and boundary safety, not real extraction quality or editorial quality.
- Follow-up: Add product-owner-approved golden essays, durable AI working artifacts, candidate Markdown rendering/export, and formal vault apply/revert only after their safety checks are designed.

### 2026-05-11 — Export candidate Markdown only under AI suggestions

- Decision: Render candidate Markdown notes from safe `KnowledgePatch` create-note operations and write them only under `_ai_suggestions/candidate-notes/<patch_id>/`.
- Reason: MVP output needs candidate Markdown notes, but formal vault mutation must remain behind explicit patch acceptance and future storage apply/revert safety checks.
- Alternatives: Write candidate notes directly to formal target paths; defer candidate Markdown output until formal apply exists.
- Risks: The current frontmatter renderer is minimal and candidate note format may change when review UI and formal apply/revert are implemented.
- Follow-up: Add durable patch persistence, review report rendering, duplicate target checks, and formal apply/revert in separate reviewed milestones.

### 2026-05-11 — Export patch review reports only under AI reports

- Decision: Render patch review reports from safe `KnowledgePatch` values and write them only under `_ai_reports/patch-reviews/<patch_id>.md`.
- Reason: The MVP needs review reports before formal writes, and reports should summarize diff, candidate note paths, risks, and rollback steps without acting as acceptance records.
- Alternatives: Treat patch acceptance as the review report; defer review reports until a UI exists; write reports beside formal notes.
- Risks: Report format may change once durable patch persistence, review UI, and formal apply/revert exist.
- Follow-up: Add a combined review package writer and raw patch persistence so reports, candidate notes, and patch files can be reviewed together.

### 2026-05-11 — Persist review packages only in AI working directories

- Decision: Persist raw patch JSON, candidate notes, and patch review reports together as a review package, constrained to `_ai_suggestions/` and `_ai_reports/`.
- Reason: Human review needs a coherent artifact package before formal apply/revert, but the package must not imply acceptance or mutate formal vault files.
- Alternatives: Persist only raw patch JSON; persist only report and candidate notes; write package artifacts beside formal target paths.
- Risks: The current package write is not transactional, and raw patch JSON may need explicit versioning once external consumers depend on it.
- Follow-up: Add AI run log and blog draft persistence, then add duplicate path/ID checks before formal apply/revert.

### 2026-05-11 — Persist AI run logs without raw AI output

- Decision: Persist typed AI run logs under `_ai_runs/<run_id>.json`, including run metadata, hashes, validation status, `created_at`, and optional cache metadata, while excluding raw model output.
- Reason: Traceability needs durable run artifacts, but raw AI output should remain outside durable run logs until retention and privacy behavior are explicitly designed.
- Alternatives: Do not persist run logs; persist raw model outputs with run logs; wait for real provider integration.
- Risks: The run artifact JSON shape may need versioning before CLI/UI consumers depend on it.
- Follow-up: Add explicit artifact schema versioning and provider-specific metadata only when real provider adapters are introduced.

### 2026-05-11 — Persist blog draft packages only in AI working directories

- Decision: Persist blog draft Markdown under `_ai_suggestions/blog-drafts/<draft_id>/draft.md` and blog quality reports under `_ai_reports/blog-quality/<draft_id>.md`.
- Reason: Local trial and review workflows need durable draft artifacts, while publishing and formal vault mutation must remain behind explicit future approval.
- Alternatives: Keep drafts in memory only; write drafts directly to `70-publications/`; defer draft persistence until a CLI exists.
- Risks: The artifact Markdown shape may need explicit versioning before CLI/UI consumers depend on it, and deterministic draft content is still scaffold-quality prose.
- Follow-up: Add a local trial harness or CLI that writes review packages, run logs, and draft packages together without formal vault mutation.

### 2026-05-11 — Local trial uses structured extraction JSON before provider integration

- Decision: Add a local trial harness and module-based CLI that accepts one Markdown essay plus structured extraction JSON, then writes AI run logs, review packages, and blog draft packages under AI working directories.
- Reason: The product owner needs a way to inspect current tool output, while real provider calls, prompt execution, auth, cost, and model policy are not approved yet.
- Alternatives: Add a real provider call now; generate fake extraction internally; wait until formal vault apply exists before exposing any local trial path.
- Risks: The trial still requires structured JSON, and its non-persisted draft generation handoff must not be confused with user approval for formal vault apply.
- Follow-up: Add artifact schema versioning, product-owner-approved golden essays, and provider adapters only after the review boundary remains stable.

### 2026-05-11 — Version AI working artifacts separately from domain schemas

- Decision: Add a shared `artifact_schema_version` value of `0.1.0` to persisted AI working artifacts.
- Reason: Local trial outputs are now user-visible files, and version markers make future replay, migration, and CLI/UI compatibility safer without changing formal domain schemas.
- Alternatives: Leave artifacts unversioned; bump formal domain `schema_version`; assign independent versions to every artifact type immediately.
- Risks: Future artifact formats may diverge and require per-artifact versioning or tolerant readers for older unversioned artifacts.
- Follow-up: Add compatibility handling when artifact import/replay is introduced and document any future artifact schema bumps.

### 2026-05-11 — Provide a checked-in local trial fixture pair

- Decision: Add a small Markdown essay fixture and matching structured extraction JSON fixture under `tests/fixtures/local_trial/`.
- Reason: The product owner needs a ready-to-run local trial without manually authoring extraction JSON before provider integration exists.
- Alternatives: Keep only synthetic unit-test fixtures; generate extraction JSON dynamically; wait for a provider adapter before adding trial fixtures.
- Risks: The fixture proves orchestration and artifact output, not real extraction quality or editorial quality.
- Follow-up: Promote or replace fixtures with product-owner-approved golden essays and add user-facing extraction JSON schema notes.

### 2026-05-12 — Document local trial extraction JSON without changing runtime schema

- Decision: Add a standalone guide for the existing local trial extraction JSON input shape and validate the guide's embedded example through the current extraction validator.
- Reason: Product-owner trial runs need a concise authoring reference before provider integration exists, but this stage should not change runtime schema or introduce a machine-readable schema dependency.
- Alternatives: Keep only the checked-in fixture; add a JSON Schema document now; implement a provider adapter before documenting hand-authored JSON.
- Risks: The guide can drift if extraction validation changes, and hand-authored JSON still does not measure real extraction quality.
- Follow-up: Add machine-readable schema or richer authoring helpers only when external trial users or provider adapters require them.

### 2026-05-12 — Add read-only formal vault conflict checks before apply behavior

- Decision: Add a storage adapter preflight that checks `KnowledgePatch` create-note operations for existing formal target paths, existing formal note IDs, and duplicate patch target IDs/paths without writing vault files.
- Reason: Formal apply/revert needs path and ID safety before mutation can be reviewed, but enabling writes now would cross the formal vault boundary too early.
- Alternatives: Implement formal apply immediately; keep conflicts as review-report prose only; wait for a full vault index.
- Risks: The minimal frontmatter ID reader may miss complex YAML forms, and path/ID checks are necessary but not sufficient for future rollback safety.
- Follow-up: Add explicit apply/revert boundaries, rollback/write-failure tests, and richer frontmatter parsing only when fixtures prove the need.

### 2026-05-12 — Add formal apply dry-run plans before write execution

- Decision: Add a storage adapter dry-run plan that converts a conflict-free `KnowledgePatch` into planned formal note files, content hashes, and rollback steps without writing vault files.
- Reason: Future formal apply/revert needs an explicit, reviewable execution boundary before mutation is implemented.
- Alternatives: Implement formal apply immediately; keep only candidate Markdown artifacts; wait until a UI exists.
- Risks: The planned note renderer may need richer formatting before real apply, and dry-run plans do not prove write atomicity or rollback execution.
- Follow-up: Add explicit user acceptance handoff, write-failure tests, and revert execution before enabling formal vault mutation.

### 2026-05-14 — Write local trial feedback reports as the trial entrypoint

- Decision: Each local trial should write a Markdown feedback report under `_ai_reports/local-trials/<trial_id>.md` and include it in CLI output.
- Reason: Product-owner trials need one starting artifact that explains status, safety boundaries, reading order, errors, unsupported claims, and feedback prompts without adding provider calls or formal vault writes.
- Alternatives: Keep trial output only as scattered paths; build a UI first; write reports beside formal notes.
- Risks: The report format may need adjustment after real trial feedback, and the report must not be mistaken for user acceptance of a patch.
- Follow-up: Use the report in controlled trial review, then decide whether a richer feedback rubric, JSON summary, or UI surface is warranted.

### 2026-05-14 — Capture local trial feedback in the report artifact

- Decision: Add a human-fillable `Feedback Capture` section to local trial reports and document the safe trial review flow in `docs/guides/local-trial-user-feedback.md`.
- Reason: Product-owner trials need a durable place to record usability feedback while keeping feedback separate from patch acceptance, formal write approval, and publication approval.
- Alternatives: Keep feedback in chat only; create a separate feedback file; build a UI before collecting structured feedback.
- Risks: The rubric may need tuning after real trial use, and report edits are not machine-readable yet.
- Follow-up: After a controlled trial, decide which feedback fields should become release criteria, golden fixture expectations, or a structured feedback artifact.

### 2026-05-14 — Add minimal package metadata for CLI trial entrypoint

- Decision: Add `pyproject.toml`, expose `diamonddust = "diamonddust.cli:main"`, and add `python3 -m diamonddust` as a module entrypoint.
- Reason: Product-owner trial runs should have a standard command after editable install, while development can still use the module fallback.
- Alternatives: Keep only `PYTHONPATH=src python3 -m diamonddust.cli`; add a shell wrapper; wait until CI/release packaging exists.
- Risks: Packaging metadata may need expansion for real releases, and editable install behavior depends on local Python packaging tooling.
- Follow-up: Add CI and release/versioning checks before treating the package metadata as a release contract.

### 2026-05-14 — Add a one-command local trial fixture shortcut

- Decision: Add `diamonddust local-trial-fixture` as a shortcut for the checked-in fixture essay and extraction JSON, defaulting output to `knowledge-vault/`.
- Reason: Product-owner trial feedback should start from a simple safe command before custom essay extraction JSON is required.
- Alternatives: Keep only the full `local-trial` command; add a shell script; move fixtures into package data before adding a shortcut.
- Risks: The shortcut is repo-root oriented and proves fixture orchestration, not real provider extraction quality.
- Follow-up: Use the shortcut for controlled trial feedback, then decide whether fixture command behavior should become package-data-backed or CI-gated.

### 2026-05-14 — Add GitHub Actions as the CI validation baseline

- Decision: Add a GitHub Actions workflow that runs on pull requests and pushes, covering editable install, unit tests, compile checks, whitespace checks, and the `diamonddust local-trial-fixture` smoke path on Python 3.11 and 3.12.
- Reason: Local trial work is now user-visible enough that PR review should have automated validation instead of relying only on local milestone checks.
- Alternatives: Keep validation local only; add a shell script without remote CI; add heavier lint/typecheck tooling immediately.
- Risks: The first remote runner execution still needs to be observed after push, and branch protection must be configured separately if CI should block merges.
- Follow-up: Confirm the first remote CI run and decide whether GitHub branch protection should require the workflow before merge.

### 2026-05-14 — Package the provider-free local trial fixture assets

- Decision: Include the local trial essay and extraction JSON as package data under `diamonddust.fixtures.local_trial`, and load the `local-trial-fixture` shortcut from package resources instead of repository-relative test fixture paths.
- Reason: Product-owner trial runs should work after editable install from any working directory, not only from the repository root.
- Alternatives: Keep the shortcut repo-root oriented; require users to pass explicit fixture paths; move all test fixtures into package data.
- Risks: Packaged fixture assets can drift from repository fixture assets if parity tests are removed, and the fixture still validates artifact UX rather than real provider extraction quality.
- Follow-up: Run a controlled installed-CLI product-owner trial, then decide which real or semi-real essays should become golden fixtures.

### 2026-05-14 — Validate CI from a built wheel

- Decision: CI builds a DiamondDust wheel with `pip wheel`, installs that wheel with `pip install --force-reinstall --no-deps`, runs `pip check`, and then executes tests and local trial fixture smoke against the installed package.
- Reason: The packaged local trial fixture assets must be verified inside installable artifacts, not only editable source checkouts.
- Alternatives: Keep editable install validation only; add a release publishing workflow immediately; add an external build tool dependency.
- Risks: The current local Codex shell cannot reproduce wheel build/install because `pip` is unavailable, so remote GitHub Actions remains the source of truth for this gate.
- Follow-up: Confirm the first remote CI run, then decide later when versioning, artifact upload, and publishing should become release gates.

### 2026-05-14 — Persist machine-readable local trial outcomes

- Decision: Each local trial writes `_ai_reports/local-trials/<trial_id>.json` beside the Markdown feedback report, using the shared AI artifact schema version and explicit no-provider/no-formal-write boundary fields.
- Reason: Product-owner trial feedback starts from the Markdown report, but lightweight comparison, issue creation, and future aggregation need a structured summary that does not require parsing Markdown.
- Alternatives: Keep only the Markdown report; add a UI or analytics backend now; treat edited human feedback as structured acceptance data.
- Risks: The JSON shape may need to evolve after real product-owner trial feedback, and report-package writes are still not transactional.
- Follow-up: Use the JSON outcome in controlled trial review, then decide whether feedback fields should become typed user-input artifacts or release criteria.

### 2026-05-15 — Separate local trial pipeline status from product-owner verdict

- Decision: Local trial feedback reports and local trial outcome JSON use `trial_pipeline_status` for run success and `product_owner_verdict: pending` for product-owner acceptance state.
- Reason: A passed provider-free pipeline run must not imply product-owner acceptance, full MVP readiness, real AI extraction quality, formal patch acceptance, or publication approval.
- Alternatives: Keep ambiguous `status`/`passed` fields; add numeric scoring immediately; treat Markdown and JSON trial artifacts as semantically independent.
- Risks: Older generated reports and JSON outcomes retain ambiguous fields until regenerated, and future tooling may need compatibility handling if it parses older artifacts.
- Follow-up: Keep feedback capture as structured free text until the rubric is calibrated by real product-owner trial feedback.

### 2026-05-15 — Apply temporary trial feedback evaluation for outcome semantics

- Decision: For the current local trial feedback task only, product-owner feedback was evaluated against artifact semantics, maintainability, architecture boundaries, and review safety before changing code and docs.
- Reason: The product owner explicitly made this a temporary task-local principle, not a long-term governance rule.
- Alternatives: Automatically implement all trial feedback; write the temporary principle into governance docs without separate approval.
- Risks: Similar future tasks need explicit instruction or a separate governance approval if this behavior should become permanent.
- Follow-up: Do not treat this as a standing governance policy unless separately approved.

### 2026-05-15 — Add local trial run log scope through typed artifact context

- Decision: Local trial AI run logs use a typed storage-layer artifact context to add `trial_id`, `stage_label`, `run_scope`, `real_provider_call`, `fixture_driven`, `prompt_used`, `metrics_scope`, `source_input_id`, `output_artifacts`, and run-specific `not_validated` fields.
- Reason: Provider-free fixture runs must not be mistaken for real provider calls or real LLM quality validation, but generic AI run logs should stay provider-neutral and should not require local trial fields.
- Alternatives: Add local trial fields directly to the domain `AIRunLog`; leave fixture scope only in the Markdown report/JSON outcome; change `prompt_version` to a fixture-specific value.
- Risks: Older generated run logs lack the new fields until regenerated, and future replay tooling may need compatibility handling for earlier artifacts.
- Follow-up: Introduce a separate extraction output artifact only if replay/debug/user feedback requires it; keep raw provider output out of run logs until retention policy is approved.

### 2026-05-15 — Harden `_ai_suggestions` preview semantics

- Decision: Candidate manifests now state preview boundaries and raw KnowledgePatch source-of-truth behavior, local trial manifests can add fixture SourceRef scope through typed context, and local trial blog drafts can add provider-free fixture draft scope through typed context.
- Reason: `_ai_suggestions/` artifacts are user-visible previews and must not be mistaken for formal vault notes, accepted knowledge, real parser/source-span validation, real AI draft quality validation, or publication-ready output.
- Alternatives: Hand-edit generated trial artifacts only; add trial/stage metadata to every candidate note; add new extraction/path-audit artifacts now.
- Risks: Older generated manifests and drafts lack the new fields until regenerated, and Claim Inventory now needs role labels because it may include supporting concepts as well as claims.
- Follow-up: Revisit the Claim Inventory name/shape only if product-owner feedback shows that mixed claim/supporting concept entries are confusing.

### 2026-05-15 — Keep patch review reports as non-binding review prompts

- Decision: Patch review reports now include artifact frontmatter, pending decision metadata, suggested review order, preview-level rollback notes, and a `Review Decision Prompt` that explicitly does not record formal acceptance.
- Reason: Patch review reports are pre-acceptance AI report artifacts; they should guide human review without becoming a patch decision artifact or permission to apply formal vault writes.
- Alternatives: Keep body-only reports; record accept/reject directly in the report; create a patch decision artifact in this task.
- Risks: Older generated review reports lack the new metadata until regenerated, and a separate typed decision artifact is still needed before formal apply execution can be safely implemented.
- Follow-up: Design patch decision artifacts separately before implementing formal vault apply.

### 2026-05-16 — Clarify blog quality report semantics

- Decision: Blog quality reports now use frontmatter and `quality_status` wording for report validation, while local trial quality reports add provider-free fixture scope, pending product-owner verdict, real-AI-generation limits, fixture-specific risks, and publication approval boundaries through typed context.
- Reason: A passed fixture-driven quality report must not imply publication readiness, real AI generation quality validation, product-owner acceptance, or formal vault writes.
- Alternatives: Hand-edit only the generated trial report; keep body-only reports; add a numeric publication score immediately.
- Risks: Older generated blog quality reports lack the new frontmatter until regenerated, and future artifact import/replay may need compatibility handling for body-only reports.
- Follow-up: Calibrate publication and editorial quality criteria only after real product-owner trial feedback.

### 2026-05-16 — Keep local trial draft handoff distinct from patch acceptance

- Decision: Rename the local trial runtime field from simulated patch acceptance to `draft_generation_handoff_completed`, align `BlogQualityReportArtifact` with persisted `quality_status` naming, isolate fixture scope strings behind local trial constants, and render empty candidate manifest risks as `- none`.
- Reason: The trial harness uses a non-persisted accepted review result only to produce draft previews; the implementation should not preserve names that sound like real patch acceptance or invite provider-specific fixture flags to leak into future provider code.
- Alternatives: Keep the old field name for compatibility; leave provider-free fixture literals inline; defer cleanup until provider integration.
- Risks: Early direct Python callers of `LocalTrialResult.simulated_patch_acceptance` must update to `draft_generation_handoff_completed`.
- Follow-up: When real provider integration begins, keep provider execution context separate from provider-free fixture context and avoid reusing fixture markers for real model runs.

### 2026-05-18 — Compose provider decision packages from readiness state

- Decision: Add a deterministic provider decision package renderer and CLI command that compose the readiness report and escalation request draft from the same typed provider decision input.
- Reason: Product-owner review of first-provider readiness needs one coherent local artifact while preserving the distinction between diagnostic input, escalation drafting, and actual approval.
- Alternatives: Keep separate readiness and escalation commands only; persist a provider approval artifact now; start real provider integration immediately.
- Risks: The package could be mistaken for approval if boundaries weaken, so it explicitly states that it records no approval, calls no provider, reads no API key values, adds no SDK dependency, and authorizes no implementation.
- Follow-up: Treat decision packages as review input only; create a separate durable approval artifact only after the product owner approves that workflow.

### 2026-05-18 — Generate extract_units output schema from domain enums

- Decision: Add a provider-neutral JSON Schema generator and CLI command for `extract_units` structured output.
- Reason: Future real-provider structured output needs a machine-readable contract, but runtime typed validation must remain the authoritative boundary before provider output becomes domain data.
- Alternatives: Keep only the Markdown guide; check in a static schema that could drift from domain enums; add a JSON Schema validation dependency now.
- Risks: JSON Schema cannot express every runtime rule, such as source references matching the top-level source input, so docs and schema comments must keep that boundary clear.
- Follow-up: Use the schema as provider planning input only; decide separately whether a runtime JSON Schema validator is needed after real provider integration begins.

### 2026-05-18 — Carry extract_units output schema in rendered prompts

- Decision: Extend `RenderedPrompt` with `extract_units` output schema id, version, hash, and schema content, and include the schema hash in prompt identity.
- Reason: Future provider adapters need the machine-readable structured-output contract at the prompt execution boundary, while typed validation remains the authoritative gate after provider output returns.
- Alternatives: Keep schema available only through a separate CLI command; make concrete provider adapters regenerate schema independently; persist prompt/schema packages now.
- Risks: Provider-specific APIs may require adapter-level schema transforms later, and rendered prompt/schema payloads must not be persisted or sent externally without the existing real-provider approvals.
- Follow-up: Add provider-specific schema mapping only after provider, model, SDK, and structured-output mechanism decisions are approved.

### 2026-05-18 — Build provider-neutral execution payloads before SDK mapping

- Decision: Add provider-neutral execution payload types that convert `ProviderExecutionRequest` into reviewable messages, output instructions, schema metadata/content, model settings, and safety flags.
- Reason: Concrete provider adapters need a stable internal payload before any provider-specific SDK request mapping is approved.
- Alternatives: Let each future adapter inspect `RenderedPrompt` directly; map to one provider SDK shape now; persist provider payloads as artifacts.
- Risks: The payload contains prompt/schema content and must remain in-memory unless prompt/schema retention is separately approved.
- Follow-up: Add provider-specific request mapping only after first-provider, SDK, network, prompt externalization, structured-output mechanism, cost, and retry decisions are approved.

### 2026-05-18 — Expose provider payload preview as local review input

- Decision: Add a `provider-payload-preview` CLI command that builds the existing provider-neutral request, rendered prompt, and execution payload for one Markdown essay, then prints the payload JSON to stdout.
- Reason: The product owner needs to inspect prompt text, source body text, output instructions, schema content, model settings, and safety flags before approving any provider-specific SDK mapping or real network call.
- Alternatives: Require Python callers to assemble the payload manually; persist payload preview artifacts; wait until a concrete provider adapter exists.
- Risks: Payload preview output contains prompt/source/schema content, so it must remain an explicit local review action and must not be mistaken for provider execution or provider approval.
- Follow-up: Keep provider-specific SDK payload mapping, prompt externalization, raw output retention, API key value reads, and real provider calls behind separate approval.

### 2026-05-19 — Bind provider output to request source identity

- Decision: The application provider extraction handoff now fails closed when structured provider output has a top-level `source_input_id` that does not match the provider request payload `source_input_id`.
- Reason: Typed extraction validation already checks internal source reference preservation, but real provider output also needs to be bound to the request context before it can become domain data.
- Alternatives: Put request/source matching into domain validation; rely only on prompt instructions; defer the check until concrete provider integration.
- Risks: Future non-essay extraction tasks may need task-specific source binding rules, and requests without `source_input_id` cannot benefit from this guard.
- Follow-up: Keep source binding in the application/provider handoff and add task-specific binding rules if future provider tasks are approved.

### 2026-05-20 — Define first-provider adapter design before implementation

- Decision: Add a first-provider adapter design document and product-owner decision package template before implementing any real provider adapter.
- Reason: The provider-neutral skeleton is ready for adapter planning, but real integration still requires explicit product-owner decisions for provider, model, dependency, API key env var, network, prompt externalization, structured output, cost, timeout, retry, fallback, and retention behavior.
- Alternatives: Start implementation from the existing readiness report only; encode adapter decisions directly in code; wait until a provider is selected before documenting boundaries.
- Risks: The template could be mistaken for approval, so it defaults to pending and states that implementation still requires explicit product-owner approval and a separate PR.
- Follow-up: Use `docs/templates/PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md` as the review input before creating a selected-provider implementation plan.

### 2026-05-20 — Approve real-provider implementation preparation only

- Decision: Product owner approved real provider code implementation preparation, selected OpenAI as the first provider target for planning, and kept actual implementation, SDK/dependency changes, API key value reading, real network calls, live smoke, raw output retention, patch acceptance, formal apply, and publication unapproved.
- Reason: DiamondDust can now compare OpenAI SDK vs direct HTTP, refine adapter mapping, CLI safety valves, and CI policy without crossing into real provider execution.
- Alternatives: Treat OpenAI selection as full implementation approval; keep first provider fully undecided; start SDK implementation immediately.
- Risks: OpenAI-targeted planning could be mistaken for live-call approval, so the decision package keeps `records_real_provider_approval: false`, `real_provider_calls_approved: false`, and `live_smoke_approval_status: pending`.
- Follow-up: After the later SDK and API key env var decisions, request separate approval for default model, dependency file changes, API key value reading, real network calls, timeout/retry/cost policy, raw output retention, and any live smoke.

### 2026-05-21 — Implement OpenAI adapter only to pre-live-smoke readiness

- Decision: Add the OpenAI SDK dependency and implement the OpenAI adapter, request/response/usage/error mapping, sanitized CLI payload preview, dry-run, fail-closed future real-run safety valve, fake/mock SDK tests, secret redaction tests, and provider-free CI dependency install behavior.
- Reason: DiamondDust needs concrete first-provider adapter code ready for owner review while preserving the boundary that no API key value is read, no prompt/source/schema is sent externally, no network call occurs, no raw provider output is persisted, and no formal vault write or patch acceptance is possible.
- Alternatives: Keep the project at design-only status; implement direct HTTP instead of the approved SDK; wait for live-smoke approval before writing adapter code.
- Risks: The OpenAI SDK dependency adds a provider-specific package surface, and the future real-run command could be mistaken for live approval if the fail-closed blockers are weakened.
- Follow-up: Before any live smoke, separately approve default model, API key value reading, prompt/source/schema externalization, per-run cost limit, real provider/network call, live-smoke scope, and whether any raw output hash/metadata retention beyond current defaults is allowed.

### 2026-05-22 — Separate live-smoke readiness from provider implementation readiness

- Decision: Add explicit provider decision fields for API key value reading, source body externalization, output schema externalization, one manual live smoke, and recurring live smoke, and add an OpenAI-specific live-smoke readiness report/CLI command.
- Reason: Env var name approval, adapter implementation, and generic provider readiness are not sufficient proof that a real live smoke is safe to run. The remaining live-smoke decisions must be visible and testable without reading secrets or calling a provider.
- Alternatives: Reuse the existing provider readiness report only; ask the product owner to approve live smoke directly in chat; defer readiness checks until the first live run.
- Risks: The diagnostic decision JSON shape gains new fields, so older decision files default these approvals to `false` and remain blocked until updated.
- Follow-up: Use `diamonddust openai-live-smoke-readiness` before any live smoke. The report is diagnostic only and still does not approve or execute live provider calls.

### 2026-05-22 — Persist validated extraction output as an AI working artifact

- Decision: Add `validated_extraction_output` JSON artifacts under `_ai_suggestions/extractions/` for extraction proposals that pass typed runtime validation and source consistency checks.
- Reason: Real-provider preparation needs durable lineage between AI run logs and downstream patch artifacts without persisting raw provider output. A validated extraction artifact gives reviewers a typed intermediate artifact before patch generation.
- Alternatives: Keep only run-log hashes and downstream patch JSON; persist raw provider output; wait until a live provider call exists before defining the artifact.
- Risks: The artifact could be mistaken for formal knowledge or patch acceptance, so the persisted payload includes explicit boundaries and remains under `_ai_suggestions/`.
- Follow-up: Revisit extraction artifact fields after real provider smoke feedback, especially source-span auditing, quality metrics, and replay needs.

### 2026-05-25 — Keep DeepSeek JSON mode shaping inside the adapter

- Decision: The DeepSeek adapter now adds the provider-neutral output instructions and a compact JSON example to the DeepSeek Chat Completions system message, and maps an adapter-level `max_tokens` value into requests.
- Reason: DeepSeek JSON mode returns valid JSON but does not enforce DiamondDust's schema. Keeping the JSON mode shaping inside `src/diamonddust/ai/adapters/deepseek.py` preserves high cohesion, avoids provider-specific behavior in domain validation, and lets typed runtime validation remain the acceptance boundary.
- Alternatives: Add alias compatibility for provider-chosen keys such as `units`; move DeepSeek-specific wording into the domain schema or application orchestrator; switch to raw-output postprocessing.
- Risks: The prompt payload becomes larger for DeepSeek calls, and successful fixture validation does not prove extraction quality on real user notes.
- Follow-up: Evaluate DeepSeek extraction quality on a product-owner-approved non-sensitive real note before enabling downstream patch generation from DeepSeek output.

### 2026-05-26 — Use Chinese for user-facing knowledge text

- Decision: Provider-neutral extraction prompts and schema descriptions now instruct providers to write generated user-facing knowledge fields in Simplified Chinese while preserving code, commands, identifiers, product names, file paths, API names, source reference metadata, and source quotes in original form.
- Reason: DiamondDust's formal knowledge base is intended for Chinese user review and reuse, but machine contracts must remain stable and provider-neutral.
- Alternatives: Translate every field into Chinese; keep all generated content in the provider's default language; add provider-specific language handling only for DeepSeek.
- Risks: Mixed-language notes still require human review for natural phrasing, and existing generated artifacts are not migrated.
- Follow-up: Evaluate the next real-note extraction artifact for Chinese title/content/reason quality before allowing downstream patch generation.

### 2026-05-27 — Build a local trial client before adding more core features

- Decision: Add a standard-library local browser client for real-note `extract_units` trials, focused on DeepSeek runs, artifact review, empty-extraction quality surfacing, and feedback capture.
- Reason: The core provider pipeline exists, but real-note feedback is insufficient. A small client can validate extraction usefulness before downstream core features expand.
- Alternatives: Continue CLI-only trials; build a full note editor; continue downstream patch/blog functionality first.
- Risks: The trial client makes real provider calls easier, so it must stay local-only, show boundaries, avoid API key disclosure, avoid raw provider output persistence, and keep formal apply/publish disabled.
- Follow-up: Use collected feedback artifacts to decide whether to harden prompts, add quality gates, or change provider/model before expanding core workflows.

### 2026-05-28 — Trial client model presets and local artifact management

- Decision: Restrict the trial client UI to DeepSeek-V4-Flash and DeepSeek-V4-Pro presets, default to DeepSeek-V4-Flash, allow local-only API key writing to `~/.config/diamonddust/provider-secrets.env`, and manage historical extraction versions by note without regenerating output.
- Reason: Product-owner testing showed that free-form model entry, shell-only key setup, and regenerate-only review flow made small-user trials too hard to operate.
- Alternatives: Keep CLI-only key setup; keep free-form model entry; build a larger data browser; delete no artifacts from the client.
- Risks: Local key writing is less secure than shell-managed secrets, so the client must never return key values. Artifact deletion must stay limited to trial-client generated AI working artifacts and never touch formal vault files.
- Follow-up: Use real-user feedback to decide whether artifact comparison, richer quality scoring, or model-specific recommendations are needed.

## Template

### YYYY-MM-DD — <decision title>

- Decision:
- Reason:
- Alternatives:
- Risks:
- Follow-up:
