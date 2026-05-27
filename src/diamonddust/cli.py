"""Command-line entry points for local DiamondDust trials."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from importlib import resources
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import Sequence, TextIO

from diamonddust.ai import (
    APIKeyEnvVarPolicy,
    CostPolicy,
    EXTRACTION_OUTPUT_SCHEMA_VERSION,
    EXTRACT_UNITS_PROMPT_VERSION,
    ModelPolicy,
    ProviderExecutionRequest,
    RetryPolicy,
    TimeoutPolicy,
    build_provider_execution_payload,
    extraction_output_json_schema,
    render_extract_units_prompt,
)
from diamonddust.ai.adapters.openai import (
    OPENAI_API_KEY_ENV_VAR,
    OPENAI_PROVIDER,
    OpenAIAdapterConfig,
    OpenAIExecutionClient,
    build_openai_dry_run_report,
    build_sanitized_openai_request_preview,
    live_execution_blockers,
)
from diamonddust.ai.adapters.deepseek import (
    DEEPSEEK_API_KEY_ENV_VAR,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_DEFAULT_MAX_TOKENS,
    DEEPSEEK_PROVIDER,
    DeepSeekAdapterConfig,
    DeepSeekExecutionClient,
    build_deepseek_dry_run_report,
    build_sanitized_deepseek_request_preview,
    live_execution_blockers as deepseek_live_execution_blockers,
)
from diamonddust.application import (
    ExtractUnitsProviderRequestSpec,
    LocalTrialResult,
    LocalTrialSpec,
    ProviderIntegrationDecisionSet,
    assess_openai_live_smoke_readiness,
    assess_provider_integration_readiness,
    build_extract_units_provider_request,
    provider_integration_decision_template_mapping,
    provider_integration_decisions_from_mapping,
    render_openai_live_smoke_readiness_markdown,
    render_provider_integration_decision_package_markdown,
    render_provider_integration_escalation_request_markdown,
    render_provider_integration_readiness_markdown,
    run_extract_units_provider_orchestration,
    run_local_trial,
)
from diamonddust.application.blog_draft import BlogMode
from diamonddust.storage import (
    AIRunLogArtifactContext,
    AIRunMetricsScope,
    AIRunOutputArtifact,
    ExtractionArtifactContext,
    read_markdown_essay,
    write_ai_run_log_artifact,
    write_validated_extraction_artifact,
)
from diamonddust.interface.trial_client import (
    DEFAULT_TRIAL_FEEDBACK_DIR,
    DEFAULT_TRIAL_HOST,
    DEFAULT_TRIAL_INPUT_DIR,
    DEFAULT_TRIAL_PORT,
    DEFAULT_TRIAL_SECRETS_ENV_FILE,
    DEFAULT_TRIAL_MODEL,
    TrialClientConfig,
    serve_trial_client,
    trial_client_url,
)


FIXTURE_TRIAL_ID = "trial_fixture_ab12cd"
FIXTURE_SOURCE_PATH = "tests/fixtures/local_trial/trial-essay.md"
FIXTURE_RESOURCE_PACKAGE = "diamonddust.fixtures.local_trial"
FIXTURE_ESSAY_RESOURCE = "trial-essay.md"
FIXTURE_EXTRACTION_RESOURCE = "extraction.json"
FIXTURE_TITLE = "Reviewable Local Trial Artifacts"
FIXTURE_AUDIENCE = "product owner"
FIXTURE_READER_PROBLEM = "inspecting generated artifacts before formal writes"
DEFAULT_VAULT_ROOT = "knowledge-vault"
OPENAI_LIVE_SMOKE_STAGE_LABEL = "first_openai_manual_live_smoke"
OPENAI_LIVE_SMOKE_RUN_SCOPE = "openai_fixture_live_smoke"
OPENAI_LIVE_SMOKE_MODEL = "gpt-5.5"
OPENAI_LIVE_SMOKE_TIMEOUT_SECONDS = 60
OPENAI_LIVE_SMOKE_COST_LIMIT = 1.0
OPENAI_LIVE_SMOKE_RAW_OUTPUT_RETENTION = "hash_and_metadata_only"
OPENAI_LIVE_SMOKE_FIXTURE_SUFFIX = "tests/fixtures/local_trial/trial-essay.md"
OPENAI_LIVE_SMOKE_NOT_VALIDATED = (
    "patch_acceptance",
    "formal_vault_apply",
    "publication",
    "recurring_live_smoke",
    "real_user_essay_externalization",
)
DEEPSEEK_RUN_STAGE_LABEL = "deepseek_manual_extract_units"
DEEPSEEK_RUN_SCOPE = "deepseek_extract_units_manual"
DEEPSEEK_RAW_OUTPUT_RETENTION = "hash_and_metadata_only"
DEEPSEEK_NOT_VALIDATED = (
    "patch_acceptance",
    "formal_vault_apply",
    "publication",
    "recurring_live_smoke",
    "provider_output_quality_acceptance",
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "local-trial":
        return _run_local_trial_command(args, stdout=sys.stdout, stderr=sys.stderr)
    if args.command == "local-trial-fixture":
        return _run_local_trial_fixture_command(args, stdout=sys.stdout, stderr=sys.stderr)
    if args.command == "provider-readiness-report":
        return _run_provider_readiness_report_command(
            args,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    if args.command == "provider-escalation-request":
        return _run_provider_escalation_request_command(
            args,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    if args.command == "provider-decisions-template":
        return _run_provider_decisions_template_command(stdout=sys.stdout)
    if args.command == "provider-decision-package":
        return _run_provider_decision_package_command(
            args,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    if args.command == "openai-live-smoke-readiness":
        return _run_openai_live_smoke_readiness_command(
            args,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    if args.command == "extraction-output-schema":
        return _run_extraction_output_schema_command(stdout=sys.stdout)
    if args.command == "provider-payload-preview":
        return _run_provider_payload_preview_command(
            args,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    if args.command == "openai-payload-preview":
        return _run_openai_payload_preview_command(
            args,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    if args.command == "openai-dry-run":
        return _run_openai_dry_run_command(
            args,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    if args.command == "openai-extract-units":
        return _run_openai_extract_units_command(
            args,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    if args.command == "deepseek-payload-preview":
        return _run_deepseek_payload_preview_command(
            args,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    if args.command == "deepseek-dry-run":
        return _run_deepseek_dry_run_command(
            args,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    if args.command == "deepseek-extract-units":
        return _run_deepseek_extract_units_command(
            args,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    if args.command == "trial-client":
        return _run_trial_client_command(
            args,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
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

    provider_readiness = subparsers.add_parser(
        "provider-readiness-report",
        help="render a provider integration readiness report without provider calls",
    )
    _add_provider_readiness_arguments(provider_readiness)

    provider_escalation = subparsers.add_parser(
        "provider-escalation-request",
        help="render a first-provider escalation request draft without provider calls",
    )
    _add_provider_readiness_arguments(provider_escalation)

    subparsers.add_parser(
        "provider-decisions-template",
        help="print a provider decisions JSON template without provider calls",
    )

    provider_decision_package = subparsers.add_parser(
        "provider-decision-package",
        help="render one provider decision review package without provider calls",
    )
    _add_provider_readiness_arguments(provider_decision_package)

    openai_live_smoke_readiness = subparsers.add_parser(
        "openai-live-smoke-readiness",
        help="render OpenAI live-smoke readiness without key reads or provider calls",
    )
    _add_provider_readiness_arguments(openai_live_smoke_readiness)

    subparsers.add_parser(
        "extraction-output-schema",
        help="print the extract_units output JSON Schema without provider calls",
    )

    provider_payload_preview = subparsers.add_parser(
        "provider-payload-preview",
        help=(
            "print the provider-neutral extract_units execution payload "
            "without provider calls"
        ),
    )
    provider_payload_preview.add_argument("--essay", required=True)
    provider_payload_preview.add_argument("--run-id", required=True)
    provider_payload_preview.add_argument("--root")
    provider_payload_preview.add_argument("--provider", default="preview-provider")
    provider_payload_preview.add_argument(
        "--model",
        default="preview-structured-model",
    )
    provider_payload_preview.add_argument(
        "--prompt-version",
        default=EXTRACT_UNITS_PROMPT_VERSION,
    )
    provider_payload_preview.add_argument(
        "--schema-version",
        default=EXTRACTION_OUTPUT_SCHEMA_VERSION,
    )
    provider_payload_preview.add_argument("--timeout-seconds", type=int)
    provider_payload_preview.add_argument("--max-retries", type=int, default=0)

    openai_payload_preview = subparsers.add_parser(
        "openai-payload-preview",
        help=(
            "print a sanitized OpenAI extract_units request preview "
            "without key reads or provider calls"
        ),
    )
    _add_openai_extract_arguments(openai_payload_preview)

    openai_dry_run = subparsers.add_parser(
        "openai-dry-run",
        help=(
            "check the future OpenAI extract_units path without key reads "
            "or provider calls"
        ),
    )
    _add_openai_extract_arguments(openai_dry_run)

    openai_extract_units = subparsers.add_parser(
        "openai-extract-units",
        help=(
            "controlled OpenAI extract_units live-smoke path; blocked by "
            "default before key reads or provider calls"
        ),
    )
    _add_openai_extract_arguments(openai_extract_units)
    openai_extract_units.add_argument("--vault-root", default=DEFAULT_VAULT_ROOT)
    openai_extract_units.add_argument("--created-at", default=_utc_now())
    openai_extract_units.add_argument(
        "--real-provider-call-approved",
        action="store_true",
        help="enable the real-provider request flag for the approved smoke",
    )
    openai_extract_units.add_argument(
        "--api-key-value-reading-approved",
        action="store_true",
        help="allow key reading only inside the approved live-smoke path",
    )
    openai_extract_units.add_argument(
        "--real-network-call-approved",
        action="store_true",
        help="allow network execution only for the approved live smoke",
    )
    openai_extract_units.add_argument(
        "--live-smoke-approved",
        action="store_true",
        help="record one-manual-live-smoke approval for this invocation",
    )
    openai_extract_units.add_argument(
        "--prompt-source-schema-externalization-approved",
        action="store_true",
        help="allow fixture prompt/source/schema externalization for this smoke",
    )
    openai_extract_units.add_argument("--cost-limit", type=float)
    openai_extract_units.add_argument("--cost-limit-approved", action="store_true")
    openai_extract_units.add_argument(
        "--raw-output-retention",
        default="hash_and_metadata_only",
    )

    deepseek_payload_preview = subparsers.add_parser(
        "deepseek-payload-preview",
        help=(
            "print a sanitized DeepSeek extract_units request preview "
            "without key reads or provider calls"
        ),
    )
    _add_deepseek_extract_arguments(deepseek_payload_preview)

    deepseek_dry_run = subparsers.add_parser(
        "deepseek-dry-run",
        help=(
            "check the future DeepSeek extract_units path without key reads "
            "or provider calls"
        ),
    )
    _add_deepseek_extract_arguments(deepseek_dry_run)

    deepseek_extract_units = subparsers.add_parser(
        "deepseek-extract-units",
        help=(
            "controlled DeepSeek extract_units path; blocked by default "
            "before key reads or provider calls"
        ),
    )
    _add_deepseek_extract_arguments(deepseek_extract_units)
    deepseek_extract_units.add_argument("--vault-root", default=DEFAULT_VAULT_ROOT)
    deepseek_extract_units.add_argument("--created-at", default=_utc_now())
    deepseek_extract_units.add_argument(
        "--real-provider-call-approved",
        action="store_true",
        help="enable the real-provider request flag for this invocation",
    )
    deepseek_extract_units.add_argument(
        "--api-key-value-reading-approved",
        action="store_true",
        help="allow DeepSeek key reading only in the approved real path",
    )
    deepseek_extract_units.add_argument(
        "--real-network-call-approved",
        action="store_true",
        help="allow DeepSeek network execution for this invocation",
    )
    deepseek_extract_units.add_argument(
        "--prompt-source-schema-externalization-approved",
        action="store_true",
        help="allow prompt/source/schema externalization for this invocation",
    )
    deepseek_extract_units.add_argument("--cost-limit", type=float)
    deepseek_extract_units.add_argument("--cost-limit-approved", action="store_true")
    deepseek_extract_units.add_argument(
        "--raw-output-retention",
        default=DEEPSEEK_RAW_OUTPUT_RETENTION,
    )

    trial_client = subparsers.add_parser(
        "trial-client",
        help="start the local browser client for real-note extraction trials",
    )
    trial_client.add_argument("--host", default=DEFAULT_TRIAL_HOST)
    trial_client.add_argument("--port", type=int, default=DEFAULT_TRIAL_PORT)
    trial_client.add_argument("--root", default=".")
    trial_client.add_argument("--input-dir", default=DEFAULT_TRIAL_INPUT_DIR)
    trial_client.add_argument("--vault-root", default=DEFAULT_VAULT_ROOT)
    trial_client.add_argument("--feedback-dir", default=DEFAULT_TRIAL_FEEDBACK_DIR)
    trial_client.add_argument(
        "--secrets-env-file",
        default=DEFAULT_TRIAL_SECRETS_ENV_FILE,
    )
    trial_client.add_argument("--model", default=DEFAULT_TRIAL_MODEL)
    trial_client.add_argument("--timeout-seconds", type=int, default=60)
    trial_client.add_argument(
        "--max-tokens",
        type=int,
        default=DEEPSEEK_DEFAULT_MAX_TOKENS,
    )
    trial_client.add_argument("--cost-limit", type=float, default=1.0)
    return parser


def _add_openai_extract_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--essay", required=True)
    command.add_argument("--run-id", required=True)
    command.add_argument("--model", required=True)
    command.add_argument("--root")
    command.add_argument("--api-key-env-var", default=OPENAI_API_KEY_ENV_VAR)
    command.add_argument(
        "--prompt-version",
        default=EXTRACT_UNITS_PROMPT_VERSION,
    )
    command.add_argument(
        "--schema-version",
        default=EXTRACTION_OUTPUT_SCHEMA_VERSION,
    )
    command.add_argument("--timeout-seconds", type=int, default=30)
    command.add_argument("--max-retries", type=int, default=0)


def _add_deepseek_extract_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--essay", required=True)
    command.add_argument("--run-id", required=True)
    command.add_argument("--model", required=True)
    command.add_argument("--root")
    command.add_argument("--api-key-env-var", default=DEEPSEEK_API_KEY_ENV_VAR)
    command.add_argument("--base-url", default=DEEPSEEK_BASE_URL)
    command.add_argument(
        "--prompt-version",
        default=EXTRACT_UNITS_PROMPT_VERSION,
    )
    command.add_argument(
        "--schema-version",
        default=EXTRACTION_OUTPUT_SCHEMA_VERSION,
    )
    command.add_argument("--timeout-seconds", type=int, default=30)
    command.add_argument("--max-retries", type=int, default=0)
    command.add_argument("--max-tokens", type=int, default=DEEPSEEK_DEFAULT_MAX_TOKENS)


def _add_provider_readiness_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--decisions-json")
    command.add_argument("--first-provider")
    command.add_argument("--default-model")
    command.add_argument("--provider-sdk-dependency")
    command.add_argument(
        "--provider-sdk-dependency-approved",
        action="store_true",
    )
    command.add_argument("--api-key-env-var")
    command.add_argument("--api-key-env-var-approved", action="store_true")
    command.add_argument("--api-key-value-reading-approved", action="store_true")
    command.add_argument(
        "--real-provider-calls-approved",
        action="store_true",
    )
    command.add_argument(
        "--real-network-calls-approved",
        action="store_true",
    )
    command.add_argument(
        "--prompt-text-external-approved",
        action="store_true",
    )
    command.add_argument("--source-body-external-approved", action="store_true")
    command.add_argument(
        "--output-schema-external-approved",
        "--schema-external-approved",
        dest="output_schema_external_approved",
        action="store_true",
    )
    command.add_argument("--structured-output-mechanism")
    command.add_argument(
        "--structured-output-mechanism-approved",
        action="store_true",
    )
    command.add_argument("--cost-limit", type=float)
    command.add_argument("--cost-limit-approved", action="store_true")
    command.add_argument("--timeout-seconds", type=int)
    command.add_argument("--timeout-policy-approved", action="store_true")
    command.add_argument("--max-retries", type=int)
    command.add_argument("--retry-policy-approved", action="store_true")
    command.add_argument("--raw-output-retention")
    command.add_argument(
        "--raw-output-retention-approved",
        action="store_true",
    )
    command.add_argument("--fallback-behavior")
    command.add_argument("--fallback-behavior-approved", action="store_true")
    command.add_argument("--manual-live-smoke-approved", action="store_true")
    command.add_argument("--recurring-live-smoke-approved", action="store_true")


def _run_provider_readiness_report_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        decisions = _provider_decisions_from_args(args)
        report = assess_provider_integration_readiness(decisions)
        stdout.write(render_provider_integration_readiness_markdown(report))
    except Exception as exc:
        print(f"provider readiness report failed: {exc}", file=stderr)
        return 1
    return 0


def _run_provider_escalation_request_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        decisions = _provider_decisions_from_args(args)
        report = assess_provider_integration_readiness(decisions)
        stdout.write(render_provider_integration_escalation_request_markdown(report))
    except Exception as exc:
        print(f"provider escalation request failed: {exc}", file=stderr)
        return 1
    return 0


def _run_provider_decisions_template_command(*, stdout: TextIO) -> int:
    stdout.write(
        json.dumps(
            provider_integration_decision_template_mapping(),
            indent=2,
            sort_keys=True,
        )
    )
    stdout.write("\n")
    return 0


def _run_provider_decision_package_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        decisions = _provider_decisions_from_args(args)
        report = assess_provider_integration_readiness(decisions)
        stdout.write(render_provider_integration_decision_package_markdown(report))
    except Exception as exc:
        print(f"provider decision package failed: {exc}", file=stderr)
        return 1
    return 0


def _run_openai_live_smoke_readiness_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        decisions = _provider_decisions_from_args(args)
        report = assess_openai_live_smoke_readiness(decisions)
        stdout.write(render_openai_live_smoke_readiness_markdown(report))
    except Exception as exc:
        print(f"OpenAI live smoke readiness failed: {exc}", file=stderr)
        return 1
    return 0


def _run_extraction_output_schema_command(*, stdout: TextIO) -> int:
    stdout.write(
        json.dumps(
            extraction_output_json_schema(),
            indent=2,
            sort_keys=True,
        )
    )
    stdout.write("\n")
    return 0


def _run_provider_payload_preview_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        essay = read_markdown_essay(args.essay, root=args.root)
        provider_request = build_extract_units_provider_request(
            essay,
            ExtractUnitsProviderRequestSpec(
                run_id=args.run_id,
                provider=args.provider,
                model=args.model,
                prompt_version=args.prompt_version,
                schema_version=args.schema_version,
                timeout_seconds=args.timeout_seconds,
                max_retries=args.max_retries,
            ),
        )
        rendered_prompt = render_extract_units_prompt(provider_request)
        execution_request = ProviderExecutionRequest(
            provider_request=provider_request,
            rendered_prompt=rendered_prompt,
        )
        payload = build_provider_execution_payload(execution_request)
        stdout.write(
            json.dumps(
                payload.to_mapping(),
                indent=2,
                sort_keys=True,
            )
        )
        stdout.write("\n")
    except Exception as exc:
        print(f"provider payload preview failed: {exc}", file=stderr)
        return 1
    return 0


def _run_openai_payload_preview_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        execution_request = _build_openai_execution_request_from_args(
            args,
            real_provider_calls_enabled=False,
        )
        config = _openai_config_from_args(args)
        preview = build_sanitized_openai_request_preview(
            execution_request,
            config=config,
        )
        stdout.write(json.dumps(preview, indent=2, sort_keys=True))
        stdout.write("\n")
    except Exception as exc:
        print(f"OpenAI payload preview failed: {exc}", file=stderr)
        return 1
    return 0


def _run_openai_dry_run_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        execution_request = _build_openai_execution_request_from_args(
            args,
            real_provider_calls_enabled=False,
        )
        config = _openai_config_from_args(args)
        report = build_openai_dry_run_report(execution_request, config=config)
        stdout.write(json.dumps(report, indent=2, sort_keys=True))
        stdout.write("\n")
    except Exception as exc:
        print(f"OpenAI dry run failed: {exc}", file=stderr)
        return 1
    return 0


def _run_openai_extract_units_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        config = _openai_config_from_args(args)
        if _openai_live_execution_requested(args):
            return _run_openai_live_extract_units_command(
                args,
                config=config,
                stdout=stdout,
            )

        execution_request = _build_openai_execution_request_from_args(
            args,
            real_provider_calls_enabled=False,
        )
        result = OpenAIExecutionClient(config=config).generate(execution_request)
        output: dict[str, object] = {
            "command": "openai-extract-units",
            "provider": OPENAI_PROVIDER,
            "run_id": execution_request.provider_request.run_id,
            "requested_real_provider_call": args.real_provider_call_approved,
            "succeeded": result.succeeded,
            "provider_called": False,
            "network_call": False,
            "api_key_value_read": False,
            "raw_provider_request_persisted": False,
            "raw_provider_response_persisted": False,
            "blockers": list(live_execution_blockers(execution_request, config)),
        }
        if result.error is not None:
            output["error"] = dict(result.error.to_mapping())
        if result.response is not None:
            output["provider_request_id"] = result.response.provider_request_id
            output["output_hash"] = result.response.output_hash
            output["raw_output_persisted"] = result.response.raw_output_persisted
        stdout.write(json.dumps(output, indent=2, sort_keys=True))
        stdout.write("\n")
    except Exception as exc:
        print(f"OpenAI extract_units failed before execution: {exc}", file=stderr)
        return 1
    return 0 if result.succeeded else 1


def _run_openai_live_extract_units_command(
    args: argparse.Namespace,
    *,
    config: OpenAIAdapterConfig,
    stdout: TextIO,
) -> int:
    preflight_blockers = _openai_live_smoke_preflight_blockers(args)
    if preflight_blockers:
        stdout.write(
            json.dumps(
                {
                    "command": "openai-extract-units",
                    "stage_label": OPENAI_LIVE_SMOKE_STAGE_LABEL,
                    "provider": OPENAI_PROVIDER,
                    "run_id": args.run_id,
                    "succeeded": False,
                    "provider_called": False,
                    "network_call": False,
                    "api_key_value_read": False,
                    "raw_provider_request_persisted": False,
                    "raw_provider_response_persisted": False,
                    "blockers": preflight_blockers,
                },
                indent=2,
                sort_keys=True,
            )
        )
        stdout.write("\n")
        return 1

    if not os.environ.get(config.api_key_env_var):
        stdout.write(
            json.dumps(
                {
                    "command": "openai-extract-units",
                    "stage_label": OPENAI_LIVE_SMOKE_STAGE_LABEL,
                    "provider": OPENAI_PROVIDER,
                    "run_id": args.run_id,
                    "succeeded": False,
                    "provider_called": False,
                    "network_call": False,
                    "api_key_value_read": True,
                    "raw_provider_request_persisted": False,
                    "raw_provider_response_persisted": False,
                    "blockers": [
                        "approved API key environment variable is not set"
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
        stdout.write("\n")
        return 1

    essay = read_markdown_essay(args.essay, root=args.root)
    spec = ExtractUnitsProviderRequestSpec(
        run_id=args.run_id,
        provider=OPENAI_PROVIDER,
        model=args.model,
        prompt_version=args.prompt_version,
        schema_version=args.schema_version,
        timeout_seconds=args.timeout_seconds,
        max_retries=args.max_retries,
        real_provider_calls_enabled=args.real_provider_call_approved,
    )
    provider = OpenAIExecutionClient(config=config)
    orchestration = run_extract_units_provider_orchestration(
        provider,
        essay,
        spec,
        model_policy=_openai_live_model_policy(args),
    )
    artifacts = _persist_openai_live_smoke_artifacts(
        orchestration,
        vault_root=args.vault_root,
        created_at=args.created_at,
    )
    result = orchestration.extraction_run.provider_result
    output: dict[str, object] = {
        "command": "openai-extract-units",
        "stage_label": OPENAI_LIVE_SMOKE_STAGE_LABEL,
        "provider": OPENAI_PROVIDER,
        "run_id": orchestration.request.run_id,
        "source_input_id": orchestration.rendered_prompt.source_input_id,
        "requested_real_provider_call": args.real_provider_call_approved,
        "live_smoke_approved": args.live_smoke_approved,
        "succeeded": orchestration.is_valid,
        "provider_called": True,
        "network_call": True,
        "api_key_value_read": True,
        "raw_provider_request_persisted": False,
        "raw_provider_response_persisted": False,
        "prompt_hash": orchestration.rendered_prompt.prompt_hash,
        "output_hash": orchestration.run_log.output_hash,
        "validation_status": orchestration.run_log.validation_status.value,
        "errors": list(orchestration.errors),
        "written_paths": artifacts,
        "formal_write_performed": False,
        "patch_acceptance": False,
        "publication_performed": False,
    }
    if result.response is not None:
        output["provider_request_id"] = result.response.provider_request_id
        output["raw_output_persisted"] = result.response.raw_output_persisted
    if result.error is not None:
        output["error"] = dict(result.error.to_mapping())
    stdout.write(json.dumps(output, indent=2, sort_keys=True))
    stdout.write("\n")
    return 0 if orchestration.is_valid else 1


def _build_openai_execution_request_from_args(
    args: argparse.Namespace,
    *,
    real_provider_calls_enabled: bool,
) -> ProviderExecutionRequest:
    essay = read_markdown_essay(args.essay, root=args.root)
    provider_request = build_extract_units_provider_request(
        essay,
        ExtractUnitsProviderRequestSpec(
            run_id=args.run_id,
            provider=OPENAI_PROVIDER,
            model=args.model,
            prompt_version=args.prompt_version,
            schema_version=args.schema_version,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            real_provider_calls_enabled=real_provider_calls_enabled,
        ),
    )
    rendered_prompt = render_extract_units_prompt(provider_request)
    return ProviderExecutionRequest(
        provider_request=provider_request,
        rendered_prompt=rendered_prompt,
    )


def _openai_config_from_args(args: argparse.Namespace) -> OpenAIAdapterConfig:
    return OpenAIAdapterConfig(
        api_key_env_var=args.api_key_env_var,
        timeout_seconds=args.timeout_seconds,
        max_retries=args.max_retries,
        api_key_value_reading_approved=getattr(
            args,
            "api_key_value_reading_approved",
            False,
        ),
        real_provider_calls_approved=getattr(
            args,
            "real_provider_call_approved",
            False,
        ),
        real_network_calls_approved=getattr(
            args,
            "real_network_call_approved",
            False,
        ),
        live_smoke_approved=getattr(args, "live_smoke_approved", False),
        prompt_source_schema_externalization_approved=getattr(
            args,
            "prompt_source_schema_externalization_approved",
            False,
        ),
        cost_limit=getattr(args, "cost_limit", None),
        cost_limit_approved=getattr(args, "cost_limit_approved", False),
    )


def _openai_live_execution_requested(args: argparse.Namespace) -> bool:
    return any(
        (
            getattr(args, "api_key_value_reading_approved", False),
            getattr(args, "real_network_call_approved", False),
            getattr(args, "live_smoke_approved", False),
            getattr(args, "prompt_source_schema_externalization_approved", False),
            getattr(args, "cost_limit_approved", False),
        )
    )


def _openai_live_smoke_preflight_blockers(args: argparse.Namespace) -> list[str]:
    blockers: list[str] = []
    if args.model != OPENAI_LIVE_SMOKE_MODEL:
        blockers.append(f"model must be {OPENAI_LIVE_SMOKE_MODEL}")
    if args.api_key_env_var != OPENAI_API_KEY_ENV_VAR:
        blockers.append(f"api_key_env_var must be {OPENAI_API_KEY_ENV_VAR}")
    if args.timeout_seconds != OPENAI_LIVE_SMOKE_TIMEOUT_SECONDS:
        blockers.append(
            f"timeout_seconds must be {OPENAI_LIVE_SMOKE_TIMEOUT_SECONDS}"
        )
    if args.max_retries != 0:
        blockers.append("max_retries must be 0")
    if args.cost_limit != OPENAI_LIVE_SMOKE_COST_LIMIT:
        blockers.append(f"cost_limit must be {OPENAI_LIVE_SMOKE_COST_LIMIT}")
    if args.raw_output_retention != OPENAI_LIVE_SMOKE_RAW_OUTPUT_RETENTION:
        blockers.append(
            "raw_output_retention must be "
            f"{OPENAI_LIVE_SMOKE_RAW_OUTPUT_RETENTION}"
        )
    if not Path(args.essay).as_posix().endswith(OPENAI_LIVE_SMOKE_FIXTURE_SUFFIX):
        blockers.append(
            f"essay must be the approved fixture {OPENAI_LIVE_SMOKE_FIXTURE_SUFFIX}"
        )
    required_flags = {
        "real_provider_call_approved": args.real_provider_call_approved,
        "api_key_value_reading_approved": args.api_key_value_reading_approved,
        "real_network_call_approved": args.real_network_call_approved,
        "live_smoke_approved": args.live_smoke_approved,
        "prompt_source_schema_externalization_approved": (
            args.prompt_source_schema_externalization_approved
        ),
        "cost_limit_approved": args.cost_limit_approved,
    }
    for name, approved in required_flags.items():
        if not approved:
            blockers.append(f"{name} must be approved")
    return blockers


def _openai_live_model_policy(args: argparse.Namespace) -> ModelPolicy:
    return ModelPolicy(
        first_provider=OPENAI_PROVIDER,
        real_provider_calls_approved=args.real_provider_call_approved,
        api_key_env_var_policy=APIKeyEnvVarPolicy(
            env_var_name=args.api_key_env_var,
            read_allowed=args.api_key_value_reading_approved,
        ),
        retry_policy=RetryPolicy(max_retries=args.max_retries),
        timeout_policy=TimeoutPolicy(
            default_timeout_seconds=args.timeout_seconds,
            maximum_timeout_seconds=args.timeout_seconds,
        ),
        cost_policy=CostPolicy(cost_limit=args.cost_limit),
    )


def _persist_openai_live_smoke_artifacts(
    orchestration,
    *,
    vault_root: str,
    created_at: str,
) -> list[str]:
    extraction_artifact_path: str | None = None
    if orchestration.validation_result.proposal is not None:
        extraction_artifact = write_validated_extraction_artifact(
            orchestration.validation_result.proposal,
            vault_root=vault_root,
            created_at=created_at,
            context=ExtractionArtifactContext(
                stage_label=OPENAI_LIVE_SMOKE_STAGE_LABEL,
                run_scope=OPENAI_LIVE_SMOKE_RUN_SCOPE,
                real_provider_call=True,
                fixture_driven=True,
                prompt_hash=orchestration.rendered_prompt.prompt_hash,
                not_validated=OPENAI_LIVE_SMOKE_NOT_VALIDATED,
            ),
        )
        extraction_artifact_path = extraction_artifact.relative_path

    run_log_artifact = write_ai_run_log_artifact(
        orchestration.run_log,
        vault_root=vault_root,
        created_at=created_at,
        context=_openai_live_run_log_context(
            orchestration,
            extraction_artifact_path=extraction_artifact_path,
        ),
    )
    paths = [run_log_artifact.relative_path]
    if extraction_artifact_path is not None:
        paths.insert(0, extraction_artifact_path)
    return paths


def _openai_live_run_log_context(
    orchestration,
    *,
    extraction_artifact_path: str | None,
) -> AIRunLogArtifactContext:
    base = orchestration.run_log_context
    output_artifacts = ()
    if extraction_artifact_path is not None:
        output_artifacts = (
            AIRunOutputArtifact(
                artifact_type="validated_extraction_output",
                path=extraction_artifact_path,
            ),
        )
    return AIRunLogArtifactContext(
        stage_label=OPENAI_LIVE_SMOKE_STAGE_LABEL,
        run_scope=OPENAI_LIVE_SMOKE_RUN_SCOPE,
        real_provider_call=True,
        fixture_driven=True,
        prompt_used=True,
        metrics_scope=AIRunMetricsScope(
            cost_applicable=True,
            latency_applicable=True,
            reason=OPENAI_LIVE_SMOKE_RUN_SCOPE,
        ),
        source_input_id=orchestration.rendered_prompt.source_input_id,
        prompt_hash=orchestration.rendered_prompt.prompt_hash,
        output_artifacts=output_artifacts,
        not_validated=OPENAI_LIVE_SMOKE_NOT_VALIDATED,
        provider_request_id=base.provider_request_id,
        retry_count=base.retry_count,
        token_usage=base.token_usage,
    )


def _run_deepseek_payload_preview_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        execution_request = _build_deepseek_execution_request_from_args(
            args,
            real_provider_calls_enabled=False,
        )
        config = _deepseek_config_from_args(args)
        preview = build_sanitized_deepseek_request_preview(
            execution_request,
            config=config,
        )
        stdout.write(json.dumps(preview, indent=2, sort_keys=True))
        stdout.write("\n")
    except Exception as exc:
        print(f"DeepSeek payload preview failed: {exc}", file=stderr)
        return 1
    return 0


def _run_deepseek_dry_run_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        execution_request = _build_deepseek_execution_request_from_args(
            args,
            real_provider_calls_enabled=False,
        )
        config = _deepseek_config_from_args(args)
        report = build_deepseek_dry_run_report(execution_request, config=config)
        stdout.write(json.dumps(report, indent=2, sort_keys=True))
        stdout.write("\n")
    except Exception as exc:
        print(f"DeepSeek dry run failed: {exc}", file=stderr)
        return 1
    return 0


def _run_deepseek_extract_units_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        config = _deepseek_config_from_args(args)
        if _deepseek_live_execution_requested(args):
            return _run_deepseek_live_extract_units_command(
                args,
                config=config,
                stdout=stdout,
            )

        execution_request = _build_deepseek_execution_request_from_args(
            args,
            real_provider_calls_enabled=False,
        )
        result = DeepSeekExecutionClient(config=config).generate(execution_request)
        output: dict[str, object] = {
            "command": "deepseek-extract-units",
            "provider": DEEPSEEK_PROVIDER,
            "run_id": execution_request.provider_request.run_id,
            "requested_real_provider_call": args.real_provider_call_approved,
            "succeeded": result.succeeded,
            "provider_called": False,
            "network_call": False,
            "api_key_value_read": False,
            "raw_provider_request_persisted": False,
            "raw_provider_response_persisted": False,
            "blockers": list(
                deepseek_live_execution_blockers(execution_request, config)
            ),
        }
        if result.error is not None:
            output["error"] = dict(result.error.to_mapping())
        if result.response is not None:
            output["provider_request_id"] = result.response.provider_request_id
            output["output_hash"] = result.response.output_hash
            output["raw_output_persisted"] = result.response.raw_output_persisted
        stdout.write(json.dumps(output, indent=2, sort_keys=True))
        stdout.write("\n")
    except Exception as exc:
        print(f"DeepSeek extract_units failed before execution: {exc}", file=stderr)
        return 1
    return 0 if result.succeeded else 1


def _run_trial_client_command(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        config = TrialClientConfig(
            host=args.host,
            port=args.port,
            root=Path(args.root),
            input_dir=Path(args.input_dir),
            vault_root=Path(args.vault_root),
            feedback_dir=Path(args.feedback_dir),
            secrets_env_file=Path(args.secrets_env_file).expanduser(),
            default_model=args.model,
            timeout_seconds=args.timeout_seconds,
            max_tokens=args.max_tokens,
            cost_limit=args.cost_limit,
        )
    except Exception as exc:
        print(f"trial client configuration failed: {exc}", file=stderr)
        return 1

    stdout.write(f"DiamondDust trial client: {trial_client_url(config)}\n")
    stdout.flush()
    try:
        serve_trial_client(config)
    except KeyboardInterrupt:
        stdout.write("\ntrial client stopped\n")
        return 0
    except Exception as exc:
        print(f"trial client failed: {exc}", file=stderr)
        return 1
    return 0


def _run_deepseek_live_extract_units_command(
    args: argparse.Namespace,
    *,
    config: DeepSeekAdapterConfig,
    stdout: TextIO,
) -> int:
    preflight_blockers = _deepseek_preflight_blockers(args)
    if preflight_blockers:
        stdout.write(
            json.dumps(
                {
                    "command": "deepseek-extract-units",
                    "stage_label": DEEPSEEK_RUN_STAGE_LABEL,
                    "provider": DEEPSEEK_PROVIDER,
                    "run_id": args.run_id,
                    "succeeded": False,
                    "provider_called": False,
                    "network_call": False,
                    "api_key_value_read": False,
                    "raw_provider_request_persisted": False,
                    "raw_provider_response_persisted": False,
                    "blockers": preflight_blockers,
                },
                indent=2,
                sort_keys=True,
            )
        )
        stdout.write("\n")
        return 1

    if not os.environ.get(config.api_key_env_var):
        stdout.write(
            json.dumps(
                {
                    "command": "deepseek-extract-units",
                    "stage_label": DEEPSEEK_RUN_STAGE_LABEL,
                    "provider": DEEPSEEK_PROVIDER,
                    "run_id": args.run_id,
                    "succeeded": False,
                    "provider_called": False,
                    "network_call": False,
                    "api_key_value_read": True,
                    "raw_provider_request_persisted": False,
                    "raw_provider_response_persisted": False,
                    "blockers": [
                        "approved API key environment variable is not set"
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
        stdout.write("\n")
        return 1

    essay = read_markdown_essay(args.essay, root=args.root)
    spec = ExtractUnitsProviderRequestSpec(
        run_id=args.run_id,
        provider=DEEPSEEK_PROVIDER,
        model=args.model,
        prompt_version=args.prompt_version,
        schema_version=args.schema_version,
        timeout_seconds=args.timeout_seconds,
        max_retries=args.max_retries,
        real_provider_calls_enabled=args.real_provider_call_approved,
    )
    provider = DeepSeekExecutionClient(config=config)
    orchestration = run_extract_units_provider_orchestration(
        provider,
        essay,
        spec,
        model_policy=_deepseek_model_policy(args),
    )
    artifacts = _persist_deepseek_artifacts(
        orchestration,
        vault_root=args.vault_root,
        created_at=args.created_at,
    )
    result = orchestration.extraction_run.provider_result
    output: dict[str, object] = {
        "command": "deepseek-extract-units",
        "stage_label": DEEPSEEK_RUN_STAGE_LABEL,
        "provider": DEEPSEEK_PROVIDER,
        "run_id": orchestration.request.run_id,
        "source_input_id": orchestration.rendered_prompt.source_input_id,
        "requested_real_provider_call": args.real_provider_call_approved,
        "succeeded": orchestration.is_valid,
        "provider_called": True,
        "network_call": True,
        "api_key_value_read": True,
        "raw_provider_request_persisted": False,
        "raw_provider_response_persisted": False,
        "prompt_hash": orchestration.rendered_prompt.prompt_hash,
        "output_hash": orchestration.run_log.output_hash,
        "validation_status": orchestration.run_log.validation_status.value,
        "errors": list(orchestration.errors),
        "written_paths": artifacts,
        "formal_write_performed": False,
        "patch_acceptance": False,
        "publication_performed": False,
    }
    if result.response is not None:
        output["provider_request_id"] = result.response.provider_request_id
        output["raw_output_persisted"] = result.response.raw_output_persisted
    if result.error is not None:
        output["error"] = dict(result.error.to_mapping())
    stdout.write(json.dumps(output, indent=2, sort_keys=True))
    stdout.write("\n")
    return 0 if orchestration.is_valid else 1


def _build_deepseek_execution_request_from_args(
    args: argparse.Namespace,
    *,
    real_provider_calls_enabled: bool,
) -> ProviderExecutionRequest:
    essay = read_markdown_essay(args.essay, root=args.root)
    provider_request = build_extract_units_provider_request(
        essay,
        ExtractUnitsProviderRequestSpec(
            run_id=args.run_id,
            provider=DEEPSEEK_PROVIDER,
            model=args.model,
            prompt_version=args.prompt_version,
            schema_version=args.schema_version,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            real_provider_calls_enabled=real_provider_calls_enabled,
        ),
    )
    rendered_prompt = render_extract_units_prompt(provider_request)
    return ProviderExecutionRequest(
        provider_request=provider_request,
        rendered_prompt=rendered_prompt,
    )


def _deepseek_config_from_args(args: argparse.Namespace) -> DeepSeekAdapterConfig:
    return DeepSeekAdapterConfig(
        api_key_env_var=args.api_key_env_var,
        base_url=args.base_url,
        timeout_seconds=args.timeout_seconds,
        max_retries=args.max_retries,
        max_tokens=args.max_tokens,
        api_key_value_reading_approved=getattr(
            args,
            "api_key_value_reading_approved",
            False,
        ),
        real_provider_calls_approved=getattr(
            args,
            "real_provider_call_approved",
            False,
        ),
        real_network_calls_approved=getattr(
            args,
            "real_network_call_approved",
            False,
        ),
        prompt_source_schema_externalization_approved=getattr(
            args,
            "prompt_source_schema_externalization_approved",
            False,
        ),
        cost_limit=getattr(args, "cost_limit", None),
        cost_limit_approved=getattr(args, "cost_limit_approved", False),
    )


def _deepseek_live_execution_requested(args: argparse.Namespace) -> bool:
    return any(
        (
            getattr(args, "api_key_value_reading_approved", False),
            getattr(args, "real_network_call_approved", False),
            getattr(args, "prompt_source_schema_externalization_approved", False),
            getattr(args, "cost_limit_approved", False),
        )
    )


def _deepseek_preflight_blockers(args: argparse.Namespace) -> list[str]:
    blockers: list[str] = []
    if args.api_key_env_var != DEEPSEEK_API_KEY_ENV_VAR:
        blockers.append(f"api_key_env_var must be {DEEPSEEK_API_KEY_ENV_VAR}")
    if args.base_url != DEEPSEEK_BASE_URL:
        blockers.append(f"base_url must be {DEEPSEEK_BASE_URL}")
    if args.max_retries != 0:
        blockers.append("max_retries must be 0")
    if args.cost_limit is None or args.cost_limit <= 0:
        blockers.append("cost_limit must be positive")
    if args.raw_output_retention != DEEPSEEK_RAW_OUTPUT_RETENTION:
        blockers.append(
            "raw_output_retention must be " f"{DEEPSEEK_RAW_OUTPUT_RETENTION}"
        )
    required_flags = {
        "real_provider_call_approved": args.real_provider_call_approved,
        "api_key_value_reading_approved": args.api_key_value_reading_approved,
        "real_network_call_approved": args.real_network_call_approved,
        "prompt_source_schema_externalization_approved": (
            args.prompt_source_schema_externalization_approved
        ),
        "cost_limit_approved": args.cost_limit_approved,
    }
    for name, approved in required_flags.items():
        if not approved:
            blockers.append(f"{name} must be approved")
    return blockers


def _deepseek_model_policy(args: argparse.Namespace) -> ModelPolicy:
    return ModelPolicy(
        first_provider=DEEPSEEK_PROVIDER,
        real_provider_calls_approved=args.real_provider_call_approved,
        api_key_env_var_policy=APIKeyEnvVarPolicy(
            env_var_name=args.api_key_env_var,
            read_allowed=args.api_key_value_reading_approved,
        ),
        retry_policy=RetryPolicy(max_retries=args.max_retries),
        timeout_policy=TimeoutPolicy(
            default_timeout_seconds=args.timeout_seconds,
            maximum_timeout_seconds=args.timeout_seconds,
        ),
        cost_policy=CostPolicy(cost_limit=args.cost_limit),
    )


def _persist_deepseek_artifacts(
    orchestration,
    *,
    vault_root: str,
    created_at: str,
) -> list[str]:
    extraction_artifact_path: str | None = None
    if orchestration.validation_result.proposal is not None:
        extraction_artifact = write_validated_extraction_artifact(
            orchestration.validation_result.proposal,
            vault_root=vault_root,
            created_at=created_at,
            context=ExtractionArtifactContext(
                stage_label=DEEPSEEK_RUN_STAGE_LABEL,
                run_scope=DEEPSEEK_RUN_SCOPE,
                real_provider_call=True,
                fixture_driven=False,
                prompt_hash=orchestration.rendered_prompt.prompt_hash,
                not_validated=DEEPSEEK_NOT_VALIDATED,
            ),
        )
        extraction_artifact_path = extraction_artifact.relative_path

    run_log_artifact = write_ai_run_log_artifact(
        orchestration.run_log,
        vault_root=vault_root,
        created_at=created_at,
        context=_deepseek_run_log_context(
            orchestration,
            extraction_artifact_path=extraction_artifact_path,
        ),
    )
    paths = [run_log_artifact.relative_path]
    if extraction_artifact_path is not None:
        paths.insert(0, extraction_artifact_path)
    return paths


def _deepseek_run_log_context(
    orchestration,
    *,
    extraction_artifact_path: str | None,
) -> AIRunLogArtifactContext:
    base = orchestration.run_log_context
    output_artifacts = ()
    if extraction_artifact_path is not None:
        output_artifacts = (
            AIRunOutputArtifact(
                artifact_type="validated_extraction_output",
                path=extraction_artifact_path,
            ),
        )
    return AIRunLogArtifactContext(
        stage_label=DEEPSEEK_RUN_STAGE_LABEL,
        run_scope=DEEPSEEK_RUN_SCOPE,
        real_provider_call=True,
        fixture_driven=False,
        prompt_used=True,
        metrics_scope=AIRunMetricsScope(
            cost_applicable=True,
            latency_applicable=True,
            reason=DEEPSEEK_RUN_SCOPE,
        ),
        source_input_id=orchestration.rendered_prompt.source_input_id,
        prompt_hash=orchestration.rendered_prompt.prompt_hash,
        output_artifacts=output_artifacts,
        not_validated=DEEPSEEK_NOT_VALIDATED,
        provider_request_id=base.provider_request_id,
        retry_count=base.retry_count,
        token_usage=base.token_usage,
    )


def _provider_decisions_from_args(
    args: argparse.Namespace,
) -> ProviderIntegrationDecisionSet:
    if args.decisions_json is not None:
        if _has_inline_provider_decisions(args):
            raise ValueError("--decisions-json cannot be combined with decision flags")
        return _load_provider_decisions_json(args.decisions_json)

    return ProviderIntegrationDecisionSet(
        first_provider=args.first_provider,
        default_model=args.default_model,
        provider_sdk_dependency=args.provider_sdk_dependency,
        provider_sdk_dependency_approved=args.provider_sdk_dependency_approved,
        api_key_env_var=args.api_key_env_var,
        api_key_env_var_approved=args.api_key_env_var_approved,
        api_key_value_reading_approved=args.api_key_value_reading_approved,
        real_provider_calls_approved=args.real_provider_calls_approved,
        real_network_calls_approved=args.real_network_calls_approved,
        prompt_text_external_approved=args.prompt_text_external_approved,
        source_body_external_approved=args.source_body_external_approved,
        output_schema_external_approved=args.output_schema_external_approved,
        structured_output_mechanism=args.structured_output_mechanism,
        structured_output_mechanism_approved=(
            args.structured_output_mechanism_approved
        ),
        cost_limit=args.cost_limit,
        cost_limit_approved=args.cost_limit_approved,
        timeout_seconds=args.timeout_seconds,
        timeout_policy_approved=args.timeout_policy_approved,
        max_retries=args.max_retries,
        retry_policy_approved=args.retry_policy_approved,
        raw_output_retention=args.raw_output_retention,
        raw_output_retention_approved=args.raw_output_retention_approved,
        fallback_behavior=args.fallback_behavior,
        fallback_behavior_approved=args.fallback_behavior_approved,
        manual_live_smoke_approved=args.manual_live_smoke_approved,
        recurring_live_smoke_approved=args.recurring_live_smoke_approved,
    )


def _has_inline_provider_decisions(args: argparse.Namespace) -> bool:
    return any(
        (
            args.first_provider is not None,
            args.default_model is not None,
            args.provider_sdk_dependency is not None,
            args.provider_sdk_dependency_approved,
            args.api_key_env_var is not None,
            args.api_key_env_var_approved,
            args.api_key_value_reading_approved,
            args.real_provider_calls_approved,
            args.real_network_calls_approved,
            args.prompt_text_external_approved,
            args.source_body_external_approved,
            args.output_schema_external_approved,
            args.structured_output_mechanism is not None,
            args.structured_output_mechanism_approved,
            args.cost_limit is not None,
            args.cost_limit_approved,
            args.timeout_seconds is not None,
            args.timeout_policy_approved,
            args.max_retries is not None,
            args.retry_policy_approved,
            args.raw_output_retention is not None,
            args.raw_output_retention_approved,
            args.fallback_behavior is not None,
            args.fallback_behavior_approved,
            args.manual_live_smoke_approved,
            args.recurring_live_smoke_approved,
        )
    )


def _load_provider_decisions_json(path: str) -> ProviderIntegrationDecisionSet:
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read provider decisions JSON: {path}") from exc

    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid provider decisions JSON: {path}") from exc

    return provider_integration_decisions_from_mapping(value)


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
