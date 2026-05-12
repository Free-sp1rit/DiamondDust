import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.ai import AIRunMetadata, validate_extraction_output
from diamonddust.application import generate_patch_from_extraction
from diamonddust.domain import KnowledgePatch, PatchOperation, PatchOperationType
from diamonddust.storage import (
    FormalVaultApplyPlanError,
    check_formal_vault_conflicts,
    plan_formal_vault_apply,
)


CREATED_AT = "2026-05-12T00:00:00Z"


class FormalVaultApplyPlanTests(unittest.TestCase):
    def test_clean_patch_produces_dry_run_apply_plan(self) -> None:
        patch = _valid_patch()

        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp) / "knowledge-vault"

            plan = plan_formal_vault_apply(patch, vault_root=vault_root)

            self.assertEqual(plan.patch_id, patch.patch_id)
            self.assertEqual(plan.file_count, 2)
            self.assertFalse(plan.formal_write_performed)
            self.assertTrue(plan.requires_user_review)
            self.assertTrue(plan.conflict_report.formal_write_safe)
            self.assertEqual(
                tuple(file.target_path for file in plan.files),
                (
                    "40-concepts/unit_20260512_apply_plan_ab12cd.md",
                    "50-synthesis/claims/unit_20260512_apply_claim_cd34ef.md",
                ),
            )
            self.assertTrue(all(file.content_hash.startswith("sha256:") for file in plan.files))
            self.assertTrue(all(file.rollback_step for file in plan.files))
            self.assertFalse(vault_root.exists())

    def test_planned_formal_note_content_removes_candidate_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            plan = plan_formal_vault_apply(
                _valid_patch(),
                vault_root=Path(tmp) / "knowledge-vault",
            )

        content = plan.files[0].content

        self.assertIn('id: "unit_20260512_apply_plan_ab12cd"', content)
        self.assertIn("relations:", content)
        self.assertNotIn("artifact_type:", content)
        self.assertNotIn("artifact_schema_version:", content)
        self.assertNotIn("candidate:", content)
        self.assertNotIn("formal_write: false", content)
        self.assertNotIn("requires_user_review: true", content)

    def test_conflicted_patch_cannot_produce_apply_plan(self) -> None:
        patch = _valid_patch()
        target_path = patch.operations[0].target_path
        assert target_path is not None

        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp) / "knowledge-vault"
            _write_note(vault_root / target_path, unit_id="unit_existing_other")

            with self.assertRaises(FormalVaultApplyPlanError):
                plan_formal_vault_apply(patch, vault_root=vault_root)

    def test_conflict_report_must_match_patch(self) -> None:
        patch = _valid_patch()
        other_patch = _valid_patch(patch_id="patch_other_apply_plan")

        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp) / "knowledge-vault"
            report = check_formal_vault_conflicts(patch, vault_root=vault_root)

            with self.assertRaises(FormalVaultApplyPlanError):
                plan_formal_vault_apply(
                    other_patch,
                    vault_root=vault_root,
                    conflict_report=report,
                )

    def test_relation_updates_for_existing_notes_are_not_planned_yet(self) -> None:
        patch = _valid_patch()
        relation = patch.operations[-1].relation
        assert relation is not None
        relation_only_patch = KnowledgePatch(
            patch_id="patch_relation_existing_note",
            created_at=patch.created_at,
            source_input_ids=patch.source_input_ids,
            operations=(
                PatchOperation(
                    operation_type=PatchOperationType.CREATE_NOTE,
                    target_path=patch.operations[0].target_path,
                    unit=patch.operations[0].unit,
                ),
                PatchOperation(
                    operation_type=PatchOperationType.ADD_RELATION,
                    relation=type(relation)(
                        source_id="unit_existing_formal_note",
                        relation_type=relation.relation_type,
                        target_id=relation.target_id,
                        confidence=relation.confidence,
                        reason=relation.reason,
                    ),
                ),
            ),
            risks=patch.risks,
            requires_user_review=True,
        )

        with TemporaryDirectory() as tmp:
            with self.assertRaises(FormalVaultApplyPlanError):
                plan_formal_vault_apply(
                    relation_only_patch,
                    vault_root=Path(tmp) / "knowledge-vault",
                )

    def test_apply_plan_does_not_modify_existing_formal_files(self) -> None:
        patch = _valid_patch()

        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp) / "knowledge-vault"
            existing_path = vault_root / "40-concepts/existing-note.md"
            _write_note(existing_path, unit_id="unit_existing_safe")
            before = existing_path.read_text(encoding="utf-8")

            plan_formal_vault_apply(patch, vault_root=vault_root)

            self.assertEqual(existing_path.read_text(encoding="utf-8"), before)


def _write_note(path: Path, *, unit_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "---",
                f"id: {unit_id}",
                "type: concept",
                "status: seedling",
                "---",
                "",
                "# Existing note",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _valid_patch(patch_id: str | None = None) -> KnowledgePatch:
    result = validate_extraction_output(_valid_output(), _metadata())
    if not result.proposal:
        raise AssertionError(result.errors)
    return generate_patch_from_extraction(
        result.proposal,
        created_at=CREATED_AT,
        patch_id=patch_id,
    )


def _metadata() -> AIRunMetadata:
    return AIRunMetadata(
        run_id="run_20260512_formal_apply_plan_ab12cd",
        task="extract_units",
        provider="test-provider",
        model="test-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        input_hash="sha256:inputhash",
    )


def _valid_output() -> dict:
    return {
        "source_input_id": "raw_essay_20260512_formal_apply_plan_ab12cd",
        "unit_candidates": [
            _unit_data(
                id="unit_20260512_apply_plan_ab12cd",
                type="concept",
                title="Formal apply plans",
                content="A dry-run apply plan should precede formal vault writes.",
            ),
            _unit_data(
                id="unit_20260512_apply_claim_cd34ef",
                type="claim",
                title="Dry-run plans keep formal writes explicit",
                content="A formal apply plan should list target files before writing them.",
            ),
        ],
        "relation_candidates": [
            {
                "source_id": "unit_20260512_apply_claim_cd34ef",
                "relation_type": "supports",
                "target_id": "unit_20260512_apply_plan_ab12cd",
                "confidence": "medium",
                "reason": "The claim supports the apply-plan concept.",
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
        "source_id": "raw_essay_20260512_formal_apply_plan_ab12cd",
        "source_path": "00-inbox/formal-apply-plan.md",
        "source_span": "lines 1-3",
        "origin": "user_text",
        "line_start": 1,
        "line_end": 3,
        "content_hash": "sha256:source",
    }


if __name__ == "__main__":
    unittest.main()
