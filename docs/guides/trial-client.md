# Trial Client Guide

The trial client is a local browser interface for a small number of real-note
`extract_units` trials.

## Start

```bash
PYTHONPATH=src .venv/bin/python -m diamonddust trial-client
```

Open:

```text
http://127.0.0.1:8765/
```

Defaults:

- input notes: `knowledge-vault/_manual_trials/deepseek-real-note-evaluation/00-input-notes`
- vault artifacts: `knowledge-vault/`
- feedback artifacts: `knowledge-vault/_manual_trials/trial-client-feedback/`
- secrets env file: `~/.config/diamonddust/provider-secrets.env`
- provider: `deepseek`
- default model: `deepseek-v4-flash`
- model presets: `deepseek-v4-flash`, `deepseek-v4-pro`

## Scope

The client can:

- list Markdown trial notes
- save the DeepSeek API key into the configured local secrets file
- run one DeepSeek `extract_units` call with explicit safety flags
- load existing extraction versions for a note without calling the provider
- delete trial-client generated versions from AI working artifact directories
- show validated extraction artifacts and safety boundaries
- render each unit candidate as structured fields, including `id`, `type`,
  `status`, `confidence`, `source_refs`, `relations`, and expandable structured
  JSON
- collapse source refs as expandable evidence instead of primary review text
- mark empty real-note extractions as quality failures
- save feedback Markdown and JSON files

The client must not:

- show or persist API key values
- persist raw provider request or response bodies
- delete non-trial-client provider artifacts
- delete formal vault files
- generate patches
- record patch acceptance
- formal apply
- publish

## Secret File

The expected local-only file is:

```text
~/.config/diamonddust/provider-secrets.env
```

Expected variable name:

```text
DIAMONDDUST_DEEPSEEK_API_KEY
```

The client can write this variable into the local file for trial convenience.
Status and history APIs return only whether the key is present; they never
return the key value. During extraction, only the subprocess environment
receives the key value.
