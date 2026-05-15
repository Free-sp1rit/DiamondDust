import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.ai import AIRunMetadata, validate_extraction_output
from diamonddust.application import generate_patch_from_extraction
from diamonddust.domain import KnowledgePatch, PatchOperation, PatchOperationType
from diamonddust.storage import (
    AI_PATCH_REVIEW_REPORTS_DIR,
    PatchReviewReportContext,
    ReviewReportError,
    render_candidate_markdown,
    render_patch_review_report,
    write_patch_review_report,
)


CREATED_AT = "2026-05-11T00:00:00Z"


class ReviewReportRenderingTests(unittest.TestCase):
    def test_renders_review_report_from_patch_and_candidate_notes(self) -> None:
        patch = _valid_patch()

        report = render_patch_review_report(patch)

        self.assertEqual(report.patch_id, patch.patch_id)
        self.assertEqual(report.relative_path, f"{AI_PATCH_REVIEW_REPORTS_DIR}/{patch.patch_id}.md")
        self.assertEqual(report.diff_line_count, 3)
        self.assertEqual(report.candidate_file_count, 2)
        self.assertEqual(report.rollback_step_count, 3)
        self.assertFalse(report.formal_write_allowed)
        self.assertTrue(report.requires_user_review)
        self.assertIn("# Patch Review Report", report.content)
        self.assertTrue(report.content.startswith("---\n"))
        self.assertIn("artifact_type: patch_review_report", report.content)
        self.assertIn(f'patch_id: "{patch.patch_id}"', report.content)
        self.assertIn("source_input_ids:", report.content)
        self.assertIn("formal_write: false", report.content)
        self.assertIn("formal_write: false", report.content)
        self.assertIn("requires_user_review: true", report.content)
        self.assertIn("patch_acceptance: false", report.content)
        self.assertIn('decision_status: "pending"', report.content)
        self.assertIn("## Patch Diff", report.content)
        self.assertIn("create note", report.content)
        self.assertIn("add relation", report.content)
        self.assertIn("## Suggested Review Order", report.content)
        self.assertIn("Inspect the raw KnowledgePatch JSON", report.content)
        self.assertIn("## Candidate Notes", report.content)
        self.assertIn("_ai_suggestions/candidate-notes/", report.content)
        self.assertIn("## Rollback Plan", report.content)
        self.assertIn("preview-level only", report.content)
        self.assertIn("delete created note", report.content)
        self.assertIn("## Review Decision Prompt", report.content)
        self.assertIn("does not record formal patch acceptance", report.content)
        self.assertIn("recommend accept in a separate decision flow", report.content)
        self.assertNotIn("## Review Decision\n", report.content)

    def test_uses_explicit_candidate_export_when_provided(self) -> None:
        patch = _valid_patch()
        candidate_export = render_candidate_markdown(patch)

        report = render_patch_review_report(patch, candidate_export=candidate_export)

        self.assertEqual(report.candidate_file_count, candidate_export.manifest.file_count)
        self.assertIn(candidate_export.files[0].relative_path, report.content)

    def test_local_trial_context_adds_fixture_review_scope(self) -> None:
        patch = _valid_patch()

        report = render_patch_review_report(
            patch,
            context=PatchReviewReportContext(
                trial_id="trial_report_ab12cd",
                review_scope="provider_free_fixture",
                fixture_driven=True,
            ),
        )

        self.assertIn('trial_id: "trial_report_ab12cd"', report.content)
        self.assertIn('review_scope: "provider_free_fixture"', report.content)
        self.assertIn("fixture-driven previews", report.content)
        self.assertIn("real LLM extraction quality", report.content)
        self.assertIn("real parser source-span accuracy", report.content)

    def test_rejects_candidate_export_for_different_patch(self) -> None:
        patch = _valid_patch()
        other_patch = _valid_patch(patch_id="patch_other_report")
        candidate_export = render_candidate_markdown(other_patch)

        with self.assertRaises(ReviewReportError):
            render_patch_review_report(patch, candidate_export=candidate_export)

    def test_writes_report_only_under_ai_reports(self) -> None:
        patch = _valid_patch()
        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp)

            report = write_patch_review_report(patch, vault_root=vault_root)

            report_path = vault_root / report.relative_path
            formal_path = vault_root / patch.operations[0].target_path

            self.assertTrue(report_path.exists())
            self.assertFalse(formal_path.exists())
            self.assertTrue(
                report_path.resolve().is_relative_to(
                    (vault_root / AI_PATCH_REVIEW_REPORTS_DIR).resolve()
                )
            )
            self.assertIn("Patch Review Report", report_path.read_text())

    def test_relation_only_patch_can_render_report_without_candidate_notes(self) -> None:
        valid_patch = _valid_patch()
        relation = valid_patch.operations[2].relation
        patch = KnowledgePatch(
            patch_id="patch_relation_only_report",
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

        report = render_patch_review_report(patch)

        self.assertEqual(report.diff_line_count, 1)
        self.assertEqual(report.candidate_file_count, 0)
        self.assertIn("## Candidate Notes\n- none", report.content)
        self.assertIn("remove relation", report.content)

    def test_unsafe_patch_id_cannot_be_used_for_report_path(self) -> None:
        patch = KnowledgePatch(
            patch_id="../escape",
            created_at=CREATED_AT,
            source_input_ids=("raw_essay_20260511_report_ab12cd",),
            operations=_valid_patch().operations,
            risks=("review required",),
            requires_user_review=True,
        )

        with self.assertRaises(ReviewReportError):
            render_patch_review_report(patch)


def _valid_patch(patch_id: str | None = None) -> KnowledgePatch:
    proposal = _valid_proposal()
    return generate_patch_from_extraction(
        proposal,
        created_at=CREATED_AT,
        patch_id=patch_id,
    )


def _valid_proposal():
    result = validate_extraction_output(_valid_output(), _metadata())
    if result.proposal is None:
        raise AssertionError(result.errors)
    return result.proposal


def _metadata() -> AIRunMetadata:
    return AIRunMetadata(
        run_id="run_20260511_extract_report_ab12cd",
        task="extract_units",
        provider="test-provider",
        model="test-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        input_hash="sha256:inputhash",
    )


def _valid_output() -> dict:
    concept_id = "unit_20260511_report_concept_ab12cd"
    claim_id = "unit_20260511_report_claim_cd34ef"
    return {
        "source_input_id": "raw_essay_20260511_report_ab12cd",
        "unit_candidates": [
            _unit_data(
                id=concept_id,
                type="concept",
                title="Review Report",
                content="A review report summarizes the patch before acceptance.",
            ),
            _unit_data(
                id=claim_id,
                type="claim",
                title="Reports protect formal writes",
                content="Review reports expose risks and rollback steps before formal writes.",
            ),
        ],
        "relation_candidates": [
            {
                "source_id": claim_id,
                "relation_type": "supports",
                "target_id": concept_id,
                "confidence": "medium",
                "reason": "The claim supports the review report concept.",
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
        "source_id": "raw_essay_20260511_report_ab12cd",
        "source_path": "00-inbox/report.md",
        "source_span": "lines 1-3",
        "origin": "user_text",
        "line_start": 1,
        "line_end": 3,
        "content_hash": "sha256:source",
    }


if __name__ == "__main__":
    unittest.main()
