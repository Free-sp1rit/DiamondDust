import unittest

from diamonddust.ai.provider import ProviderErrorType
from diamonddust.ai.adapters.openai import (
    provider_error_from_openai_exception,
    provider_result_from_openai_response,
    sanitize_openai_error_message,
    usage_from_openai_response,
)
from unit.test_openai_adapter_mapping import _execution_request


class OpenAIAdapterErrorMappingTests(unittest.TestCase):
    def test_maps_success_response_into_provider_result(self) -> None:
        request = _execution_request()
        response = {
            "id": "resp_openai_ab12cd",
            "output_parsed": {"source_input_id": "raw_essay_openai_mapping_ab12cd"},
            "usage": {
                "input_tokens": 10,
                "output_tokens": 4,
                "total_tokens": 14,
            },
        }

        result = provider_result_from_openai_response(request, response)

        self.assertTrue(result.succeeded)
        self.assertIsNotNone(result.response)
        self.assertEqual(result.response.provider_request_id, "resp_openai_ab12cd")
        self.assertFalse(result.response.raw_output_persisted)
        self.assertEqual(result.response.usage.input_tokens, 10)
        self.assertEqual(result.response.usage.output_tokens, 4)
        self.assertEqual(result.response.usage.total_tokens, 14)
        self.assertEqual(
            result.response.structured_output,
            {"source_input_id": "raw_essay_openai_mapping_ab12cd"},
        )

    def test_maps_output_text_json_into_provider_result(self) -> None:
        request = _execution_request()
        response = {
            "id": "resp_openai_json_text_ab12cd",
            "output_text": '{"source_input_id": "raw_essay_openai_mapping_ab12cd"}',
            "usage": {"prompt_tokens": 3, "completion_tokens": 5},
        }

        result = provider_result_from_openai_response(request, response)

        self.assertTrue(result.succeeded)
        self.assertEqual(result.response.usage.input_tokens, 3)
        self.assertEqual(result.response.usage.output_tokens, 5)
        self.assertEqual(result.response.usage.total_tokens, 8)

    def test_maps_malformed_response_to_fail_closed_error(self) -> None:
        request = _execution_request()

        result = provider_result_from_openai_response(
            request,
            {"id": "resp_malformed_ab12cd", "output_text": "not-json"},
        )

        self.assertFalse(result.succeeded)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.error_type, ProviderErrorType.MALFORMED_RESPONSE)
        self.assertFalse(result.error.should_retry)
        self.assertEqual(result.error.provider_request_id, "resp_malformed_ab12cd")

    def test_usage_defaults_when_provider_usage_absent(self) -> None:
        usage = usage_from_openai_response({"id": "resp_no_usage"})

        self.assertIsNone(usage.input_tokens)
        self.assertIsNone(usage.output_tokens)
        self.assertIsNone(usage.total_tokens)
        self.assertEqual(usage.retry_count, 0)

    def test_maps_known_exception_types(self) -> None:
        cases = (
            (_exception("AuthenticationError"), ProviderErrorType.AUTH_ERROR),
            (_exception("PermissionDeniedError"), ProviderErrorType.PERMISSION_ERROR),
            (_exception("RateLimitError"), ProviderErrorType.RATE_LIMIT),
            (_exception("APITimeoutError"), ProviderErrorType.TIMEOUT),
            (_exception("APIConnectionError"), ProviderErrorType.NETWORK_ERROR),
            (_exception("BadRequestError"), ProviderErrorType.INVALID_REQUEST),
            (_exception("UnsupportedFeatureError"), ProviderErrorType.UNSUPPORTED_FEATURE),
            (_exception("APIResponseValidationError"), ProviderErrorType.SCHEMA_VALIDATION_FAILED),
        )

        for exc, error_type in cases:
            with self.subTest(error_type=error_type):
                provider_error = provider_error_from_openai_exception(exc)
                self.assertEqual(provider_error.error_type, error_type)
                self.assertFalse(provider_error.should_retry)

    def test_maps_status_code_exceptions(self) -> None:
        cases = (
            (401, ProviderErrorType.AUTH_ERROR),
            (403, ProviderErrorType.PERMISSION_ERROR),
            (429, ProviderErrorType.RATE_LIMIT),
            (408, ProviderErrorType.TIMEOUT),
            (500, ProviderErrorType.PROVIDER_SERVER_ERROR),
        )

        for status_code, error_type in cases:
            with self.subTest(status_code=status_code):
                provider_error = provider_error_from_openai_exception(
                    _status_exception(status_code)
                )
                self.assertEqual(provider_error.error_type, error_type)

    def test_sanitizes_key_like_error_messages(self) -> None:
        message = sanitize_openai_error_message(
            "authorization: Bearer sk-test-secret and api_key=plain-secret",
            secrets=("plain-secret",),
        )

        self.assertNotIn("sk-test-secret", message)
        self.assertNotIn("plain-secret", message)
        self.assertIn("[REDACTED]", message)


def _exception(class_name: str) -> Exception:
    cls = type(class_name, (Exception,), {})
    return cls("provider failed")


def _status_exception(status_code: int) -> Exception:
    class StatusError(Exception):
        pass

    error = StatusError(f"status {status_code}")
    error.status_code = status_code
    error.request_id = f"req_{status_code}"
    return error


if __name__ == "__main__":
    unittest.main()
