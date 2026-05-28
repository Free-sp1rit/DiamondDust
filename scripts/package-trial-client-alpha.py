#!/usr/bin/env python3
"""Build the DiamondDust trial-client alpha distribution package."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from diamonddust.artifact_time import artifact_timestamp_slug  # noqa: E402
from diamonddust.interface.trial_distribution import (  # noqa: E402
    TrialDistributionConfig,
    build_trial_distribution,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="package-trial-client-alpha")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output-root", default="dist/trial-client-alpha")
    parser.add_argument(
        "--version",
        default=f"alpha-{artifact_timestamp_slug()}",
        help="package version label; defaults to an UTC+8 timestamp slug",
    )
    parser.add_argument(
        "--skip-frontend-build",
        action="store_true",
        help="use the existing frontend dist directory instead of running npm build",
    )
    parser.add_argument(
        "--skip-frontend-dist",
        action="store_true",
        help="build a package without frontend dist assets; intended for diagnostics only",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = repo_root / output_root

    if not args.skip_frontend_build and not args.skip_frontend_dist:
        _run_frontend_build(repo_root)

    result = build_trial_distribution(
        TrialDistributionConfig(
            repo_root=repo_root,
            output_root=output_root,
            version=args.version,
            include_frontend_dist=not args.skip_frontend_dist,
        )
    )
    print(f"package_dir={result.package_dir}")
    print(f"zip_path={result.zip_path}")
    print(f"manifest_path={result.manifest_path}")
    return 0


def _run_frontend_build(repo_root: Path) -> None:
    frontend_root = repo_root / "frontend" / "trial-client"
    subprocess.run(["npm", "run", "build"], cwd=frontend_root, check=True)


if __name__ == "__main__":
    raise SystemExit(main())
