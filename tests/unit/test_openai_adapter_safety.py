import ast
from pathlib import Path
import unittest
from unittest.mock import patch

from diamonddust.ai import (
    EXTRACTION_TASK,
    EXTRACT_UNITS_PROMPT_VERSION,
    ProviderExecutionRequest,
    ProviderModelSettings,
    ProviderRequest,
    render_extract_units_prompt,
)
from diamonddust.ai.adapters import openai as openai_adapter
from diamonddust.ai.adapters.openai import (
    OpenAIAdapterConfig,
    OpenAIExecutionClient,
    build_openai_dry_run_report,
    build_sanitized_openai_request_preview,
)
from diamonddust.ai.provider import ProviderErrorType


ROOT = Path(__file__).resolve().parents[2]


class OpenAIAdapterSafetyTests(unittest.TestCase):
    def test_generate_refuses_when_request_does_not_enable_real_provider_calls(self) -> None:
        fake_client = _FakeSDKClient()
        request = _execution_request(real_provider_calls_enabled=False)

        result = OpenAIExecutionClient(
            config=OpenAIAdapterConfig(),
            sdk_client=fake_client,
        ).generate(request)

        self.assertFalse(result.succeeded)
        self.assertEqual(result.error.error_type, ProviderErrorType.PERMISSION_ERROR)
        self.assertIn(
            "provider request real_provider_calls_enabled is false",
            result.error.message,
        )
        self.assertEqual(fake_client.create_call_count, 0)

    def test_generate_refuses_even_with_request_flag_until_live_approvals_exist(self) -> None:
        fake_client = _FakeSDKClient()
        request = _execution_request(real_provider_calls_enabled=True)

        result = OpenAIExecutionClient(
            config=OpenAIAdapterConfig(),
            sdk_client=fake_client,
        ).generate(request)

        self.assertFalse(result.succeeded)
        self.assertEqual(result.error.error_type, ProviderErrorType.PERMISSION_ERROR)
        self.assertIn("API key value reading is not approved", result.error.message)
        self.assertIn("real network calls are not approved", result.error.message)
        self.assertEqual(fake_client.create_call_count, 0)

    def test_generate_uses_injected_client_when_live_approvals_exist(self) -> None:
        fake_client = _FakeSDKClient()
        request = _execution_request(real_provider_calls_enabled=True)

        result = OpenAIExecutionClient(
            config=OpenAIAdapterConfig(
                timeout_seconds=60,
                api_key_value_reading_approved=True,
                real_provider_calls_approved=True,
                real_network_calls_approved=True,
                live_smoke_approved=True,
                prompt_source_schema_externalization_approved=True,
                cost_limit=1.0,
                cost_limit_approved=True,
            ),
            sdk_client=fake_client,
        ).generate(request)

        self.assertTrue(result.succeeded, result.error)
        self.assertEqual(fake_client.create_call_count, 1)

    def test_preview_dry_run_and_guard_do_not_read_environment_values(self) -> None:
        request = _execution_request(real_provider_calls_enabled=True)
        exploding_environ = _ExplodingEnviron()

        with patch.object(openai_adapter.os, "environ", exploding_environ):
            preview = build_sanitized_openai_request_preview(request)
            dry_run = build_openai_dry_run_report(request)
            result = OpenAIExecutionClient().generate(request)

        self.assertFalse(preview["api_key_value_read"])
        self.assertFalse(dry_run["api_key_value_read"])
        self.assertFalse(result.succeeded)

    def test_openai_sdk_import_is_adapter_local(self) -> None:
        violations: list[str] = []
        for path in sorted((ROOT / "src" / "diamonddust").rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported = {alias.name for alias in node.names}
                    if "openai" in imported:
                        _record_if_not_adapter(path, violations)
                if isinstance(node, ast.ImportFrom) and node.module == "openai":
                    _record_if_not_adapter(path, violations)

        self.assertEqual(violations, [])


class _FakeResponses:
    def __init__(self) -> None:
        self.create_call_count = 0

    def create(self, **kwargs: object) -> object:
        self.create_call_count += 1
        return {"id": "resp_fake", "output_parsed": {"ok": True}}


class _FakeSDKClient:
    def __init__(self) -> None:
        self.responses = _FakeResponses()

    @property
    def create_call_count(self) -> int:
        return self.responses.create_call_count


class _ExplodingEnviron(dict):
    def get(self, *args: object, **kwargs: object) -> object:
        raise AssertionError("environment value was read")

    def __getitem__(self, key: object) -> object:
        raise AssertionError("environment value was read")


def _record_if_not_adapter(path: Path, violations: list[str]) -> None:
    relative = path.relative_to(ROOT).as_posix()
    if relative != "src/diamonddust/ai/adapters/openai.py":
        violations.append(relative)


def _execution_request(
    *,
    real_provider_calls_enabled: bool = False,
) -> ProviderExecutionRequest:
    provider_request = _provider_request(real_provider_calls_enabled=False)
    rendered_prompt = render_extract_units_prompt(provider_request)
    if real_provider_calls_enabled:
        provider_request = _provider_request(real_provider_calls_enabled=True)
    return ProviderExecutionRequest(
        provider_request=provider_request,
        rendered_prompt=rendered_prompt,
    )


def _provider_request(*, real_provider_calls_enabled: bool) -> ProviderRequest:
    return ProviderRequest(
        run_id="run_openai_safety_ab12cd",
        task=EXTRACTION_TASK,
        input_hash="input_hash_ab12cd",
        input_payload={
            "source_input_id": "raw_essay_openai_safety_ab12cd",
            "source_path": "tests/fixtures/openai-safety.md",
            "raw_content_hash": "raw_hash_ab12cd",
            "body_content_hash": "body_hash_ab12cd",
            "body_line_start": 5,
            "body_line_end": 5,
            "frontmatter": {"id": "raw_essay_openai_safety_ab12cd"},
            "body": "body text visible only inside full mapping",
            "source_ref": {
                "source_id": "raw_essay_openai_safety_ab12cd",
                "source_path": "tests/fixtures/openai-safety.md",
                "source_span": "body",
                "origin": "user",
                "is_approximate": True,
            },
        },
        settings=ProviderModelSettings(
            provider="openai",
            model="owner-approved-model-placeholder",
            prompt_version=EXTRACT_UNITS_PROMPT_VERSION,
            schema_version="0.1.0",
            timeout_seconds=60,
            max_retries=0,
            real_provider_calls_enabled=real_provider_calls_enabled,
        ),
    )


if __name__ == "__main__":
    unittest.main()
