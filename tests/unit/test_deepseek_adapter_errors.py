import unittest

from diamonddust.ai.adapters.deepseek import (
    provider_error_from_deepseek_exception,
    provider_result_from_deepseek_response,
    sanitize_deepseek_error_message,
    usage_from_deepseek_response,
)
from diamonddust.ai.provider import ProviderErrorType

try:
    from unit.test_deepseek_adapter_mapping import _execution_request
except ModuleNotFoundError:  # pragma: no cover - supports direct module runs.
    from tests.unit.test_deepseek_adapter_mapping import _execution_request


class DeepSeekAdapterErrorMappingTests(unittest.TestCase):
    def test_maps_chat_completion_success_into_provider_result(self) -> None:
        request = _execution_request()
        response = {
            "id": "chatcmpl_deepseek_ab12cd",
            "choices": [
                {
                    "message": {
                        "content": '{"source_input_id": "raw_essay_deepseek_mapping_ab12cd"}'
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 4,
                "total_tokens": 14,
            },
        }

        result = provider_result_from_deepseek_response(request, response)

        self.assertTrue(result.succeeded)
        self.assertIsNotNone(result.response)
        self.assertEqual(
            result.response.provider_request_id,
            "chatcmpl_deepseek_ab12cd",
        )
        self.assertFalse(result.response.raw_output_persisted)
        self.assertEqual(result.response.usage.input_tokens, 10)
        self.assertEqual(result.response.usage.output_tokens, 4)
        self.assertEqual(result.response.usage.total_tokens, 14)
        self.assertEqual(
            result.response.structured_output,
            {"source_input_id": "raw_essay_deepseek_mapping_ab12cd"},
        )

    def test_maps_object_style_chat_completion_success(self) -> None:
        request = _execution_request()
        response = _Response(
            id="chatcmpl_object_ab12cd",
            choices=(
                _Choice(
                    message=_Message(
                        content='{"source_input_id": "raw_essay_deepseek_mapping_ab12cd"}'
                    )
                ),
            ),
            usage=_Usage(prompt_tokens=3, completion_tokens=5, total_tokens=8),
        )

        result = provider_result_from_deepseek_response(request, response)

        self.assertTrue(result.succeeded)
        self.assertEqual(result.response.usage.input_tokens, 3)
        self.assertEqual(result.response.usage.output_tokens, 5)
        self.assertEqual(result.response.usage.total_tokens, 8)

    def test_maps_malformed_response_to_fail_closed_error(self) -> None:
        request = _execution_request()

        result = provider_result_from_deepseek_response(
            request,
            {
                "id": "chatcmpl_malformed_ab12cd",
                "choices": [{"message": {"content": "not-json"}}],
            },
        )

        self.assertFalse(result.succeeded)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.error_type, ProviderErrorType.MALFORMED_RESPONSE)
        self.assertFalse(result.error.should_retry)
        self.assertEqual(result.error.provider_request_id, "chatcmpl_malformed_ab12cd")

    def test_usage_defaults_when_provider_usage_absent(self) -> None:
        usage = usage_from_deepseek_response({"id": "resp_no_usage"})

        self.assertIsNone(usage.input_tokens)
        self.assertIsNone(usage.output_tokens)
        self.assertIsNone(usage.total_tokens)
        self.assertEqual(usage.retry_count, 0)

    def test_maps_deepseek_status_code_exceptions(self) -> None:
        cases = (
            (400, ProviderErrorType.INVALID_REQUEST),
            (401, ProviderErrorType.AUTH_ERROR),
            (402, ProviderErrorType.COST_LIMIT_EXCEEDED),
            (422, ProviderErrorType.INVALID_REQUEST),
            (429, ProviderErrorType.RATE_LIMIT),
            (500, ProviderErrorType.PROVIDER_SERVER_ERROR),
            (503, ProviderErrorType.PROVIDER_SERVER_ERROR),
        )

        for status_code, error_type in cases:
            with self.subTest(status_code=status_code):
                provider_error = provider_error_from_deepseek_exception(
                    _status_exception(status_code)
                )
                self.assertEqual(provider_error.error_type, error_type)

    def test_sanitizes_key_like_error_messages(self) -> None:
        message = sanitize_deepseek_error_message(
            "authorization: Bearer sk-test-secret and api_key=plain-secret",
            secrets=("plain-secret",),
        )

        self.assertNotIn("sk-test-secret", message)
        self.assertNotIn("plain-secret", message)
        self.assertIn("[REDACTED]", message)


class _Message:
    def __init__(self, *, content: str) -> None:
        self.content = content


class _Choice:
    def __init__(self, *, message: _Message) -> None:
        self.message = message


class _Usage:
    def __init__(
        self,
        *,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
    ) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class _Response:
    def __init__(
        self,
        *,
        id: str,
        choices: tuple[_Choice, ...],
        usage: _Usage,
    ) -> None:
        self.id = id
        self.choices = choices
        self.usage = usage


def _status_exception(status_code: int) -> Exception:
    class StatusError(Exception):
        pass

    error = StatusError(f"status {status_code}")
    error.status_code = status_code
    error.request_id = f"req_{status_code}"
    return error


if __name__ == "__main__":
    unittest.main()
