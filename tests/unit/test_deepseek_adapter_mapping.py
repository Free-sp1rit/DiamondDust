import json
import unittest

from diamonddust.ai import (
    CURRENT_EXTRACTION_SCHEMA_VERSION,
    EXTRACTION_TASK,
    EXTRACT_UNITS_PROMPT_VERSION,
    ProviderExecutionRequest,
    ProviderModelSettings,
    ProviderRequest,
    render_extract_units_prompt,
)
from diamonddust.ai.adapters.deepseek import (
    DEEPSEEK_BASE_URL,
    DEEPSEEK_DEFAULT_MAX_TOKENS,
    DEEPSEEK_RESPONSE_FORMAT,
    build_deepseek_request_mapping,
    build_sanitized_deepseek_request_preview,
)


class DeepSeekAdapterMappingTests(unittest.TestCase):
    def test_maps_provider_neutral_request_to_deepseek_chat_shape(self) -> None:
        request = _execution_request()

        mapped = build_deepseek_request_mapping(request)

        self.assertEqual(mapped["method"], "chat.completions.create")
        self.assertEqual(mapped["base_url"], DEEPSEEK_BASE_URL)
        self.assertEqual(mapped["model"], "owner-approved-model-placeholder")
        self.assertFalse(mapped["stream"])
        self.assertEqual(mapped["response_format"], DEEPSEEK_RESPONSE_FORMAT)
        self.assertEqual(
            [message["role"] for message in mapped["messages"]],
            ["system", "user"],
        )
        self.assertIn(
            "Return one JSON object with:",
            mapped["messages"][0]["content"],
        )
        self.assertIn(
            '"unit_candidates": []',
            mapped["messages"][0]["content"],
        )
        self.assertIn(
            '"relation_candidates": []',
            mapped["messages"][0]["content"],
        )
        self.assertIn(
            "body text visible only inside full mapping",
            mapped["messages"][1]["content"],
        )
        self.assertEqual(mapped["max_tokens"], DEEPSEEK_DEFAULT_MAX_TOKENS)
        self.assertEqual(
            mapped["_adapter_options"]["structured_output_mechanism"],
            "json_object",
        )
        self.assertEqual(mapped["_adapter_options"]["max_retries"], 0)
        self.assertEqual(
            mapped["_adapter_options"]["max_tokens"],
            DEEPSEEK_DEFAULT_MAX_TOKENS,
        )

    def test_sanitized_preview_excludes_raw_prompt_and_schema(self) -> None:
        request = _execution_request()

        preview = build_sanitized_deepseek_request_preview(request)
        preview_json = json.dumps(preview, sort_keys=True)

        self.assertEqual(preview["provider"], "deepseek")
        self.assertEqual(preview["sdk_method"], "chat.completions.create")
        self.assertFalse(preview["provider_called"])
        self.assertFalse(preview["network_call"])
        self.assertFalse(preview["api_key_value_read"])
        self.assertFalse(preview["payload_contains_raw_prompt"])
        self.assertFalse(preview["payload_contains_raw_schema"])
        self.assertEqual(preview["message_roles"], ["system", "user"])
        self.assertEqual(len(preview["message_content_hashes"]), 2)
        self.assertEqual(preview["structured_output_mechanism"], "json_object")
        self.assertEqual(preview["response_format"], {"type": "json_object"})
        self.assertEqual(preview["max_tokens"], DEEPSEEK_DEFAULT_MAX_TOKENS)
        self.assertNotIn("body text visible only inside full mapping", preview_json)
        self.assertNotIn("knowledge_unit", preview_json)


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
        run_id="run_deepseek_mapping_ab12cd",
        task=EXTRACTION_TASK,
        input_hash="input_hash_ab12cd",
        input_payload={
            "source_input_id": "raw_essay_deepseek_mapping_ab12cd",
            "source_path": "tests/fixtures/deepseek.md",
            "raw_content_hash": "raw_hash_ab12cd",
            "body_content_hash": "body_hash_ab12cd",
            "body_line_start": 5,
            "body_line_end": 5,
            "frontmatter": {"id": "raw_essay_deepseek_mapping_ab12cd"},
            "body": "body text visible only inside full mapping",
            "source_ref": {
                "source_id": "raw_essay_deepseek_mapping_ab12cd",
                "source_path": "tests/fixtures/deepseek.md",
                "source_span": "body",
                "origin": "user",
                "is_approximate": True,
            },
        },
        settings=ProviderModelSettings(
            provider="deepseek",
            model="owner-approved-model-placeholder",
            prompt_version=EXTRACT_UNITS_PROMPT_VERSION,
            schema_version=CURRENT_EXTRACTION_SCHEMA_VERSION,
            timeout_seconds=30,
            max_retries=0,
            real_provider_calls_enabled=real_provider_calls_enabled,
        ),
    )


if __name__ == "__main__":
    unittest.main()
