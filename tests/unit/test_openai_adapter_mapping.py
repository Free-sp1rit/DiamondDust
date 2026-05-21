import json
import unittest

from diamonddust.ai import (
    EXTRACTION_TASK,
    EXTRACT_UNITS_PROMPT_VERSION,
    ProviderExecutionRequest,
    ProviderModelSettings,
    ProviderRequest,
    render_extract_units_prompt,
)
from diamonddust.ai.adapters.openai import (
    OPENAI_JSON_SCHEMA_NAME,
    build_openai_request_mapping,
    build_sanitized_openai_request_preview,
)


class OpenAIAdapterMappingTests(unittest.TestCase):
    def test_maps_provider_neutral_request_to_openai_shape(self) -> None:
        request = _execution_request()

        mapped = build_openai_request_mapping(request)

        self.assertEqual(mapped["method"], "responses.create")
        self.assertEqual(mapped["model"], "owner-approved-model-placeholder")
        self.assertEqual(mapped["tools"], [])
        self.assertFalse(mapped["store"])
        self.assertEqual(
            [message["role"] for message in mapped["input"]],
            ["system", "user"],
        )
        self.assertIn("body text visible only inside full mapping", mapped["input"][1]["content"])
        schema_format = mapped["text"]["format"]
        self.assertEqual(schema_format["type"], "json_schema")
        self.assertEqual(schema_format["name"], OPENAI_JSON_SCHEMA_NAME)
        self.assertTrue(schema_format["strict"])
        self.assertIn("knowledge_unit", schema_format["schema"]["$defs"])
        self.assertEqual(mapped["_adapter_options"]["max_retries"], 0)

    def test_sanitized_preview_excludes_raw_prompt_and_schema(self) -> None:
        request = _execution_request()

        preview = build_sanitized_openai_request_preview(request)
        preview_json = json.dumps(preview, sort_keys=True)

        self.assertEqual(preview["provider"], "openai")
        self.assertEqual(preview["sdk_method"], "responses.create")
        self.assertFalse(preview["provider_called"])
        self.assertFalse(preview["network_call"])
        self.assertFalse(preview["api_key_value_read"])
        self.assertFalse(preview["payload_contains_raw_prompt"])
        self.assertFalse(preview["payload_contains_raw_schema"])
        self.assertEqual(preview["message_roles"], ["system", "user"])
        self.assertEqual(len(preview["message_content_hashes"]), 2)
        self.assertEqual(
            preview["output_schema_id"],
            "diamonddust.extract_units.output.v0",
        )
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
        run_id="run_openai_mapping_ab12cd",
        task=EXTRACTION_TASK,
        input_hash="input_hash_ab12cd",
        input_payload={
            "source_input_id": "raw_essay_openai_mapping_ab12cd",
            "source_path": "tests/fixtures/openai.md",
            "raw_content_hash": "raw_hash_ab12cd",
            "body_content_hash": "body_hash_ab12cd",
            "body_line_start": 5,
            "body_line_end": 5,
            "frontmatter": {"id": "raw_essay_openai_mapping_ab12cd"},
            "body": "body text visible only inside full mapping",
            "source_ref": {
                "source_id": "raw_essay_openai_mapping_ab12cd",
                "source_path": "tests/fixtures/openai.md",
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
            timeout_seconds=30,
            max_retries=0,
            real_provider_calls_enabled=real_provider_calls_enabled,
        ),
    )


if __name__ == "__main__":
    unittest.main()
