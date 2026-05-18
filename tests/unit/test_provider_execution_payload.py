import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.ai import (
    EXTRACTION_OUTPUT_SCHEMA_ID,
    FakeExecutionProvider,
    PROVIDER_EXECUTION_PAYLOAD_SCHEMA_VERSION,
    ProviderBoundaryError,
    ProviderExecutionMessage,
    ProviderExecutionMessageRole,
    ProviderExecutionPayload,
    ProviderExecutionRequest,
    build_provider_execution_payload,
    render_extract_units_prompt,
)
from diamonddust.application import (
    ExtractUnitsProviderRequestSpec,
    build_extract_units_provider_request,
)
from diamonddust.storage import ingest_markdown_text


class ProviderExecutionPayloadTests(unittest.TestCase):
    def test_builds_provider_neutral_payload_from_execution_request(self) -> None:
        execution_request = _execution_request()

        payload = build_provider_execution_payload(execution_request)

        self.assertEqual(
            payload.payload_schema_version,
            PROVIDER_EXECUTION_PAYLOAD_SCHEMA_VERSION,
        )
        self.assertEqual(payload.run_id, "run_provider_payload_ab12cd")
        self.assertEqual(payload.task, "extract_units")
        self.assertEqual(payload.provider, "fake-provider")
        self.assertEqual(payload.model, "fake-structured-model")
        self.assertEqual(payload.prompt_hash, execution_request.prompt_hash)
        self.assertEqual(len(payload.messages), 2)
        self.assertEqual(payload.messages[0].role, ProviderExecutionMessageRole.SYSTEM)
        self.assertEqual(payload.messages[1].role, ProviderExecutionMessageRole.USER)
        self.assertIn("Return structured JSON only.", payload.messages[0].content)
        self.assertIn("Payloads prepare provider adapter input.", payload.messages[1].content)
        self.assertEqual(payload.output_schema_id, EXTRACTION_OUTPUT_SCHEMA_ID)
        self.assertEqual(
            payload.output_schema_hash,
            execution_request.rendered_prompt.output_schema_hash,
        )
        self.assertEqual(
            payload.output_schema["$id"],
            "diamonddust.extract_units.output.v0",
        )
        self.assertTrue(payload.structured_output_required)
        self.assertFalse(payload.real_provider_calls_enabled)
        self.assertFalse(payload.tool_calls_enabled)
        self.assertFalse(payload.raw_output_persistence_allowed)

    def test_payload_mapping_is_json_serializable_review_shape(self) -> None:
        payload = build_provider_execution_payload(_execution_request())

        mapping = payload.to_mapping()
        encoded = json.dumps(mapping, sort_keys=True)
        decoded = json.loads(encoded)

        self.assertEqual(decoded["payload_schema_version"], "0.1.0")
        self.assertEqual(decoded["messages"][0]["role"], "system")
        self.assertEqual(decoded["messages"][1]["role"], "user")
        self.assertEqual(
            decoded["output_schema"]["$id"],
            "diamonddust.extract_units.output.v0",
        )
        self.assertNotIn("api_key", encoded.lower())
        self.assertNotIn("provider_sdk_payload", decoded)

    def test_payload_construction_does_not_execute_provider_or_persist_files(self) -> None:
        execution_request = _execution_request()
        provider = _RecordingExecutionProvider()

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            payload = build_provider_execution_payload(execution_request)

            self.assertFalse(provider.called)
            self.assertEqual(list(root.iterdir()), [])
            self.assertEqual(payload.run_id, execution_request.provider_request.run_id)

    def test_payload_rejects_unsafe_or_invalid_shape(self) -> None:
        with self.assertRaises(ProviderBoundaryError):
            build_provider_execution_payload("not execution request")

        with self.assertRaises(ProviderBoundaryError):
            ProviderExecutionMessage(
                role="system",
                content="not strongly typed",
            )

        with self.assertRaises(ProviderBoundaryError):
            ProviderExecutionPayload(
                payload_schema_version="0.1.0",
                run_id="run_payload_invalid_ab12cd",
                task="extract_units",
                provider="fake-provider",
                model="fake-model",
                prompt_version="extract_units.v1",
                schema_version="0.1.0",
                input_hash="sha256:input",
                prompt_hash="sha256:prompt",
                messages=(
                    ProviderExecutionMessage(
                        role=ProviderExecutionMessageRole.SYSTEM,
                        content="system",
                    ),
                ),
                output_instructions="instructions",
                output_schema_id=EXTRACTION_OUTPUT_SCHEMA_ID,
                output_schema_version="0.1.0",
                output_schema_hash="sha256:schema",
                output_schema={"$id": EXTRACTION_OUTPUT_SCHEMA_ID},
                structured_output_required=True,
                real_provider_calls_enabled=False,
                tool_calls_enabled=False,
                timeout_seconds=None,
                max_retries=0,
                raw_output_persistence_allowed=True,
            )


class _RecordingExecutionProvider:
    def __init__(self) -> None:
        self.called = False

    def generate(self, request: ProviderExecutionRequest):
        self.called = True
        return FakeExecutionProvider(structured_output={}).generate(request)


def _execution_request() -> ProviderExecutionRequest:
    request = build_extract_units_provider_request(
        ingest_markdown_text(
            """---
id: raw_essay_provider_payload_ab12cd
tags:
  - ai
  - provider
---
# Provider payload

Payloads prepare provider adapter input.
""",
            source_path="00-inbox/provider-payload.md",
            source_name="provider-payload",
        ),
        ExtractUnitsProviderRequestSpec(
            run_id="run_provider_payload_ab12cd",
            provider="fake-provider",
            model="fake-structured-model",
            prompt_version="extract_units.v1",
            schema_version="0.1.0",
            timeout_seconds=30,
            max_retries=1,
        ),
    )
    return ProviderExecutionRequest(
        provider_request=request,
        rendered_prompt=render_extract_units_prompt(request),
    )


if __name__ == "__main__":
    unittest.main()
