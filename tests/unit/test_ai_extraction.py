import unittest

from diamonddust.ai import (
    AIRunMetadata,
    AIValidationStatus,
    ExtractionValidationError,
    compute_ai_output_hash,
    validate_extraction_output,
)
from diamonddust.domain import KnowledgeUnit, Relation


class AIExtractionProposalTests(unittest.TestCase):
    def test_valid_structured_output_becomes_typed_proposal(self) -> None:
        result = validate_extraction_output(_valid_output(), _metadata())

        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, ())
        self.assertIsNotNone(result.proposal)
        assert result.proposal is not None
        self.assertIsInstance(result.proposal.unit_candidates[0], KnowledgeUnit)
        self.assertIsInstance(result.proposal.relation_candidates[0], Relation)
        self.assertEqual(result.run_log.validation_status, AIValidationStatus.PASSED)
        self.assertEqual(result.run_log.prompt_version, "extract_units.v1")
        self.assertEqual(result.run_log.schema_version, "0.1.0")
        self.assertEqual(result.run_log.provider, "test-provider")
        self.assertEqual(result.run_log.model, "test-model")
        self.assertTrue(result.run_log.output_hash.startswith("sha256:"))

    def test_run_log_can_be_serialized_without_raw_output(self) -> None:
        result = validate_extraction_output(_valid_output(), _metadata(cost=0.01, latency=1.25))

        log = result.run_log.to_mapping()

        self.assertEqual(log["run_id"], "run_20260510_extract_ab12cd")
        self.assertEqual(log["task"], "extract_units")
        self.assertEqual(log["prompt_version"], "extract_units.v1")
        self.assertEqual(log["cost"], 0.01)
        self.assertEqual(log["latency"], 1.25)
        self.assertEqual(log["validation_status"], "passed")
        self.assertNotIn("raw_output", log)

    def test_free_form_output_fails_safely(self) -> None:
        result = validate_extraction_output(
            "Here are some ideas, but not structured output.",
            _metadata(),
        )

        self.assertFalse(result.is_valid)
        self.assertIsNone(result.proposal)
        self.assertEqual(result.run_log.validation_status, AIValidationStatus.FAILED)
        self.assertIn("structured mapping", result.errors[0])
        self.assertTrue(result.run_log.output_hash.startswith("sha256:"))

    def test_invalid_domain_candidate_fails_safely(self) -> None:
        output = _valid_output()
        output["unit_candidates"][0]["type"] = "not_a_unit_type"

        result = validate_extraction_output(output, _metadata())

        self.assertFalse(result.is_valid)
        self.assertIsNone(result.proposal)
        self.assertEqual(result.run_log.validation_status, AIValidationStatus.FAILED)
        self.assertIn("unsupported value", result.errors[0])

    def test_unit_candidates_must_preserve_source_refs(self) -> None:
        output = _valid_output()
        output["unit_candidates"][0]["source_refs"] = []

        result = validate_extraction_output(output, _metadata())

        self.assertFalse(result.is_valid)
        self.assertIsNone(result.proposal)
        self.assertEqual(result.run_log.validation_status, AIValidationStatus.FAILED)
        self.assertIn("preserve source_refs", result.errors[0])

    def test_hash_is_deterministic_for_structured_output(self) -> None:
        left = {"b": [2, 3], "a": {"nested": True}}
        right = {"a": {"nested": True}, "b": [2, 3]}

        self.assertEqual(compute_ai_output_hash(left), compute_ai_output_hash(right))

    def test_metadata_requires_prompt_version(self) -> None:
        with self.assertRaises(ExtractionValidationError):
            AIRunMetadata(
                run_id="run_1",
                task="extract_units",
                provider="test-provider",
                model="test-model",
                prompt_version="",
                schema_version="0.1.0",
                input_hash="sha256:input",
            )

    def test_wrong_task_metadata_fails_safely(self) -> None:
        metadata = AIRunMetadata(
            run_id="run_1",
            task="review_blog_draft",
            provider="test-provider",
            model="test-model",
            prompt_version="review_blog_draft.v1",
            schema_version="0.1.0",
            input_hash="sha256:input",
        )

        result = validate_extraction_output(_valid_output(), metadata)

        self.assertFalse(result.is_valid)
        self.assertIsNone(result.proposal)
        self.assertEqual(result.run_log.validation_status, AIValidationStatus.FAILED)
        self.assertIn("extract_units", result.errors[0])


def _metadata(cost: float | None = None, latency: float | None = None) -> AIRunMetadata:
    return AIRunMetadata(
        run_id="run_20260510_extract_ab12cd",
        task="extract_units",
        provider="test-provider",
        model="test-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        input_hash="sha256:inputhash",
        cost=cost,
        latency=latency,
    )


def _valid_output() -> dict:
    return {
        "source_input_id": "raw_essay_20260510_gate4_ab12cd",
        "unit_candidates": [
            _unit_data(
                id="unit_20260510_structured_output_ab12cd",
                type="concept",
                title="Structured AI output",
                content="AI extraction output must be structured before validation.",
            ),
            _unit_data(
                id="unit_20260510_validation_boundary_cd34ef",
                type="claim",
                title="Validation boundary protects internal data",
                content="Free-form AI output should not become internal data.",
            ),
        ],
        "relation_candidates": [
            {
                "source_id": "unit_20260510_validation_boundary_cd34ef",
                "relation_type": "depends_on",
                "target_id": "unit_20260510_structured_output_ab12cd",
                "confidence": "medium",
                "reason": "The claim depends on structured output validation.",
            }
        ],
    }


def _unit_data(*, id: str, type: str, title: str, content: str) -> dict:
    return {
        "id": id,
        "type": type,
        "title": title,
        "content": content,
        "status": "seedling",
        "source_refs": [_source_ref_data()],
        "relations": [],
        "confidence": "medium",
        "created_at": "2026-05-10T00:00:00Z",
        "updated_at": "2026-05-10T00:00:00Z",
        "schema_version": "0.1.0",
    }


def _source_ref_data() -> dict:
    return {
        "source_id": "raw_essay_20260510_gate4_ab12cd",
        "source_path": "00-inbox/gate4.md",
        "source_span": "lines 1-3",
        "origin": "user_text",
        "line_start": 1,
        "line_end": 3,
        "content_hash": "sha256:source",
    }


if __name__ == "__main__":
    unittest.main()
