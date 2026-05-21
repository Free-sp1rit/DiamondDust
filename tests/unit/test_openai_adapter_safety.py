import ast
from pathlib import Path
import unittest
from unittest.mock import patch

from diamonddust.ai.adapters import openai as openai_adapter
from diamonddust.ai.adapters.openai import (
    OpenAIAdapterConfig,
    OpenAIExecutionClient,
    build_openai_dry_run_report,
    build_sanitized_openai_request_preview,
)
from diamonddust.ai.provider import ProviderErrorType
from unit.test_openai_adapter_mapping import _execution_request


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


if __name__ == "__main__":
    unittest.main()
