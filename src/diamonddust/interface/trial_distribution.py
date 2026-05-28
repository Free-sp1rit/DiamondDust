"""Trial-client alpha distribution packaging helpers."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import zipfile

from diamonddust.artifact_time import artifact_now


DEFAULT_TRIAL_PACKAGE_NAME = "DiamondDustTrialAlpha"
TRIAL_DISTRIBUTION_ARTIFACT_TYPE = "trial_client_alpha_distribution"
TRIAL_DISTRIBUTION_SCHEMA_VERSION = "0.1.0"

_VERSION_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
_FORBIDDEN_PATH_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "knowledge-vault",
    "node_modules",
}
_FORBIDDEN_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "provider-secrets.env",
}


class TrialDistributionError(ValueError):
    """Raised when a trial distribution package cannot be created safely."""


@dataclass(frozen=True)
class TrialDistributionConfig:
    repo_root: Path
    output_root: Path
    version: str
    package_name: str = DEFAULT_TRIAL_PACKAGE_NAME
    include_frontend_dist: bool = True
    created_at: str | None = None
    overwrite: bool = True

    def __post_init__(self) -> None:
        _require_directory("repo_root", self.repo_root)
        _require_non_empty("version", self.version)
        if not _VERSION_PATTERN.match(self.version):
            raise TrialDistributionError(
                "version may contain only letters, numbers, '.', '_', and '-'"
            )
        _require_non_empty("package_name", self.package_name)


@dataclass(frozen=True)
class TrialDistributionResult:
    package_dir: Path
    zip_path: Path
    manifest_path: Path
    included_paths: tuple[str, ...]


def trial_distribution_relative_paths(
    *,
    include_frontend_dist: bool = True,
) -> tuple[str, ...]:
    paths = [
        "pyproject.toml",
        "README.md",
        "src",
        "scripts/windows",
        "docs/guides/trial-client.md",
        "docs/guides/trial-client-alpha-distribution.md",
    ]
    if include_frontend_dist:
        paths.append("frontend/trial-client/dist")
    return tuple(paths)


def build_trial_distribution(
    config: TrialDistributionConfig,
) -> TrialDistributionResult:
    repo_root = config.repo_root.resolve()
    output_root = config.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    relative_paths = trial_distribution_relative_paths(
        include_frontend_dist=config.include_frontend_dist
    )
    _require_relative_paths(repo_root, relative_paths)

    package_dir = output_root / f"{config.package_name}-{config.version}"
    if package_dir.exists():
        if not config.overwrite:
            raise TrialDistributionError(f"package directory already exists: {package_dir}")
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    included_paths: list[str] = []
    for relative_path in relative_paths:
        source = repo_root / relative_path
        target = package_dir / relative_path
        _copy_distribution_path(source, target)
        included_paths.append(relative_path)

    _write_package_launchers(package_dir)
    _write_start_here(package_dir, config.version)
    manifest_path = _write_manifest(
        package_dir,
        config=config,
        included_paths=tuple(included_paths),
    )
    _assert_no_forbidden_package_paths(package_dir)
    zip_path = _write_zip(package_dir)

    return TrialDistributionResult(
        package_dir=package_dir,
        zip_path=zip_path,
        manifest_path=manifest_path,
        included_paths=tuple(included_paths),
    )


def _copy_distribution_path(source: Path, target: Path) -> None:
    if source.is_dir():
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns(
                "__pycache__",
                "*.pyc",
                "*.egg-info",
                ".DS_Store",
                "node_modules",
                ".vite",
            ),
        )
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _write_package_launchers(package_dir: Path) -> None:
    (package_dir / "start-diamonddust-trial.cmd").write_text(
        "\n".join(
            [
                "@echo off",
                "setlocal",
                'call "%~dp0scripts\\windows\\start-trial-client.cmd" %*',
                "endlocal",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (package_dir / "start-diamonddust-trial.ps1").write_text(
        "\n".join(
            [
                "param(",
                '    [string]$Port = "8765",',
                '    [string]$WorkspaceDir = "",',
                "    [switch]$NoBrowser",
                ")",
                '$Launcher = Join-Path $PSScriptRoot "scripts\\windows\\start-trial-client.ps1"',
                "& $Launcher -Port $Port -WorkspaceDir $WorkspaceDir -NoBrowser:$NoBrowser",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_start_here(package_dir: Path, version: str) -> None:
    (package_dir / "START_HERE.md").write_text(
        f"""# DiamondDust Trial Alpha

