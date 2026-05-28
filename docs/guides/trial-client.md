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

Win11 shortcut:

```powershell
.\scripts\windows\start-trial-client.ps1
```

Optional Win11 workspace:

```powershell
.\scripts\windows\start-trial-client.ps1 -WorkspaceDir C:\DiamondDustTrial
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
- configure a local trial workspace
- import Markdown files from the browser into the active input directory
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

## Workspace

The client can switch to a trial workspace from the browser. A workspace
directory creates these local paths:

```text
<workspace>/input-notes/
<workspace>/knowledge-vault/
<workspace>/feedback/
```

Imported Markdown files are written only under the active `input-notes`
directory. Artifact deletion remains limited to trial-client generated AI
working artifacts and does not delete formal vault files.

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

## React Frontend

A maintainable React/Vite frontend lives in:

```text
frontend/trial-client/
```

Development mode:

```bash
PYTHONPATH=src .venv/bin/python -m diamonddust trial-client
cd frontend/trial-client
npm install
npm run dev
```

The Vite dev server proxies `/api` to the Python backend.

Built frontend:

```bash
cd frontend/trial-client
npm run build
cd ../..
PYTHONPATH=src .venv/bin/python -m diamonddust trial-client \
  --frontend-dist frontend/trial-client/dist
```

The Python backend remains the owner of provider execution, artifact loading,
feedback persistence, and safety boundaries. The frontend must not contain
domain validation rules or provider-specific execution logic.
