# DeepSeek Provider Adapter Design

Status: implemented provider boundary; no live call executed by this stage.

## Source References

- DeepSeek quick start: `https://api-docs.deepseek.com/zh-cn/`
- DeepSeek JSON Output guide:
  `https://api-docs.deepseek.com/zh-cn/guides/json_mode`
- DeepSeek error codes:
  `https://api-docs.deepseek.com/zh-cn/quick_start/error_codes`
- DeepSeek models and pricing:
  `https://api-docs.deepseek.com/zh-cn/quick_start/pricing`

## Scope

The DeepSeek adapter is limited to:

- task: `extract_units`
- API family: DeepSeek OpenAI-compatible Chat Completions
- SDK dependency: existing `openai` Python SDK
- base URL: `https://api.deepseek.com`
- output mode: JSON Output with `response_format={"type": "json_object"}`
- typed runtime validation: required before provider output becomes domain data

Out of scope:

- provider-side tools
- web search
- file search
- MCP tool calls
- autonomous agent behavior
- default model selection
- raw provider request/response persistence
- patch acceptance
- formal vault apply
- publication

## Boundary

```text
Markdown essay
  -> storage.markdown.read_markdown_essay
  -> application.build_extract_units_provider_request
  -> ai.render_extract_units_prompt
  -> ai.ProviderExecutionRequest
  -> ai adapter: DeepSeekExecutionClient
  -> OpenAI SDK-compatible DeepSeek chat.completions.create
  -> ai.ProviderResult
  -> application source binding + typed extraction validation
  -> storage adapters persist AI working artifacts only when called by pipeline
```

DeepSeek-specific code lives only in `src/diamonddust/ai/adapters/deepseek.py`.
The adapter must not construct `KnowledgeUnit`, `Relation`, or
`KnowledgePatch`, and it must not persist artifacts directly.

## Request Mapping

DeepSeek's OpenAI-compatible path maps DiamondDust's provider-neutral payload
into:

- `chat.completions.create`
- `model`: explicit CLI/runtime model
- `messages`: rendered system and user prompt messages
- `response_format`: `{"type": "json_object"}`
- `stream`: `false`
- `base_url`: `https://api.deepseek.com`

The DeepSeek API guide requires the prompt to request JSON output when JSON mode
is used. DiamondDust's `extract_units.v1` prompt already includes JSON output
instructions and the provider-neutral output schema in the prompt package.

Unlike the OpenAI Responses adapter path, this adapter does not rely on
provider-side strict JSON Schema enforcement. DiamondDust typed runtime
validation remains the acceptance boundary.

## Safety Policy

Default behavior:

- no API key value read
- no network call
- no provider call
- no raw request persistence
- no raw response persistence
- no formal vault write

The real execution path requires explicit runtime flags for:

- real provider call approval
- API key value reading approval
- real network call approval
- prompt/source/schema externalization approval
- cost limit and cost approval

The API key environment variable is:

```text
DIAMONDDUST_DEEPSEEK_API_KEY
```

Approving or using this variable name does not mean the key value may be
printed, committed, logged, or persisted.

## Error Mapping

DeepSeek documented status codes map into provider-neutral errors:

- `400`, `422` -> `invalid_request`
- `401` -> `auth_error`
- `402` -> `cost_limit_exceeded`
- `429` -> `rate_limit`
- `500`, `503` -> `provider_server_error`

Other OpenAI-compatible SDK exception class names are normalized through the
same provider-neutral taxonomy.

## CLI

Provider-free commands:

```text
diamonddust deepseek-payload-preview
diamonddust deepseek-dry-run
```

Controlled future real path:

```text
diamonddust deepseek-extract-units
```

The real path remains blocked until all approval flags are present. Validation
for this stage does not execute it against DeepSeek.

## Remaining Decisions Before Any Broader Use

- approved DeepSeek model for live use
- whether real user essays may be externalized
- manual live-smoke scope and cost limit
- whether to keep JSON Output mode or add provider-specific schema prompting
  refinements
- how to evaluate real DeepSeek extraction quality before downstream patch work
