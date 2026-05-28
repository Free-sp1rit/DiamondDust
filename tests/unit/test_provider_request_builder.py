import unittest

from diamonddust.ai import (
    CURRENT_EXTRACTION_SCHEMA_VERSION,
    EXTRACTION_TASK,
    FakeProvider,
    ModelPolicyError,
)
from diamonddust.application import (
    ExtractUnitsProviderRequestSpec,
    ProviderRequestBuildError,
    build_extract_units_provider_request,
    run_provider_extraction,
)
from diamonddust.storage import ingest_markdown_text


class ProviderRequestBuilderTests(unittest.TestCase):
    def test_builds_extract_units_request_from_ingested_markdown(self) -> None:
        essay = _essay()

        request = build_extract_units_provider_request(essay, _spec())

        self.assertEqual(request.run_id, "run_provider_request_ab12cd")
        self.assertEqual(request.task, EXTRACTION_TASK)
        self.assertEqual(request.input_hash, essay.raw_content_hash)
        self.assertEqual(request.provider, "fake-provider")
        self.assertEqual(request.model, "fake-structured-model")
        self.assertEqual(request.prompt_version, "extract_units.v1")
        self.assertTrue(request.structured_output_required)

        payload = request.input_payload
        self.assertEqual(payload["source_input_id"], essay.source_id)
        self.assertEqual(payload["source_path"], "00-inbox/provider-request.md")
        self.assertEqual(payload["raw_content_hash"], essay.raw_content_hash)
        self.assertEqual(payload["body_content_hash"], essay.body_content_hash)
        self.assertEqual(payload["body_line_start"], essay.body_line_start)
        self.assertEqual(payload["body_line_end"], essay.body_line_end)
        self.assertEqual(payload["body"], essay.body)
        self.assertEqual(
            payload["frontmatter"],
            {
                "id": "raw_essay_provider_request_ab12cd",
                "tags": ["ai", "provider"],
            },
        )
        self.assertEqual(
            payload["source_ref"],
            {
                "source_id": essay.source_id,
                "source_path": essay.source_path,
                "source_span": essay.source_ref.source_span,
                "origin": "user_text",
                "is_approximate": False,
                "line_start": essay.body_line_start,
                "line_end": essay.body_line_end,
                "content_hash": essay.body_content_hash,
            },
        )

    def test_request_builder_validates_model_policy_before_returning(self) -> None:
        with self.assertRaises(ModelPolicyError):
            build_extract_units_provider_request(
                _essay(),
                _spec(real_provider_calls_enabled=True),
            )

    def test_request_can_flow_through_fake_provider_without_network_or_persistence(self) -> None:
        request = build_extract_units_provider_request(_essay(), _spec())

        run = run_provider_extraction(
            FakeProvider(structured_output=_valid_output(request.input_payload)),
            request,
        )

        self.assertTrue(run.is_valid, run.errors)
        self.assertEqual(run.run_log.run_id, "run_provider_request_ab12cd")
        self.assertEqual(run.run_log.input_hash, request.input_hash)

    def test_builder_rejects_invalid_inputs(self) -> None:
        with self.assertRaises(ProviderRequestBuildError):
            build_extract_units_provider_request("not an essay", _spec())

        with self.assertRaises(ProviderRequestBuildError):
            build_extract_units_provider_request(_essay(), "not a spec")

        with self.assertRaises(ProviderRequestBuildError):
            ExtractUnitsProviderRequestSpec(
                run_id="",
                provider="fake-provider",
                model="fake-structured-model",
                prompt_version="extract_units.v1",
                schema_version="0.1.0",
            )


def _essay():
    return ingest_markdown_text(
        """---
id: raw_essay_provider_request_ab12cd
tags:
  - ai
  - provider
---
# Provider request

Provider requests preserve source identity before extraction.
""",
        source_path="00-inbox/provider-request.md",
        source_name="provider-request",
    )


def _spec(*, real_provider_calls_enabled: bool = False) -> ExtractUnitsProviderRequestSpec:
    return ExtractUnitsProviderRequestSpec(
        run_id="run_provider_request_ab12cd",
        provider="fake-provider",
        model="fake-structured-model",
        prompt_version="extract_units.v1",
        schema_version=CURRENT_EXTRACTION_SCHEMA_VERSION,
        real_provider_calls_enabled=real_provider_calls_enabled,
    )


def _valid_output(payload) -> dict:
    source_ref = dict(payload["source_ref"])
    return {
        "source_input_id": payload["source_input_id"],
        "source_context": {
            "source_input_id": payload["source_input_id"],
            "source_shape": "engineering_procedure_note",
            "knowledge_domains": ["Provider request"],
            "background": "这是一份关于 provider request 的工程说明。",
            "main_content": ["source identity", "request payload"],
            "scope": "用于测试 provider request builder 输出。",
            "source_refs": [source_ref],
        },
        "unit_candidates": [
            {
                "id": "unit_provider_request_ab12cd",
                "type": "concept",
                "title": "Provider requests",
                "content": "Provider requests preserve traceable source identity.",
                "status": "seedling",
                "source_refs": [source_ref],
                "relations": [],
                "confidence": "medium",
                "created_at": "2026-05-16T00:00:00Z",
                "updated_at": "2026-05-16T00:00:00Z",
                "schema_version": CURRENT_EXTRACTION_SCHEMA_VERSION,
            }
        ],
        "relation_candidates": [],
    }


if __name__ == "__main__":
    unittest.main()
