import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.ai import AIRunMetadata, validate_extraction_output
from diamonddust.application import PatchReviewError, generate_patch_from_extraction
from diamonddust.domain import KnowledgePatch, PatchOperation, PatchOperationType
from diamonddust.storage import (
    AI_CANDIDATE_NOTES_DIR,
    CandidateMarkdownExportContext,
    CandidateMarkdownError,
    render_candidate_markdown,
    render_candidate_manifest_content,
    write_candidate_markdown_export,
)


CREATED_AT = "2026-05-11T00:00:00Z"


class CandidateMarkdownExportTests(unittest.TestCase):
    def test_renders_candidate_markdown_files_from_patch(self) -> None:
        patch = _valid_patch()

        export = render_candidate_markdown(patch)

        self.assertEqual(export.manifest.patch_id, patch.patch_id)
        self.assertEqual(export.manifest.file_count, 2)
        self.assertEqual(export.manifest.relation_count, 1)
        self.assertEqual(
            export.manifest.candidate_root,
            f"{AI_CANDIDATE_NOTES_DIR}/{patch.patch_id}",
        )
        self.assertEqual(
            export.files[0].relative_path,
            (
                f"{AI_CANDIDATE_NOTES_DIR}/{patch.patch_id}/"
                "40-concepts/unit_20260511_candidate_markdown_ab12cd.md"
            ),
        )
        self.assertIn("formal_write: false", export.files[0].content)
        self.assertIn("requires_user_review: true", export.files[0].content)
        self.assertIn("source_refs:", export.files[0].content)
        self.assertIn("raw_essay_20260511_candidate_ab12cd", export.files[0].content)
        self.assertIn("# Candidate Markdown", export.files[0].content)
        manifest_content = render_candidate_manifest_content(export.manifest)
        self.assertIn("## Candidate Preview Boundary", manifest_content)
        self.assertIn("They are not formal vault notes.", manifest_content)
        self.assertIn("## Patch Operation Source of Truth", manifest_content)
        self.assertIn("raw KnowledgePatch JSON is the source of truth", manifest_content)
        self.assertNotIn("## Fixture SourceRef Scope", manifest_content)

    def test_candidate_note_includes_patch_relation_for_source_unit(self) -> None:
        export = render_candidate_markdown(_valid_patch())
        claim_file = export.files[1]

        self.assertIn("relations:", claim_file.content)
        self.assertIn('relation_type: "supports"', claim_file.content)
        self.assertIn(
            'target_id: "unit_20260511_candidate_markdown_ab12cd"',
            claim_file.content,
        )

    def test_writes_candidate_files_only_under_ai_suggestions(self) -> None:
        patch = _valid_patch()
        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp)

            export = write_candidate_markdown_export(patch, vault_root=vault_root)

            manifest_path = vault_root / export.manifest_relative_path
            candidate_path = vault_root / export.files[0].relative_path
            formal_path = vault_root / export.files[0].target_path

            self.assertTrue(manifest_path.exists())
            self.assertTrue(candidate_path.exists())
            self.assertFalse(formal_path.exists())
            self.assertTrue(
                candidate_path.resolve().is_relative_to(
                    (vault_root / AI_CANDIDATE_NOTES_DIR).resolve()
                )
            )
            self.assertIn("Candidate Markdown Export", manifest_path.read_text())

    def test_fixture_source_ref_scope_can_be_added_to_manifest(self) -> None:
        export = render_candidate_markdown(
            _valid_patch(),
            context=CandidateMarkdownExportContext(fixture_source_ref_scope=True),
        )

        manifest_content = render_candidate_manifest_content(export.manifest)

        self.assertIn("## Fixture SourceRef Scope", manifest_content)
        self.assertIn("fixture-level source references", manifest_content)
        self.assertIn("synthetic placeholders", manifest_content)
        self.assertIn("real parser source-span accuracy", manifest_content)

    def test_unsafe_patch_id_cannot_be_used_for_export_path(self) -> None:
        patch = KnowledgePatch(
            patch_id="../escape",
            created_at=CREATED_AT,
            source_input_ids=("raw_essay_20260511_candidate_ab12cd",),
            operations=_valid_patch().operations,
            risks=("review required",),
            requires_user_review=True,
        )

        with self.assertRaises(CandidateMarkdownError):
            render_candidate_markdown(patch)

    def test_relation_only_patch_has_no_candidate_note_to_render(self) -> None:
        valid_patch = _valid_patch()
        relation = valid_patch.operations[2].relation
        patch = KnowledgePatch(
            patch_id="patch_relation_only",
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

        with self.assertRaises(CandidateMarkdownError):
            render_candidate_markdown(patch)

    def test_export_rejects_patch_with_ai_suggestion_target_path(self) -> None:
        valid_patch = _valid_patch()
        unit = valid_patch.operations[0].unit
        patch = KnowledgePatch(
            patch_id="patch_bad_candidate_target",
            created_at=CREATED_AT,
            source_input_ids=valid_patch.source_input_ids,
            operations=(
                PatchOperation(
                    operation_type=PatchOperationType.CREATE_NOTE,
                    target_path="_ai_suggestions/bad.md",
                    unit=unit,
                ),
            ),
            risks=("review required",),
            requires_user_review=True,
        )

        with self.assertRaises(PatchReviewError):
            render_candidate_markdown(patch)


def _valid_patch() -> KnowledgePatch:
    proposal = _valid_proposal()
    return generate_patch_from_extraction(proposal, created_at=CREATED_AT)


def _valid_proposal():
    result = validate_extraction_output(_valid_output(), _metadata())
    if result.proposal is None:
        raise AssertionError(result.errors)
    return result.proposal


def _metadata() -> AIRunMetadata:
    return AIRunMetadata(
        run_id="run_20260511_extract_candidate_ab12cd",
        task="extract_units",
        provider="test-provider",
        model="test-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        input_hash="sha256:inputhash",
    )


def _valid_output() -> dict:
    concept_id = "unit_20260511_candidate_markdown_ab12cd"
    claim_id = "unit_20260511_candidate_claim_cd34ef"
    return {
        "source_input_id": "raw_essay_20260511_candidate_ab12cd",
        "unit_candidates": [
            _unit_data(
                id=concept_id,
                type="concept",
                title="Candidate Markdown",
                content="Candidate notes are rendered before formal vault apply.",
            ),
            _unit_data(
                id=claim_id,
                type="claim",
                title="Candidate exports protect review",
                content="Candidate exports keep AI output in reviewable working areas.",
            ),
        ],
        "relation_candidates": [
            {
                "source_id": claim_id,
                "relation_type": "supports",
                "target_id": concept_id,
                "confidence": "medium",
                "reason": "The claim supports the candidate Markdown concept.",
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
        "source_id": "raw_essay_20260511_candidate_ab12cd",
        "source_path": "00-inbox/candidate.md",
        "source_span": "lines 1-3",
        "origin": "user_text",
        "line_start": 1,
        "line_end": 3,
        "content_hash": "sha256:source",
    }


if __name__ == "__main__":
    unittest.main()
