import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.ai import AIRunMetadata, validate_extraction_output
from diamonddust.application import generate_patch_from_extraction
from diamonddust.domain import KnowledgePatch
from diamonddust.storage import (
    FormalVaultConflictType,
    check_formal_vault_conflicts,
)


CREATED_AT = "2026-05-12T00:00:00Z"


class FormalVaultConflictCheckTests(unittest.TestCase):
    def test_empty_vault_is_formal_write_safe_and_read_only(self) -> None:
        patch = _valid_patch()

        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp) / "knowledge-vault"

            report = check_formal_vault_conflicts(patch, vault_root=vault_root)

            self.assertTrue(report.formal_write_safe)
            self.assertEqual(report.conflicts, ())
            self.assertFalse(vault_root.exists())
            self.assertEqual(
                report.checked_target_paths,
                (
                    "40-concepts/unit_20260512_conflict_check_ab12cd.md",
                    "50-synthesis/claims/unit_20260512_conflict_claim_cd34ef.md",
                ),
            )
            self.assertEqual(
                report.checked_unit_ids,
                (
                    "unit_20260512_conflict_check_ab12cd",
                    "unit_20260512_conflict_claim_cd34ef",
                ),
            )

    def test_existing_target_path_is_reported_as_conflict(self) -> None:
        patch = _valid_patch()
        target_path = patch.operations[0].target_path
        assert target_path is not None

        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp) / "knowledge-vault"
            _write_note(vault_root / target_path, unit_id="unit_existing_other")

            report = check_formal_vault_conflicts(patch, vault_root=vault_root)

            self.assertFalse(report.formal_write_safe)
            self.assertIn(
                FormalVaultConflictType.TARGET_PATH_EXISTS,
                _conflict_types(report),
            )
            self.assertEqual(report.conflicts[0].existing_path, target_path)

    def test_existing_unit_id_is_reported_as_conflict(self) -> None:
        patch = _valid_patch()
        unit = patch.operations[0].unit
        assert unit is not None

        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp) / "knowledge-vault"
            _write_note(vault_root / "40-concepts/existing-note.md", unit_id=unit.id)

            report = check_formal_vault_conflicts(patch, vault_root=vault_root)

            self.assertFalse(report.formal_write_safe)
            self.assertIn(
                FormalVaultConflictType.UNIT_ID_EXISTS,
                _conflict_types(report),
            )
            self.assertEqual(
                report.existing_unit_paths[unit.id],
                "40-concepts/existing-note.md",
            )

    def test_duplicate_patch_targets_are_reported_without_vault_files(self) -> None:
        patch = _valid_patch()
        duplicate_patch = KnowledgePatch(
            patch_id="patch_duplicate_targets",
            created_at=patch.created_at,
            source_input_ids=patch.source_input_ids,
            operations=(patch.operations[0], patch.operations[0]),
            risks=patch.risks,
            requires_user_review=True,
        )

        with TemporaryDirectory() as tmp:
            report = check_formal_vault_conflicts(
                duplicate_patch,
                vault_root=Path(tmp) / "knowledge-vault",
            )

            self.assertFalse(report.formal_write_safe)
            self.assertIn(
                FormalVaultConflictType.DUPLICATE_PATCH_TARGET_PATH,
                _conflict_types(report),
            )
            self.assertIn(
                FormalVaultConflictType.DUPLICATE_PATCH_UNIT_ID,
                _conflict_types(report),
            )

    def test_ai_working_directories_are_ignored_for_formal_conflicts(self) -> None:
        patch = _valid_patch()
        unit = patch.operations[0].unit
        assert unit is not None

        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp) / "knowledge-vault"
            _write_note(
                vault_root / "_ai_suggestions/candidate-notes/patch/example.md",
                unit_id=unit.id,
            )

            report = check_formal_vault_conflicts(patch, vault_root=vault_root)

            self.assertTrue(report.formal_write_safe)
            self.assertEqual(report.conflicts, ())
            self.assertEqual(dict(report.existing_unit_paths), {})

    def test_conflict_check_does_not_modify_existing_formal_files(self) -> None:
        patch = _valid_patch()
        unit = patch.operations[0].unit
        assert unit is not None

        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp) / "knowledge-vault"
            existing_path = vault_root / "40-concepts/existing-note.md"
            _write_note(existing_path, unit_id=unit.id)
            before = existing_path.read_text(encoding="utf-8")

            check_formal_vault_conflicts(patch, vault_root=vault_root)

            self.assertEqual(existing_path.read_text(encoding="utf-8"), before)


def _conflict_types(report) -> tuple[FormalVaultConflictType, ...]:
    return tuple(conflict.conflict_type for conflict in report.conflicts)


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


def _valid_patch() -> KnowledgePatch:
    result = validate_extraction_output(_valid_output(), _metadata())
    if not result.proposal:
        raise AssertionError(result.errors)
    return generate_patch_from_extraction(result.proposal, created_at=CREATED_AT)


def _metadata() -> AIRunMetadata:
    return AIRunMetadata(
        run_id="run_20260512_vault_conflict_checks_ab12cd",
        task="extract_units",
        provider="test-provider",
        model="test-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        input_hash="sha256:inputhash",
    )


def _valid_output() -> dict:
    return {
        "source_input_id": "raw_essay_20260512_conflict_checks_ab12cd",
        "unit_candidates": [
            _unit_data(
                id="unit_20260512_conflict_check_ab12cd",
                type="concept",
                title="Vault conflict checks",
                content="Formal vault writes need path and ID conflict checks.",
            ),
            _unit_data(
                id="unit_20260512_conflict_claim_cd34ef",
                type="claim",
                title="Conflict checks precede apply",
                content="A patch should be checked before formal apply behavior exists.",
            ),
        ],
        "relation_candidates": [],
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
        "source_id": "raw_essay_20260512_conflict_checks_ab12cd",
        "source_path": "00-inbox/conflict-checks.md",
        "source_span": "lines 1-3",
        "origin": "user_text",
        "line_start": 1,
        "line_end": 3,
        "content_hash": "sha256:source",
    }


if __name__ == "__main__":
    unittest.main()
