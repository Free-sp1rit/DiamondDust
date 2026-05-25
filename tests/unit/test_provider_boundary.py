import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.ai import (
    EXTRACTION_TASK,
    FakeProvider,
    ProviderBoundaryError,
    ProviderError,
    ProviderErrorType,
    ModelPolicyError,
    ProviderModelSettings,
    ProviderRequest,
    ProviderResult,
    ProviderUsage,
)
from diamonddust.application import (
    generate_patch_from_extraction,
    provider_run_log_context,
    run_provider_extraction,
)


CREATED_AT = "2026-05-16T00:00:00Z"
SOURCE_ID = "raw_essay_provider_boundary_ab12cd"


class ProviderBoundaryTests(unittest.TestCase):
    def test_provider_request_allows_extract_units_only(self) -> None:
        request = _request()

        self.assertEqual(request.task, EXTRACTION_TASK)
        self.assertEqual(request.provider, "fake-provider")
        self.assertEqual(request.model, "fake-structured-model")
        self.assertFalse(request.settings.real_provider_calls_enabled)
        self.assertFalse(request.settings.tool_calls_enabled)

        with self.assertRaises(ProviderBoundaryError):
            _request(task="suggest_relations")

    def test_provider_boundary_rejects_tool_execution_in_v0(self) -> None:
        with self.assertRaises(ProviderBoundaryError):
            ProviderModelSettings(
                provider="fake-provider",
                model="fake-structured-model",
                prompt_version="extract_units.v1",
                schema_version="0.1.0",
                tool_calls_enabled=True,
            )

    def test_fake_provider_returns_typed_response_without_persistence(self) -> None:
        provider = FakeProvider(
            structured_output=_valid_output(),
            usage=ProviderUsage(input_tokens=10, output_tokens=20, total_tokens=30),
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = provider.generate(_request())

            self.assertTrue(result.succeeded)
            self.assertIsNotNone(result.response)
            self.assertIsNone(result.error)
            self.assertTrue(result.response.output_hash.startswith("sha256:"))
            self.assertFalse(result.response.raw_output_persisted)
            self.assertEqual(list(root.iterdir()), [])

    def test_provider_extraction_validates_structured_output_before_patch_generation(self) -> None:
        run = run_provider_extraction(
            FakeProvider(
                structured_output=_valid_output(),
                provider_request_id="provider_req_boundary_ab12cd",
                usage=ProviderUsage(
                    input_tokens=11,
                    output_tokens=22,
                    total_tokens=33,
                    cost=0.12,
                    latency_ms=250.0,
                    retry_count=1,
                ),
            ),
            _request(),
        )

        self.assertTrue(run.is_valid, run.errors)
        self.assertIsNotNone(run.validation_result.proposal)
        self.assertEqual(run.run_log.validation_status.value, "passed")
        self.assertEqual(run.run_log.provider, "fake-provider")
        self.assertEqual(run.run_log.cost, 0.12)
        self.assertEqual(run.run_log.latency, 250.0)

        context = provider_run_log_context(run).to_mapping()
        self.assertEqual(context["provider_request_id"], "provider_req_boundary_ab12cd")
        self.assertEqual(context["retry_count"], 1)
        self.assertEqual(
            context["token_usage"],
            {
                "input_tokens": 11,
                "output_tokens": 22,
                "total_tokens": 33,
            },
        )

        patch = generate_patch_from_extraction(
            run.validation_result.proposal,
            created_at=CREATED_AT,
        )
        self.assertTrue(patch.patch_id.startswith("patch_"))

    def test_invalid_provider_output_fails_before_patch_generation(self) -> None:
        run = run_provider_extraction(
            FakeProvider(structured_output="free form output"),
            _request(),
        )

        self.assertFalse(run.is_valid)
        self.assertIsNone(run.validation_result.proposal)
        self.assertEqual(run.run_log.validation_status.value, "failed")
        self.assertIn("structured mapping", run.errors[0])

    def test_provider_extraction_binds_top_level_source_input_id_from_request(self) -> None:
        output = _valid_output()
        output["source_input_id"] = "raw_essay_provider_generated_wrong_id"

        run = run_provider_extraction(
            FakeProvider(structured_output=output),
            _request(),
        )

        self.assertTrue(run.is_valid, run.errors)
        self.assertIsNotNone(run.validation_result.proposal)
        self.assertEqual(run.validation_result.proposal.source_input_id, SOURCE_ID)
        self.assertEqual(run.run_log.validation_status.value, "passed")

    def test_provider_output_source_refs_must_match_request_source_input_id(self) -> None:
        output = _valid_output()
        output["source_input_id"] = "raw_essay_unrelated_source_cd34ef"
        output["unit_candidates"][0]["source_refs"][0][
            "source_id"
        ] = "raw_essay_unrelated_source_cd34ef"

        run = run_provider_extraction(
            FakeProvider(structured_output=output),
            _request(),
        )

        self.assertFalse(run.is_valid)
        self.assertIsNone(run.validation_result.proposal)
        self.assertEqual(run.run_log.validation_status.value, "failed")
        self.assertIn("must reference source_input_id", run.errors[0])

    def test_provider_error_fails_safely_and_records_failed_run_log(self) -> None:
        error = ProviderError(
            error_type=ProviderErrorType.TIMEOUT,
            message="provider timed out",
            provider_request_id="provider_req_timeout_ab12cd",
            retry_count=2,
        )
        run = run_provider_extraction(
            FakeProvider(error=error),
            _request(),
        )

        self.assertFalse(run.is_valid)
        self.assertIsNone(run.validation_result.proposal)
        self.assertEqual(run.run_log.validation_status.value, "failed")
        self.assertTrue(run.run_log.output_hash.startswith("sha256:"))
        self.assertEqual(run.errors, ("provider timeout: provider timed out",))
        self.assertTrue(error.should_retry)
        context = provider_run_log_context(run).to_mapping()
        self.assertEqual(context["provider_request_id"], "provider_req_timeout_ab12cd")
        self.assertEqual(context["retry_count"], 2)
        self.assertNotIn("token_usage", context)

    def test_unapproved_real_provider_call_fails_before_provider_execution(self) -> None:
        provider = _RecordingProvider()
        with self.assertRaises(ModelPolicyError):
            run_provider_extraction(
                provider,
                _request(settings=_settings(real_provider_calls_enabled=True)),
            )

        self.assertFalse(provider.called)

    def test_auth_errors_are_not_retryable_by_default(self) -> None:
        error = ProviderError(
            error_type=ProviderErrorType.AUTH_ERROR,
            message="bad credentials",
        )

        self.assertFalse(error.should_retry)


class _RecordingProvider:
    def __init__(self) -> None:
        self.called = False

    def generate(self, request: ProviderRequest) -> ProviderResult:
        self.called = True
        return FakeProvider(structured_output=_valid_output()).generate(request)


def _settings(*, real_provider_calls_enabled: bool = False) -> ProviderModelSettings:
    return ProviderModelSettings(
        provider="fake-provider",
        model="fake-structured-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        real_provider_calls_enabled=real_provider_calls_enabled,
    )


def _request(
    *,
    task: str = EXTRACTION_TASK,
    settings: ProviderModelSettings | None = None,
) -> ProviderRequest:
    return ProviderRequest(
        run_id="run_provider_boundary_ab12cd",
        task=task,
        input_hash="sha256:input",
        input_payload={"source_input_id": SOURCE_ID},
        settings=settings or _settings(),
    )


def _valid_output() -> dict:
    return {
        "source_input_id": SOURCE_ID,
        "unit_candidates": [
            {
                "id": "unit_provider_boundary_ab12cd",
                "type": "concept",
                "title": "Provider boundaries",
                "content": "Provider adapters return envelopes before validation.",
                "status": "seedling",
                "source_refs": [
                    {
                        "source_id": SOURCE_ID,
                        "source_path": "00-inbox/provider-boundary.md",
                        "source_span": "lines 1-3",
                        "origin": "user_text",
                        "line_start": 1,
                        "line_end": 3,
                        "content_hash": "sha256:source",
                    }
                ],
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
