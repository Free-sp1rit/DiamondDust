import unittest
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.ai import (
    FakeExecutionProvider,
    ProviderBoundaryError,
    ProviderExecutionRequest,
    ProviderUsage,
    render_extract_units_prompt,
)
from diamonddust.application import (
    ExtractUnitsProviderRequestSpec,
    build_extract_units_provider_request,
)
from diamonddust.storage import ingest_markdown_text


class ProviderExecutionRequestTests(unittest.TestCase):
    def test_execution_request_binds_provider_request_and_rendered_prompt(self) -> None:
        request = _request()
        rendered_prompt = render_extract_units_prompt(request)

        execution_request = ProviderExecutionRequest(
            provider_request=request,
            rendered_prompt=rendered_prompt,
        )

        self.assertEqual(execution_request.provider_request, request)
        self.assertEqual(execution_request.rendered_prompt, rendered_prompt)
        self.assertEqual(execution_request.prompt_hash, rendered_prompt.prompt_hash)

    def test_execution_request_rejects_mismatched_prompt_metadata(self) -> None:
        request = _request()
        rendered_prompt = render_extract_units_prompt(request)

        with self.assertRaises(ProviderBoundaryError):
            ProviderExecutionRequest(
                provider_request=request,
                rendered_prompt=replace(rendered_prompt, run_id="run_other_ab12cd"),
            )

        with self.assertRaises(ProviderBoundaryError):
            ProviderExecutionRequest(
                provider_request=request,
                rendered_prompt=replace(
                    rendered_prompt,
                    source_input_id="raw_essay_other_ab12cd",
                ),
            )

        with self.assertRaises(ProviderBoundaryError):
            ProviderExecutionRequest(
                provider_request=request,
                rendered_prompt=replace(rendered_prompt, output_schema_version="0.2.0"),
            )

    def test_fake_execution_provider_returns_envelope_without_persistence(self) -> None:
        request = _request()
        execution_request = ProviderExecutionRequest(
            provider_request=request,
            rendered_prompt=render_extract_units_prompt(request),
        )
        provider = FakeExecutionProvider(
            structured_output=_valid_output(request.input_payload),
            provider_request_id="provider_req_execution_ab12cd",
            usage=ProviderUsage(input_tokens=5, output_tokens=8, total_tokens=13),
        )

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = provider.generate(execution_request)

            self.assertTrue(result.succeeded)
            self.assertEqual(result.request, request)
            self.assertEqual(
                result.response.provider_request_id,
                "provider_req_execution_ab12cd",
            )
            self.assertFalse(result.response.raw_output_persisted)
            self.assertEqual(list(root.iterdir()), [])

    def test_fake_execution_provider_rejects_plain_provider_request(self) -> None:
        with self.assertRaises(ProviderBoundaryError):
            FakeExecutionProvider(structured_output={}).generate(_request())


def _request():
    return build_extract_units_provider_request(
        ingest_markdown_text(
            """---
id: raw_essay_provider_execution_ab12cd
tags:
  - ai
  - provider
---
# Provider execution request

Execution requests carry rendered prompts into provider adapters.
""",
            source_path="00-inbox/provider-execution.md",
            source_name="provider-execution",
        ),
        ExtractUnitsProviderRequestSpec(
            run_id="run_provider_execution_ab12cd",
            provider="fake-provider",
            model="fake-structured-model",
            prompt_version="extract_units.v1",
            schema_version="0.1.0",
        ),
    )


def _valid_output(payload) -> dict:
    source_ref = dict(payload["source_ref"])
    return {
        "source_input_id": payload["source_input_id"],
        "unit_candidates": [
            {
                "id": "unit_provider_execution_ab12cd",
                "type": "concept",
                "title": "Provider execution requests",
                "content": "Provider execution requests carry rendered prompts into provider adapters.",
                "status": "seedling",
                "source_refs": [source_ref],
                "relations": [],
                "confidence": "medium",
                "created_at": "2026-05-17T00:00:00Z",
                "updated_at": "2026-05-17T00:00:00Z",
                "schema_version": "0.1.0",
            }
        ],
        "relation_candidates": [],
    }


if __name__ == "__main__":
    unittest.main()
