import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.ai import AIRunMetadata, validate_extraction_output
from diamonddust.application import generate_patch_from_extraction
from diamonddust.domain import KnowledgePatch, PatchOperation, PatchOperationType
from diamonddust.storage import (
    AI_CANDIDATE_NOTES_DIR,
    AI_PATCH_REVIEW_REPORTS_DIR,
    AI_PATCH_SUGGESTIONS_DIR,
    ReviewPackageError,
    render_patch_json_artifact,
    write_review_package,
)


CREATED_AT = "2026-05-11T00:00:00Z"


class ReviewPackagePersistenceTests(unittest.TestCase):
    def test_renders_patch_json_artifact_from_valid_patch(self) -> None:
        patch = _valid_patch()

        artifact = render_patch_json_artifact(patch)
        data = json.loads(artifact.content)

        self.assertEqual(artifact.patch_id, patch.patch_id)
        self.assertEqual(artifact.validation_status, "passed")
        self.assertEqual(
            artifact.relative_path,
            f"{AI_PATCH_SUGGESTIONS_DIR}/{patch.patch_id}.json",
        )
        self.assertEqual(data["patch_id"], patch.patch_id)
        self.assertEqual(data["validation_status"], "passed")
        self.assertFalse(data["formal_write_allowed"])
        self.assertTrue(data["requires_user_review"])
        self.assertEqual(len(data["operations"]), 3)
        self.assertEqual(data["operations"][0]["unit"]["type"], "concept")
        self.assertEqual(data["operations"][2]["relation"]["relation_type"], "supports")

    def test_writes_full_review_package_without_formal_vault_mutation(self) -> None:
        patch = _valid_patch()
        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp)

            package = write_review_package(patch, vault_root=vault_root)

            patch_path = vault_root / package.patch_artifact.relative_path
            report_path = vault_root / package.review_report.relative_path
            candidate_paths = [
                vault_root / file.relative_path for file in package.candidate_export.files
            ]
            candidate_manifest_path = vault_root / package.candidate_export.manifest_relative_path
            formal_path = vault_root / patch.operations[0].target_path

            self.assertTrue(patch_path.exists())
            self.assertTrue(report_path.exists())
            self.assertTrue(candidate_manifest_path.exists())
            self.assertTrue(all(path.exists() for path in candidate_paths))
            self.assertFalse(formal_path.exists())
            self.assertFalse(package.formal_write_allowed)
            self.assertIn(package.patch_artifact.relative_path, package.written_paths)
            self.assertIn(package.review_report.relative_path, package.written_paths)
            self.assertIn(
                package.candidate_export.files[0].relative_path,
                package.written_paths,
            )
            self.assertTrue(
                patch_path.resolve().is_relative_to(
                    (vault_root / AI_PATCH_SUGGESTIONS_DIR).resolve()
                )
            )
            self.assertTrue(
                report_path.resolve().is_relative_to(
                    (vault_root / AI_PATCH_REVIEW_REPORTS_DIR).resolve()
                )
            )
            self.assertTrue(
                candidate_paths[0].resolve().is_relative_to(
                    (vault_root / AI_CANDIDATE_NOTES_DIR).resolve()
                )
            )

    def test_package_report_links_written_candidate_note_paths(self) -> None:
        patch = _valid_patch()
        with TemporaryDirectory() as tmp:
            package = write_review_package(patch, vault_root=tmp)

        first_candidate_path = package.candidate_export.files[0].relative_path

        self.assertIn(first_candidate_path, package.review_report.content)
        self.assertIn(first_candidate_path, package.written_paths)

    def test_relation_only_patch_writes_patch_and_report_without_candidate_notes(self) -> None:
        valid_patch = _valid_patch()
        relation = valid_patch.operations[2].relation
        patch = KnowledgePatch(
            patch_id="patch_relation_only_package",
            created_at=CREATED_AT,
            source_input_ids=valid_patch.source_input_ids,
            operations=(
                PatchOperation(
                    operation_type=PatchOperationType.ADD_RELATION,
                    relation=relation,
                ),
            ),
            risks=("review required",),
            requires_user_review=True,
        )
        with TemporaryDirectory() as tmp:
            package = write_review_package(patch, vault_root=tmp)
            root = Path(tmp)

            self.assertTrue((root / package.patch_artifact.relative_path).exists())
            self.assertTrue((root / package.review_report.relative_path).exists())

        self.assertIsNone(package.candidate_export)
        self.assertEqual(len(package.written_paths), 2)
        self.assertIn("## Candidate Notes\n- none", package.review_report.content)

    def test_unsafe_patch_id_cannot_be_persisted(self) -> None:
        patch = KnowledgePatch(
            patch_id="../escape",
            created_at=CREATED_AT,
            source_input_ids=("raw_essay_20260511_package_ab12cd",),
            operations=_valid_patch().operations,
            risks=("review required",),
            requires_user_review=True,
        )

        with self.assertRaises(ReviewPackageError):
            render_patch_json_artifact(patch)


def _valid_patch() -> KnowledgePatch:
    proposal = _valid_proposal()
    return generate_patch_from_extraction(
        proposal,
        created_at=CREATED_AT,
        patch_id="patch_review_package_ab12cd",
    )


def _valid_proposal():
    result = validate_extraction_output(_valid_output(), _metadata())
    if result.proposal is None:
        raise AssertionError(result.errors)
    return result.proposal


def _metadata() -> AIRunMetadata:
    return AIRunMetadata(
        run_id="run_20260511_extract_package_ab12cd",
        task="extract_units",
        provider="test-provider",
        model="test-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        input_hash="sha256:inputhash",
    )


def _valid_output() -> dict:
    concept_id = "unit_20260511_package_concept_ab12cd"
    claim_id = "unit_20260511_package_claim_cd34ef"
    return {
        "source_input_id": "raw_essay_20260511_package_ab12cd",
        "unit_candidates": [
            _unit_data(
                id=concept_id,
                type="concept",
                title="Review Package",
                content="A review package groups patch artifacts before acceptance.",
            ),
            _unit_data(
                id=claim_id,
                type="claim",
                title="Packages keep review artifacts aligned",
                content="A package keeps patch JSON, candidate notes, and reports together.",
            ),
        ],
        "relation_candidates": [
            {
                "source_id": claim_id,
                "relation_type": "supports",
                "target_id": concept_id,
                "confidence": "medium",
                "reason": "The claim supports the review package concept.",
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
        "source_id": "raw_essay_20260511_package_ab12cd",
        "source_path": "00-inbox/package.md",
        "source_span": "lines 1-3",
        "origin": "user_text",
        "line_start": 1,
        "line_end": 3,
        "content_hash": "sha256:source",
    }


if __name__ == "__main__":
    unittest.main()
