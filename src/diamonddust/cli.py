"""Command-line entry points for local DiamondDust trials."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO

from diamonddust.application import LocalTrialSpec, run_local_trial
from diamonddust.application.blog_draft import BlogMode


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "local-trial":
        return _run_local_trial_command(args, stdout=sys.stdout, stderr=sys.stderr)
    parser.print_help()
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="diamonddust")
    subparsers = parser.add_subparsers(dest="command")

    local_trial = subparsers.add_parser(
        "local-trial",
        help="write inspectable AI working artifacts for one essay",
    )
    local_trial.add_argument("--trial-id", required=True)
    local_trial.add_argument("--essay", required=True)
    local_trial.add_argument("--extraction-json", required=True)
    local_trial.add_argument("--root", default=".")
    local_trial.add_argument("--vault-root", required=True)
    local_trial.add_argument("--title", required=True)
    local_trial.add_argument("--mode", choices=tuple(mode.value for mode in BlogMode), required=True)
    local_trial.add_argument("--audience", required=True)
    local_trial.add_argument("--reader-problem", required=True)
    local_trial.add_argument("--created-at", default=_utc_now())
    local_trial.add_argument("--provider", default="local-trial")
    local_trial.add_argument("--model", default="structured-json")
    local_trial.add_argument("--prompt-version", default="extract_units.v1")
    local_trial.add_argument("--schema-version", default="0.1.0")
    return parser


def _run_local_trial_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        extraction_output = _load_json(args.extraction_json)
        spec = LocalTrialSpec(
            trial_id=args.trial_id,
            essay_path=args.essay,
            extraction_output=extraction_output,
            blog_title=args.title,
            blog_mode=BlogMode(args.mode),
            audience=args.audience,
            reader_problem=args.reader_problem,
            provider=args.provider,
            model=args.model,
            prompt_version=args.prompt_version,
            schema_version=args.schema_version,
        )
        result = run_local_trial(
            spec,
            root=args.root,
            vault_root=args.vault_root,
            created_at=args.created_at,
        )
    except Exception as exc:
        print(f"local trial failed before execution: {exc}", file=stderr)
        return 1

    print(result.summary, file=stdout)
    print(f"source_input_id: {result.source_input_id or 'none'}", file=stdout)
    print(f"patch_id: {result.patch_id or 'none'}", file=stdout)
    print(f"draft_id: {result.draft_id or 'none'}", file=stdout)
    print("formal_write_performed: false", file=stdout)
    print("provider_called: false", file=stdout)
    print("written_paths:", file=stdout)
    if result.written_paths:
        for path in result.written_paths:
            print(f"- {path}", file=stdout)
    else:
        print("- none", file=stdout)

    if result.errors:
        print("errors:", file=stdout)
        for error in result.errors:
            print(f"- {error}", file=stdout)
    return 0 if result.passed else 1


def _load_json(path: str) -> object:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read extraction JSON: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid extraction JSON: {path}") from exc


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
