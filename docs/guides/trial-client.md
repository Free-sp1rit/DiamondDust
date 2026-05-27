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
- model: `deepseek-chat`

## Scope

The client can:

- list Markdown trial notes
- run one DeepSeek `extract_units` call with explicit safety flags
- show validated extraction artifacts and safety boundaries
- render each unit candidate as structured fields, including `id`, `type`,
  `status`, `confidence`, `source_refs`, `relations`, and expandable
  structured JSON
- mark empty real-note extractions as quality failures
- save feedback Markdown and JSON files

The client must not:

- show or persist API key values
- persist raw provider request or response bodies
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

Only the subprocess environment receives the key value. The browser API returns
only whether the key is present.
