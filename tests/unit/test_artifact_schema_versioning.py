import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.ai import AIRunMetadata, validate_extraction_output
from diamonddust.application import (
    BlogMode,
    LocalTrialSpec,
    PatchReviewDecision,
    generate_blog_draft_from_review,
    generate_patch_from_extraction,
    review_patch,
    run_local_trial,
)
from diamonddust.storage import (
    ARTIFACT_SCHEMA_VERSION,
    render_ai_run_log_artifact,
    render_blog_draft_markdown,
    render_blog_quality_report,
    render_candidate_markdown,
    render_patch_json_artifact,
    render_patch_review_report,
    write_review_package,
)


CREATED_AT = "2026-05-11T00:00:00Z"
SOURCE_ID = "raw_essay_artifact_schema_ab12cd"


class ArtifactSchemaVersioningTests(unittest.TestCase):
    def test_json_artifacts_include_artifact_schema_version(self) -> None:
        result = validate_extraction_output(_valid_extraction_output(), _metadata())
        if result.proposal is None:
            raise AssertionError(result.errors)
        patch = generate_patch_from_extraction(result.proposal, created_at=CREATED_AT)

        run_artifact = render_ai_run_log_artifact(result.run_log, created_at=CREATED_AT)
        patch_artifact = render_patch_json_artifact(patch)

        self.assertEqual(
            json.loads(run_artifact.content)["artifact_schema_version"],
            ARTIFACT_SCHEMA_VERSION,
        )
        self.assertEqual(
            json.loads(patch_artifact.content)["artifact_schema_version"],
            ARTIFACT_SCHEMA_VERSION,
        )

    def test_markdown_review_artifacts_include_artifact_schema_version(self) -> None:
        patch = _valid_patch()
        candidate_export = render_candidate_markdown(patch)
        review_report = render_patch_review_report(
            patch,
            candidate_export=candidate_export,
        )

        self.assertIn(
            f"artifact_schema_version: \"{ARTIFACT_SCHEMA_VERSION}\"",
            candidate_export.files[0].content,
        )
        self.assertIn(
            f"Artifact schema version: `{ARTIFACT_SCHEMA_VERSION}`",
            review_report.content,
        )
        with TemporaryDirectory() as tmp:
            package = write_review_package(patch, vault_root=tmp)
            manifest_path = Path(tmp) / package.candidate_export.manifest_relative_path

            self.assertIn(
                f"Artifact schema version: `{ARTIFACT_SCHEMA_VERSION}`",
                manifest_path.read_text(encoding="utf-8"),
            )

    def test_blog_artifacts_include_artifact_schema_version(self) -> None:
        review_result = review_patch(_valid_patch(), PatchReviewDecision.ACCEPTED)
        package = generate_blog_draft_from_review(
            review_result,
            title="Artifact Schema Versions",
            mode=BlogMode.EXPLANATION,
            audience="maintainers",
            reader_problem="tracking persisted artifact shapes",
            draft_id="draft_artifact_schema_ab12cd",
            quality_report_id="report_draft_artifact_schema_ab12cd",
        )

        draft_artifact = render_blog_draft_markdown(package)
        quality_report = render_blog_quality_report(package)

        self.assertIn(
            f"artifact_schema_version: \"{ARTIFACT_SCHEMA_VERSION}\"",
            draft_artifact.content,
        )
        self.assertIn(
            f"Artifact schema version: `{ARTIFACT_SCHEMA_VERSION}`",
            quality_report.content,
        )

    def test_local_trial_written_artifacts_include_artifact_schema_version(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            essay_path = _write_essay(root)
            vault_root = root / "knowledge-vault"

            result = run_local_trial(
                LocalTrialSpec(
                    trial_id="trial_artifact_schema_ab12cd",
                    essay_path=essay_path.as_posix(),
                    extraction_output=_valid_extraction_output(),
                    blog_title="Artifact Schema Versions",
                    blog_mode=BlogMode.EXPLANATION,
                    audience="maintainers",
                    reader_problem="checking persisted artifact shapes",
                ),
                root=root,
                vault_root=vault_root,
                created_at=CREATED_AT,
            )

            self.assertTrue(result.passed)
            for relative_path in result.written_paths:
                content = (vault_root / relative_path).read_text(encoding="utf-8")
                self.assertTrue(
                    (
                        f"artifact_schema_version" in content
                        or f"Artifact schema version: `{ARTIFACT_SCHEMA_VERSION}`" in content
                    ),
                    relative_path,
                )


def _valid_patch():
    result = validate_extraction_output(_valid_extraction_output(), _metadata())
    if result.proposal is None:
        raise AssertionError(result.errors)
    return generate_patch_from_extraction(result.proposal, created_at=CREATED_AT)


def _metadata() -> AIRunMetadata:
    return AIRunMetadata(
        run_id="run_artifact_schema_ab12cd",
        task="extract_units",
        provider="test-provider",
        model="test-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        input_hash="sha256:inputhash",
    )


def _write_essay(root: Path) -> Path:
    inbox = root / "00-inbox"
    inbox.mkdir(parents=True)
    path = inbox / "artifact-schema.md"
    path.write_text(
        "---\n"
        f"id: {SOURCE_ID}\n"
        "---\n\n"
        "Artifact schema versions make trial outputs easier to compare.\n",
        encoding="utf-8",
    )
    return path


def _valid_extraction_output() -> dict:
    concept_id = "unit_artifact_schema_concept_ab12cd"
    claim_id = "unit_artifact_schema_claim_cd34ef"
    return {
        "source_input_id": SOURCE_ID,
        "unit_candidates": [
            _unit_data(
                id=concept_id,
                type="concept",
                title="Artifact schema versioning",
                content="Artifact schema versioning makes persisted outputs traceable.",
            ),
            _unit_data(
                id=claim_id,
                type="claim",
                title="Versioned artifacts are easier to migrate",
                content="Versioned artifacts are easier to migrate than unmarked files.",
            ),
        ],
        "relation_candidates": [
            {
                "source_id": claim_id,
                "relation_type": "supports",
                "target_id": concept_id,
                "confidence": "medium",
                "reason": "The claim supports artifact schema versioning.",
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
        "created_at": CREATED_AT,
        "updated_at": CREATED_AT,
        "schema_version": "0.1.0",
    }


def _source_ref_data() -> dict:
    return {
        "source_id": SOURCE_ID,
        "source_path": "00-inbox/artifact-schema.md",
        "source_span": "lines 5-5",
        "origin": "user_text",
        "line_start": 5,
        "line_end": 5,
        "content_hash": "sha256:source",
    }


if __name__ == "__main__":
    unittest.main()
