import unittest

from diamonddust.ai import (
    FakeProvider,
    ModelPolicyError,
    ProviderError,
    ProviderErrorType,
    ProviderRequest,
    ProviderResult,
    ProviderUsage,
)
from diamonddust.application import (
    ExtractUnitsProviderRequestSpec,
    ProviderExtractionError,
    build_extract_units_provider_request,
    generate_patch_from_extraction,
    run_extract_units_provider_orchestration,
)
from diamonddust.storage import ingest_markdown_text


CREATED_AT = "2026-05-16T00:00:00Z"


class ProviderExtractionOrchestratorTests(unittest.TestCase):
    def test_orchestrates_request_prompt_provider_validation_and_context(self) -> None:
        essay = _essay()
        spec = _spec()
        request = build_extract_units_provider_request(essay, spec)
        provider = FakeProvider(
            structured_output=_valid_output(request.input_payload),
            provider_request_id="provider_req_orchestrator_ab12cd",
            usage=ProviderUsage(
                input_tokens=13,
                output_tokens=21,
                total_tokens=34,
                retry_count=1,
            ),
        )

        run = run_extract_units_provider_orchestration(provider, essay, spec)

        self.assertTrue(run.is_valid, run.errors)
        self.assertEqual(run.request.run_id, "run_provider_orchestrator_ab12cd")
        self.assertEqual(run.rendered_prompt.source_input_id, essay.source_id)
        self.assertTrue(run.rendered_prompt.prompt_hash.startswith("sha256:"))
        self.assertEqual(run.run_log.validation_status.value, "passed")

        context = run.run_log_context.to_mapping()
        self.assertTrue(context["prompt_used"])
        self.assertEqual(context["source_input_id"], essay.source_id)
        self.assertEqual(context["prompt_hash"], run.rendered_prompt.prompt_hash)
        self.assertEqual(context["provider_request_id"], "provider_req_orchestrator_ab12cd")
        self.assertEqual(context["retry_count"], 1)
        self.assertEqual(
            context["token_usage"],
            {
                "input_tokens": 13,
                "output_tokens": 21,
                "total_tokens": 34,
            },
        )
        self.assertNotIn("system_prompt", context)
        self.assertNotIn("user_prompt", context)

        patch = generate_patch_from_extraction(
            run.validation_result.proposal,
            created_at=CREATED_AT,
        )
        self.assertTrue(patch.patch_id.startswith("patch_"))

    def test_provider_error_keeps_prompt_hash_and_fails_safely(self) -> None:
        error = ProviderError(
            error_type=ProviderErrorType.TIMEOUT,
            message="provider timed out",
            provider_request_id="provider_req_orchestrator_timeout_ab12cd",
            retry_count=2,
        )

        run = run_extract_units_provider_orchestration(
            FakeProvider(error=error),
            _essay(),
            _spec(),
        )

        self.assertFalse(run.is_valid)
        self.assertEqual(run.run_log.validation_status.value, "failed")
        self.assertEqual(run.errors, ("provider timeout: provider timed out",))
        context = run.run_log_context.to_mapping()
        self.assertTrue(context["prompt_used"])
        self.assertEqual(context["prompt_hash"], run.rendered_prompt.prompt_hash)
        self.assertEqual(
            context["provider_request_id"],
            "provider_req_orchestrator_timeout_ab12cd",
        )
        self.assertEqual(context["retry_count"], 2)

    def test_invalid_provider_output_fails_before_patch_generation(self) -> None:
        run = run_extract_units_provider_orchestration(
            FakeProvider(structured_output="not structured"),
            _essay(),
            _spec(),
        )

        self.assertFalse(run.is_valid)
        self.assertIsNone(run.validation_result.proposal)
        self.assertIn("structured mapping", run.errors[0])
        self.assertEqual(
            run.run_log_context.to_mapping()["prompt_hash"],
            run.rendered_prompt.prompt_hash,
        )

    def test_policy_guard_prevents_provider_execution(self) -> None:
        provider = _RecordingProvider()

        with self.assertRaises(ModelPolicyError):
            run_extract_units_provider_orchestration(
                provider,
                _essay(),
                _spec(real_provider_calls_enabled=True),
            )

        self.assertFalse(provider.called)

    def test_orchestrator_rejects_invalid_inputs(self) -> None:
        with self.assertRaises(ProviderExtractionError):
            run_extract_units_provider_orchestration(
                FakeProvider(structured_output={}),
                "not an essay",
                _spec(),
            )

        with self.assertRaises(ProviderExtractionError):
            run_extract_units_provider_orchestration(
                FakeProvider(structured_output={}),
                _essay(),
                "not a spec",
            )


class _RecordingProvider:
    def __init__(self) -> None:
        self.called = False

    def generate(self, request: ProviderRequest) -> ProviderResult:
        self.called = True
        return FakeProvider(structured_output={}).generate(request)


def _essay():
    return ingest_markdown_text(
        """---
id: raw_essay_provider_orchestrator_ab12cd
tags:
  - ai
  - provider
---
# Provider orchestrator

Provider orchestration keeps prompt rendering separate from provider execution.
""",
        source_path="00-inbox/provider-orchestrator.md",
        source_name="provider-orchestrator",
    )


def _spec(*, real_provider_calls_enabled: bool = False) -> ExtractUnitsProviderRequestSpec:
    return ExtractUnitsProviderRequestSpec(
        run_id="run_provider_orchestrator_ab12cd",
        provider="fake-provider",
        model="fake-structured-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        real_provider_calls_enabled=real_provider_calls_enabled,
    )


def _valid_output(payload) -> dict:
    source_ref = dict(payload["source_ref"])
    return {
        "source_input_id": payload["source_input_id"],
        "unit_candidates": [
            {
                "id": "unit_provider_orchestrator_ab12cd",
                "type": "concept",
                "title": "Provider orchestration",
                "content": "Provider orchestration composes request, prompt, provider, and validation boundaries.",
                "status": "seedling",
                "source_refs": [source_ref],
                "relations": [],
                "confidence": "medium",
                "created_at": CREATED_AT,
                "updated_at": CREATED_AT,
                "schema_version": "0.1.0",
            }
        ],
        "relation_candidates": [],
    }


if __name__ == "__main__":
    unittest.main()
