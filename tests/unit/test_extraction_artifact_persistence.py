import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.ai import AIRunMetadata, validate_extraction_output
from diamonddust.storage import (
    AI_EXTRACTION_OUTPUTS_DIR,
    ExtractionArtifactContext,
    ExtractionArtifactPersistenceError,
    render_validated_extraction_artifact,
    validated_extraction_artifact_path,
    write_validated_extraction_artifact,
)


CREATED_AT = "2026-05-22T00:00:00Z"
SOURCE_ID = "raw_essay_extraction_artifact_ab12cd"


class ExtractionArtifactPersistenceTests(unittest.TestCase):
    def test_renders_validated_extraction_artifact_without_raw_output(self) -> None:
        result = validate_extraction_output(_valid_output(), _metadata())
        assert result.proposal is not None

        artifact = render_validated_extraction_artifact(
            result.proposal,
            created_at=CREATED_AT,
            context=ExtractionArtifactContext(
                stage_label="local_trial_artifact_pipeline",
                run_scope="provider_free_fixture",
                real_provider_call=False,
                fixture_driven=True,
                prompt_hash="sha256:prompt",
                not_validated=("real_llm_extraction_quality",),
            ),
        )
        data = json.loads(artifact.content)

        self.assertEqual(artifact.run_id, "run_extraction_artifact_ab12cd")
        self.assertEqual(
            artifact.relative_path,
            f"{AI_EXTRACTION_OUTPUTS_DIR}/run_extraction_artifact_ab12cd.json",
        )
        self.assertEqual(artifact.validation_status, "passed")
        self.assertFalse(artifact.formal_write_allowed)
        self.assertFalse(artifact.raw_provider_output_persisted)
        self.assertEqual(data["artifact_type"], "validated_extraction_output")
        self.assertEqual(data["artifact_schema_version"], "0.1.0")
        self.assertEqual(data["source_input_id"], SOURCE_ID)
        self.assertEqual(data["input_hash"], "sha256:input")
        self.assertTrue(data["output_hash"].startswith("sha256:"))
        self.assertEqual(data["validation_status"], "passed")
        self.assertEqual(data["unit_candidate_count"], 1)
        self.assertEqual(data["relation_candidate_count"], 0)
        self.assertEqual(data["unit_candidates"][0]["id"], "unit_extraction_artifact_ab12cd")
        self.assertFalse(data["boundaries"]["raw_provider_output_persisted"])
        self.assertFalse(data["boundaries"]["formal_write_allowed"])
        self.assertFalse(data["boundaries"]["patch_generation_performed"])
        self.assertFalse(data["boundaries"]["patch_acceptance"])
        self.assertFalse(data["boundaries"]["formal_write_performed"])
        self.assertFalse(data["boundaries"]["publication_performed"])
        self.assertTrue(data["requires_user_review"])
        self.assertFalse(data["real_provider_call"])
        self.assertTrue(data["fixture_driven"])
        self.assertIn("real_llm_extraction_quality", data["not_validated"])
        self.assertNotIn("raw_output", data)
        self.assertNotIn("raw_provider_response", data)
        self.assertNotIn("prompt_text", data)

    def test_writes_only_under_ai_suggestions(self) -> None:
        result = validate_extraction_output(_valid_output(), _metadata())
        assert result.proposal is not None
        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp)

            artifact = write_validated_extraction_artifact(
                result.proposal,
                vault_root=vault_root,
                created_at=CREATED_AT,
            )

            artifact_path = vault_root / artifact.relative_path
            formal_path = vault_root / "40-concepts" / f"{artifact.artifact_id}.json"
            self.assertTrue(artifact_path.exists())
            self.assertFalse(formal_path.exists())
            self.assertTrue(
                artifact_path.resolve().is_relative_to(
                    (vault_root / AI_EXTRACTION_OUTPUTS_DIR).resolve()
                )
            )

    def test_artifact_path_is_deterministic(self) -> None:
        result = validate_extraction_output(_valid_output(), _metadata())
        assert result.proposal is not None

        self.assertEqual(
            validated_extraction_artifact_path(result.proposal),
            f"{AI_EXTRACTION_OUTPUTS_DIR}/run_extraction_artifact_ab12cd.json",
        )

    def test_rejects_invalid_inputs(self) -> None:
        result = validate_extraction_output("free form", _metadata())

        with self.assertRaises(ExtractionArtifactPersistenceError):
            render_validated_extraction_artifact(
                result.proposal,  # type: ignore[arg-type]
                created_at=CREATED_AT,
            )

        valid = validate_extraction_output(_valid_output(), _metadata())
        assert valid.proposal is not None
        with self.assertRaises(ExtractionArtifactPersistenceError):
            render_validated_extraction_artifact(valid.proposal, created_at="")

        with self.assertRaises(ExtractionArtifactPersistenceError):
            ExtractionArtifactContext(real_provider_call="yes")  # type: ignore[arg-type]


def _metadata() -> AIRunMetadata:
    return AIRunMetadata(
        run_id="run_extraction_artifact_ab12cd",
        task="extract_units",
        provider="fixture-provider",
        model="fixture-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        input_hash="sha256:input",
    )


def _valid_output() -> dict:
    return {
        "source_input_id": SOURCE_ID,
        "unit_candidates": [
            {
                "id": "unit_extraction_artifact_ab12cd",
                "type": "concept",
                "title": "Validated extraction artifact",
                "content": "Validated extraction artifacts preserve typed proposals.",
                "status": "seedling",
                "source_refs": [_source_ref_data()],
                "relations": [],
                "confidence": "medium",
                "created_at": CREATED_AT,
                "updated_at": CREATED_AT,
                "schema_version": "0.1.0",
            }
        ],
        "relation_candidates": [],
    }


def _source_ref_data() -> dict:
    return {
        "source_id": SOURCE_ID,
        "source_path": "00-inbox/extraction-artifact.md",
        "source_span": "lines 1-3",
        "origin": "user_text",
        "line_start": 1,
        "line_end": 3,
        "content_hash": "sha256:source",
    }


if __name__ == "__main__":
    unittest.main()
