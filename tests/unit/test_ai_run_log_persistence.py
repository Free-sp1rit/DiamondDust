import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.ai import AIRunMetadata, AIValidationStatus, validate_extraction_output
from diamonddust.storage import (
    AI_RUNS_DIR,
    AIRunLogArtifactContext,
    AIRunMetricsScope,
    AIRunOutputArtifact,
    AIRunTokenUsage,
    AIRunLogPersistenceError,
    render_ai_run_log_artifact,
    write_ai_run_log_artifact,
)


CREATED_AT = "2026-05-11T00:00:00Z"


class AIRunLogPersistenceTests(unittest.TestCase):
    def test_renders_passed_run_log_artifact_without_raw_output(self) -> None:
        result = validate_extraction_output(_valid_output(), _metadata())

        artifact = render_ai_run_log_artifact(result.run_log, created_at=CREATED_AT)
        data = json.loads(artifact.content)

        self.assertEqual(artifact.run_id, "run_20260511_extract_ai_run_ab12cd")
        self.assertEqual(artifact.relative_path, f"{AI_RUNS_DIR}/{artifact.run_id}.json")
        self.assertEqual(artifact.validation_status, "passed")
        self.assertEqual(data["artifact_type"], "ai_run_log")
        self.assertEqual(data["run_id"], artifact.run_id)
        self.assertEqual(data["task"], "extract_units")
        self.assertEqual(data["provider"], "test-provider")
        self.assertEqual(data["model"], "test-model")
        self.assertEqual(data["prompt_version"], "extract_units.v1")
        self.assertEqual(data["schema_version"], "0.1.0")
        self.assertEqual(data["input_hash"], "sha256:inputhash")
        self.assertTrue(data["output_hash"].startswith("sha256:"))
        self.assertEqual(data["validation_status"], "passed")
        self.assertEqual(data["created_at"], CREATED_AT)
        self.assertNotIn("raw_output", data)
        self.assertNotIn("run_scope", data)
        self.assertNotIn("real_provider_call", data)
        self.assertNotIn("fixture_driven", data)
        self.assertNotIn("metrics_scope", data)

    def test_renders_failed_run_log_artifact(self) -> None:
        result = validate_extraction_output("free form output", _metadata())

        artifact = render_ai_run_log_artifact(result.run_log, created_at=CREATED_AT)
        data = json.loads(artifact.content)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.run_log.validation_status, AIValidationStatus.FAILED)
        self.assertEqual(artifact.validation_status, "failed")
        self.assertEqual(data["validation_status"], "failed")
        self.assertTrue(data["output_hash"].startswith("sha256:"))

    def test_optional_cache_metadata_is_preserved(self) -> None:
        result = validate_extraction_output(_valid_output(), _metadata(cost=0.12, latency=2.5))

        artifact = render_ai_run_log_artifact(
            result.run_log,
            created_at=CREATED_AT,
            knowledge_base_snapshot_hash="sha256:kb",
            cache_key="cache_extract_units_abc123",
        )
        data = json.loads(artifact.content)

        self.assertEqual(data["cost"], 0.12)
        self.assertEqual(data["latency"], 2.5)
        self.assertEqual(data["knowledge_base_snapshot_hash"], "sha256:kb")
        self.assertEqual(data["cache_key"], "cache_extract_units_abc123")

    def test_optional_artifact_context_is_preserved(self) -> None:
        result = validate_extraction_output(_valid_output(), _metadata())

        artifact = render_ai_run_log_artifact(
            result.run_log,
            created_at=CREATED_AT,
            context=AIRunLogArtifactContext(
                trial_id="trial_ai_run_ab12cd",
                stage_label="local_trial_artifact_pipeline",
                run_scope="provider_free_fixture",
                real_provider_call=False,
                fixture_driven=True,
                prompt_used=False,
                metrics_scope=AIRunMetricsScope(
                    cost_applicable=False,
                    latency_applicable=False,
                    reason="provider_free_local_trial",
                ),
                source_input_id="raw_essay_20260511_ai_run_ab12cd",
                output_artifacts=(
                    AIRunOutputArtifact(
                        artifact_type="local_trial_feedback_report",
                        path="_ai_reports/local-trials/trial_ai_run_ab12cd.md",
                    ),
                ),
                not_validated=(
                    "real_llm_extraction_quality",
                    "provider_latency",
                    "provider_cost",
                ),
                provider_request_id="provider_req_ai_run_ab12cd",
                retry_count=2,
                token_usage=AIRunTokenUsage(
                    input_tokens=10,
                    output_tokens=20,
                    total_tokens=30,
                ),
            ),
        )
        data = json.loads(artifact.content)

        self.assertEqual(data["trial_id"], "trial_ai_run_ab12cd")
        self.assertEqual(data["stage_label"], "local_trial_artifact_pipeline")
        self.assertEqual(data["run_scope"], "provider_free_fixture")
        self.assertFalse(data["real_provider_call"])
        self.assertTrue(data["fixture_driven"])
        self.assertFalse(data["prompt_used"])
        self.assertEqual(
            data["metrics_scope"],
            {
                "cost_applicable": False,
                "latency_applicable": False,
                "reason": "provider_free_local_trial",
            },
        )
        self.assertEqual(data["source_input_id"], "raw_essay_20260511_ai_run_ab12cd")
        self.assertEqual(
            data["output_artifacts"],
            [
                {
                    "artifact_type": "local_trial_feedback_report",
                    "path": "_ai_reports/local-trials/trial_ai_run_ab12cd.md",
                }
            ],
        )
        self.assertIn("real_llm_extraction_quality", data["not_validated"])
        self.assertIn("provider_latency", data["not_validated"])
        self.assertIn("provider_cost", data["not_validated"])
        self.assertEqual(data["provider_request_id"], "provider_req_ai_run_ab12cd")
        self.assertEqual(data["retry_count"], 2)
        self.assertEqual(
            data["token_usage"],
            {
                "input_tokens": 10,
                "output_tokens": 20,
                "total_tokens": 30,
            },
        )

    def test_writes_run_log_only_under_ai_runs(self) -> None:
        result = validate_extraction_output(_valid_output(), _metadata())
        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp)

            artifact = write_ai_run_log_artifact(
                result.run_log,
                vault_root=vault_root,
                created_at=CREATED_AT,
            )

            run_path = vault_root / artifact.relative_path
            formal_path = vault_root / "00-inbox" / f"{result.run_log.run_id}.json"

            self.assertTrue(run_path.exists())
            self.assertFalse(formal_path.exists())
            self.assertTrue(
                run_path.resolve().is_relative_to((vault_root / AI_RUNS_DIR).resolve())
            )
            self.assertEqual(json.loads(run_path.read_text())["run_id"], result.run_log.run_id)

    def test_unsafe_run_id_cannot_be_persisted(self) -> None:
        run_log = validate_extraction_output(
            _valid_output(),
            _metadata(run_id="../escape"),
        ).run_log

        with self.assertRaises(AIRunLogPersistenceError):
            render_ai_run_log_artifact(run_log, created_at=CREATED_AT)

    def test_output_artifact_paths_must_stay_in_ai_working_areas(self) -> None:
        with self.assertRaises(AIRunLogPersistenceError):
            AIRunOutputArtifact(
                artifact_type="formal_note",
                path="40-concepts/unit_ai_run_ab12cd.md",
            )

    def test_provider_metadata_context_is_validated(self) -> None:
        with self.assertRaises(AIRunLogPersistenceError):
            AIRunLogArtifactContext(retry_count=-1)

        with self.assertRaises(AIRunLogPersistenceError):
            AIRunTokenUsage()

    def test_created_at_is_required(self) -> None:
        result = validate_extraction_output(_valid_output(), _metadata())

        with self.assertRaises(AIRunLogPersistenceError):
            render_ai_run_log_artifact(result.run_log, created_at="")


def _metadata(
    *,
    run_id: str = "run_20260511_extract_ai_run_ab12cd",
    cost: float | None = None,
    latency: float | None = None,
) -> AIRunMetadata:
    return AIRunMetadata(
        run_id=run_id,
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
        "source_input_id": "raw_essay_20260511_ai_run_ab12cd",
        "unit_candidates": [
            {
                "id": "unit_20260511_ai_run_concept_ab12cd",
                "type": "concept",
                "title": "AI run logs",
                "content": "AI run logs make validation traceable.",
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
        "source_id": "raw_essay_20260511_ai_run_ab12cd",
        "source_path": "00-inbox/ai-run.md",
        "source_span": "lines 1-3",
        "origin": "user_text",
        "line_start": 1,
        "line_end": 3,
        "content_hash": "sha256:source",
    }


if __name__ == "__main__":
    unittest.main()