版本：`{version}`

这是面向少量真实用户试用的本地客户端发行包，不是稳定版发布。

## 快速启动（Win11）

前置条件：Windows 11、Python 3.11 或更新版本，并且首次启动时可联网安装依赖。

1. 解压整个目录。
2. 双击 `start-diamonddust-trial.cmd`。
3. 首次启动会在本目录创建 `.venv` 并安装试用依赖。
4. 浏览器打开 `http://127.0.0.1:8765/` 后，在页面中设置试用工作目录。
5. 在客户端保存 DeepSeek API key，导入 Markdown 笔记，选择模型预设并运行。
6. 查看历史产物、删除试用产物或填写反馈时，都在客户端内完成。

PowerShell 用户也可以运行：

```powershell
.\\start-diamonddust-trial.ps1 -WorkspaceDir C:\\DiamondDustTrial
```

## 本地数据边界

- API key 只应保存在本机用户目录的
  `~/.config/diamonddust/provider-secrets.env`。
- 试用产物写入你选择的工作目录。
- 本发行包不包含 API key、`knowledge-vault/`、`.git/`、`.venv/`、
  `node_modules/` 或历史模型调用产物。
- 试用客户端不会 formal apply、不会发布、不会记录 patch acceptance。

更多说明见 `docs/guides/trial-client-alpha-distribution.md`。
""",
        encoding="utf-8",
    )


def _write_manifest(
    package_dir: Path,
    *,
    config: TrialDistributionConfig,
    included_paths: tuple[str, ...],
) -> Path:
    manifest = {
        "artifact_type": TRIAL_DISTRIBUTION_ARTIFACT_TYPE,
        "artifact_schema_version": TRIAL_DISTRIBUTION_SCHEMA_VERSION,
        "package_name": config.package_name,
        "version": config.version,
        "created_at": config.created_at or artifact_now(),
        "include_frontend_dist": config.include_frontend_dist,
        "entrypoints": [
            "start-diamonddust-trial.cmd",
            "start-diamonddust-trial.ps1",
            "scripts/windows/start-trial-client.cmd",
            "scripts/windows/start-trial-client.ps1",
        ],
        "included_paths": included_paths,
        "excluded_by_policy": sorted(_FORBIDDEN_PATH_PARTS | _FORBIDDEN_FILE_NAMES),
        "boundaries": {
            "api_key_values_included": False,
            "knowledge_vault_included": False,
            "node_modules_included": False,
            "venv_included": False,
            "git_history_included": False,
            "raw_provider_request_included": False,
            "raw_provider_response_included": False,
            "formal_write_enabled": False,
            "publication_enabled": False,
        },
    }
    manifest_path = package_dir / "TRIAL_RELEASE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def _write_zip(package_dir: Path) -> Path:
    zip_path = package_dir.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(package_dir.parent))
    return zip_path


def _require_relative_paths(repo_root: Path, relative_paths: tuple[str, ...]) -> None:
    missing = [
        relative_path
        for relative_path in relative_paths
        if not (repo_root / relative_path).exists()
    ]
    if missing:
        raise TrialDistributionError(
            "missing distribution inputs: " + ", ".join(sorted(missing))
        )


def _assert_no_forbidden_package_paths(package_dir: Path) -> None:
    for path in package_dir.rglob("*"):
        relative = path.relative_to(package_dir)
        lower_parts = {part.lower() for part in relative.parts}
        if lower_parts & _FORBIDDEN_PATH_PARTS:
            raise TrialDistributionError(
                f"forbidden runtime path entered package: {relative.as_posix()}"
            )
        if any(part.endswith(".egg-info") for part in lower_parts):
            raise TrialDistributionError(
                f"forbidden build metadata entered package: {relative.as_posix()}"
            )
        if path.name.lower() in _FORBIDDEN_FILE_NAMES:
            raise TrialDistributionError(
                f"forbidden secret file entered package: {relative.as_posix()}"
            )


def _require_directory(name: str, value: Path) -> None:
    if not isinstance(value, Path) or not value.exists() or not value.is_dir():
        raise TrialDistributionError(f"{name} must be an existing directory")


def _require_non_empty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise TrialDistributionError(f"{name} must be a non-empty string")
