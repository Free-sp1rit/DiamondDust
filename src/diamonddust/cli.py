"""Command-line entry points for local DiamondDust trials."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from importlib import resources
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import Sequence, TextIO

from diamonddust.application import LocalTrialResult, LocalTrialSpec, run_local_trial
from diamonddust.application.blog_draft import BlogMode


FIXTURE_TRIAL_ID = "trial_fixture_ab12cd"
FIXTURE_SOURCE_PATH = "tests/fixtures/local_trial/trial-essay.md"
FIXTURE_RESOURCE_PACKAGE = "diamonddust.fixtures.local_trial"
FIXTURE_ESSAY_RESOURCE = "trial-essay.md"
FIXTURE_EXTRACTION_RESOURCE = "extraction.json"
FIXTURE_TITLE = "Reviewable Local Trial Artifacts"
FIXTURE_AUDIENCE = "product owner"
FIXTURE_READER_PROBLEM = "inspecting generated artifacts before formal writes"
DEFAULT_VAULT_ROOT = "knowledge-vault"


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "local-trial":
        return _run_local_trial_command(args, stdout=sys.stdout, stderr=sys.stderr)
    if args.command == "local-trial-fixture":
        return _run_local_trial_fixture_command(args, stdout=sys.stdout, stderr=sys.stderr)
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

    fixture_trial = subparsers.add_parser(
        "local-trial-fixture",
        help="run the checked-in provider-free local trial fixture",
    )
    fixture_trial.add_argument("--trial-id", default=FIXTURE_TRIAL_ID)
    fixture_trial.add_argument("--root", default=".")
    fixture_trial.add_argument("--vault-root", default=DEFAULT_VAULT_ROOT)
    fixture_trial.add_argument("--created-at", default=_utc_now())
    return parser


def _run_local_trial_fixture_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        extraction_output = _load_packaged_fixture_json()
        with TemporaryDirectory() as tmp:
            fixture_root = Path(tmp)
            essay_path = fixture_root / FIXTURE_SOURCE_PATH
            essay_path.parent.mkdir(parents=True, exist_ok=True)
            essay_path.write_text(_load_packaged_fixture_text(), encoding="utf-8")

            spec = LocalTrialSpec(
                trial_id=args.trial_id,
                essay_path=FIXTURE_SOURCE_PATH,
                extraction_output=extraction_output,
                blog_title=FIXTURE_TITLE,
                blog_mode=BlogMode.EXPLANATION,
                audience=FIXTURE_AUDIENCE,
                reader_problem=FIXTURE_READER_PROBLEM,
                provider="local-trial",
                model="structured-json",
                prompt_version="extract_units.v1",
                schema_version="0.1.0",
            )
            result = run_local_trial(
                spec,
                root=fixture_root,
                vault_root=args.vault_root,
                created_at=args.created_at,
            )
    except Exception as exc:
        print(f"local trial failed before execution: {exc}", file=stderr)
        return 1

    return _print_local_trial_result(result, stdout=stdout)


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

    return _print_local_trial_result(result, stdout=stdout)


def _print_local_trial_result(result: LocalTrialResult, *, stdout: TextIO) -> int:
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


def _load_packaged_fixture_json() -> object:
    try:
        raw_json = _fixture_resource(FIXTURE_EXTRACTION_RESOURCE).read_text(encoding="utf-8")
        return json.loads(raw_json)
    except OSError as exc:
        raise ValueError("cannot read packaged local trial extraction JSON") from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid packaged local trial extraction JSON") from exc


def _load_packaged_fixture_text() -> str:
    try:
        return _fixture_resource(FIXTURE_ESSAY_RESOURCE).read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError("cannot read packaged local trial essay") from exc


def _fixture_resource(name: str) -> resources.abc.Traversable:
    return resources.files(FIXTURE_RESOURCE_PACKAGE).joinpath(name)


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
