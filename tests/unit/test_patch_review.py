import unittest

from diamonddust.ai import AIRunMetadata, validate_extraction_output
from diamonddust.application import (
    PatchReviewDecision,
    PatchReviewError,
    generate_patch_from_extraction,
    inspect_patch_diff,
    review_patch,
    target_path_for_unit,
)
from diamonddust.domain import KnowledgePatch, PatchOperation, PatchOperationType


class PatchReviewWorkflowTests(unittest.TestCase):
    def test_generates_knowledge_patch_from_extraction_proposal(self) -> None:
        proposal = _valid_proposal()

        patch = generate_patch_from_extraction(
            proposal,
            created_at="2026-05-10T00:00:00Z",
        )

        self.assertTrue(patch.patch_id.startswith("patch_raw_essay_20260510_gate5_"))
        self.assertEqual(patch.source_input_ids, ("raw_essay_20260510_gate5_ab12cd",))
        self.assertEqual(len(patch.operations), 3)
        self.assertTrue(patch.requires_user_review)
        self.assertEqual(
            patch.operations[0].target_path,
            "40-concepts/unit_20260510_patch_review_ab12cd.md",
        )
        self.assertEqual(
            patch.operations[1].target_path,
            "50-synthesis/claims/unit_20260510_review_gate_cd34ef.md",
        )
        self.assertEqual(
            patch.operations[2].operation_type,
            PatchOperationType.ADD_RELATION,
        )

    def test_patch_diff_is_inspectable_and_has_rollback_steps(self) -> None:
        patch = _valid_patch()

        diff = inspect_patch_diff(patch)

        self.assertEqual(diff.patch_id, patch.patch_id)
        self.assertEqual(len(diff.lines), 3)
        self.assertTrue(diff.has_rollback_plan)
        self.assertIn("create note", diff.lines[0].summary)
        self.assertIn("add relation", diff.lines[2].summary)
        self.assertIn("delete created note", diff.rollback_steps[0])
        self.assertIn("remove relation", diff.rollback_steps[2])

    def test_rejecting_patch_never_allows_formal_write(self) -> None:
        patch = _valid_patch()

        result = review_patch(patch, PatchReviewDecision.REJECTED)

        self.assertEqual(result.decision, PatchReviewDecision.REJECTED)
        self.assertFalse(result.formal_write_allowed)
        self.assertEqual(result.patch, patch)
        self.assertTrue(result.diff.has_rollback_plan)

    def test_accepting_patch_allows_formal_write_handoff(self) -> None:
        patch = _valid_patch()

        result = review_patch(patch, PatchReviewDecision.ACCEPTED)

        self.assertEqual(result.decision, PatchReviewDecision.ACCEPTED)
        self.assertTrue(result.formal_write_allowed)
        self.assertEqual(result.patch, patch)

    def test_review_requires_explicit_decision_enum(self) -> None:
        with self.assertRaises(PatchReviewError):
            review_patch(_valid_patch(), "accepted")  # type: ignore[arg-type]

    def test_unsafe_unit_id_cannot_generate_target_path(self) -> None:
        proposal = _proposal_from_output(_valid_output(unit_id="../escape"))

        with self.assertRaises(PatchReviewError):
            generate_patch_from_extraction(
                proposal,
                created_at="2026-05-10T00:00:00Z",
            )

    def test_patch_review_rejects_ai_working_directory_target(self) -> None:
        proposal = _valid_proposal()
        unit = proposal.unit_candidates[0]
        patch = KnowledgePatch(
            patch_id="patch_bad_target",
            created_at="2026-05-10T00:00:00Z",
            source_input_ids=(proposal.source_input_id,),
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
            inspect_patch_diff(patch)

    def test_unsupported_operation_cannot_enter_gate_5_review(self) -> None:
        patch = KnowledgePatch(
            patch_id="patch_blog_draft_not_gate5",
            created_at="2026-05-10T00:00:00Z",
            source_input_ids=("raw_essay_20260510_gate5_ab12cd",),
            operations=(
                PatchOperation(
                    operation_type=PatchOperationType.CREATE_BLOG_DRAFT,
                    draft_id="draft_1",
                ),
            ),
            risks=("review required",),
            requires_user_review=True,
        )

        with self.assertRaises(PatchReviewError):
            inspect_patch_diff(patch)

    def test_empty_extraction_proposal_cannot_generate_patch(self) -> None:
        proposal = _proposal_from_output(
            {
                "source_input_id": "raw_essay_20260510_gate5_ab12cd",
                "unit_candidates": [],
                "relation_candidates": [],
            }
        )

        with self.assertRaises(PatchReviewError):
            generate_patch_from_extraction(
                proposal,
                created_at="2026-05-10T00:00:00Z",
            )

    def test_patch_generation_requires_created_at(self) -> None:
        with self.assertRaises(PatchReviewError):
            generate_patch_from_extraction(
                _valid_proposal(),
                created_at="",
            )

    def test_target_path_uses_unit_type_path_rule(self) -> None:
        proposal = _valid_proposal()

        self.assertEqual(
            target_path_for_unit(proposal.unit_candidates[0]),
            "40-concepts/unit_20260510_patch_review_ab12cd.md",
        )
        self.assertEqual(
            target_path_for_unit(proposal.unit_candidates[1]),
            "50-synthesis/claims/unit_20260510_review_gate_cd34ef.md",
        )


def _valid_patch() -> KnowledgePatch:
    return generate_patch_from_extraction(
        _valid_proposal(),
        created_at="2026-05-10T00:00:00Z",
    )


def _valid_proposal():
    return _proposal_from_output(_valid_output())


def _proposal_from_output(output: dict):
    result = validate_extraction_output(output, _metadata())
    if not result.proposal:
        raise AssertionError(result.errors)
    return result.proposal


def _metadata() -> AIRunMetadata:
    return AIRunMetadata(
        run_id="run_20260510_extract_gate5_ab12cd",
        task="extract_units",
        provider="test-provider",
        model="test-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        input_hash="sha256:inputhash",
    )


def _valid_output(unit_id: str = "unit_20260510_patch_review_ab12cd") -> dict:
    return {
        "source_input_id": "raw_essay_20260510_gate5_ab12cd",
        "unit_candidates": [
            _unit_data(
                id=unit_id,
                type="concept",
                title="Patch review",
                content="A patch must be reviewed before formal write.",
            ),
            _unit_data(
                id="unit_20260510_review_gate_cd34ef",
                type="claim",
                title="Review gates protect formal writes",
                content="Formal vault changes require accepted patches.",
            ),
        ],
        "relation_candidates": [
            {
                "source_id": "unit_20260510_review_gate_cd34ef",
                "relation_type": "depends_on",
                "target_id": unit_id,
                "confidence": "medium",
                "reason": "The claim depends on the patch review concept.",
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
        "source_id": "raw_essay_20260510_gate5_ab12cd",
        "source_path": "00-inbox/gate5.md",
        "source_span": "lines 1-3",
        "origin": "user_text",
        "line_start": 1,
        "line_end": 3,
        "content_hash": "sha256:source",
    }


if __name__ == "__main__":
    unittest.main()
