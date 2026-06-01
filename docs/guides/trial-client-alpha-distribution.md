# Trial Client Alpha Distribution

This guide describes how to build and hand off a DiamondDust trial-client alpha
package for a small number of real-note testers.

This is not a stable release, package publication, formal vault write approval,
or recurring provider-use approval.

## Maintainer Build

From the repository root:

```bash
python3 scripts/package-trial-client-alpha.py
```

The script runs the React frontend build and writes:

```text
dist/trial-client-alpha/DiamondDustTrialAlpha-<version>/
dist/trial-client-alpha/DiamondDustTrialAlpha-<version>.zip
```

If the frontend has already been built:

```bash
python3 scripts/package-trial-client-alpha.py --skip-frontend-build
```

## Package Contents

The package intentionally includes only the allowlisted runtime surface:

- Python source under `src/`
- `pyproject.toml`
- root `README.md`
- built React frontend under `frontend/trial-client/dist/`
- Win11 launcher scripts under `scripts/windows/`
- trial-client guides
- generated `START_HERE.md`
- generated `TRIAL_RELEASE_MANIFEST.json`

The package must not include:

- API key values
- `provider-secrets.env`
- `knowledge-vault/`
- `.git/`
- `.venv/`
- `node_modules/`
- raw provider request or response bodies
- historical trial artifacts

## Tester First Run

Requirements:

- Windows 11
- Python 3.11 or newer, including Python 3.13/3.12/3.11. The Win launcher
  checks `py -3.13`, `py -3.12`, `py -3.11`, `py -3`, then `python`.
- Internet access on first start for Python dependency installation and during
  provider extraction calls

For Win11 testers:

1. Unzip the package.
2. Double-click `start-diamonddust-trial.cmd`.
3. Wait for the first launch to create `.venv` and install dependencies.
4. Open the local URL printed by the launcher if the browser does not open
   automatically.
5. In the client, choose a workspace directory such as `C:\DiamondDustTrial`.
6. Save the DeepSeek API key through the client.
7. Import a Markdown note or use files already placed in the workspace input
   directory.
8. Choose `DeepSeek-V4-Flash` or `DeepSeek-V4-Pro`.
9. Run extraction, inspect SourceContext, units, relations, and evidence.
10. Use historical versions from the client instead of regenerating when
   reviewing the same note.
11. Save feedback from the client.

PowerShell users can run:

```powershell
.\start-diamonddust-trial.ps1 -WorkspaceDir C:\DiamondDustTrial
```

If PowerShell script execution is blocked, use the `.cmd` launcher.

If startup fails, the launcher keeps the terminal open and writes diagnostics
to:

```text
<package>/.diamonddust-trial/logs/trial-client-launch.log
```

Common first-run blockers:

- Python 3.11+ is not installed or is not discoverable through `py`/`python`.
- The first-run dependency installation cannot access the Python package index.
- A stale `.venv` was created with an older Python version.

If port `8765` is already in use, the Win launcher automatically tries ports
`8765` through `8775`. To force a port before launch:

```bat
set DIAMONDDUST_TRIAL_PORT=8788
start-diamonddust-trial.cmd
```

## Runtime Boundaries

The trial client remains local-first:

- The backend runs on `127.0.0.1`.
- API key status is shown without returning the key value.
- The Win alpha launchers pass a package-local secret file to the backend:
  `<package>/.diamonddust-trial/secrets/provider-secrets.env`. Do not share the
  unpacked package directory after saving an API key.
- Run settings are stored locally at
  `<package>/.diamonddust-trial/trial-client-settings.json` so the client can
  remember model, timeout, max output, and per-run cost preferences.
- The trial client trims surrounding whitespace before saving or loading the
  local API key value, including quoted values in existing local secret files.
- Provider calls happen only when the user explicitly runs extraction.
- Raw provider request and response bodies are not persisted by default.
- Trial output is written under the selected workspace.
- A local `.venv` may be created inside the package directory on first start.
- Local launch logs may be created inside `.diamonddust-trial/logs/`.
- Formal vault writes, patch acceptance, and publication remain disabled.

## Rebuild Notes

The zip is generated output and should not be committed. To rebuild a package
with a readable version label:

```bash
python3 scripts/package-trial-client-alpha.py --version alpha-2026-05-28
```

Before handing the package to testers, run the normal validation suite and
inspect `TRIAL_RELEASE_MANIFEST.json`.
