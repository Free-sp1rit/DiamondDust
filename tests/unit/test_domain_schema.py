import unittest

from diamonddust.domain import (
    Confidence,
    KnowledgePatch,
    KnowledgeUnit,
    PatchOperation,
    PatchOperationType,
    Relation,
    RelationType,
    SourceOrigin,
    SourceRef,
    Status,
    UnitType,
    ValidationError,
)


class DomainSchemaTest(unittest.TestCase):
    def test_source_ref_from_mapping_validates_required_fields(self) -> None:
        source_ref = SourceRef.from_mapping(_source_ref_data())

        self.assertEqual(source_ref.source_id, "raw_essay_1")
        self.assertEqual(source_ref.origin, SourceOrigin.USER_TEXT)

    def test_source_ref_rejects_missing_required_field(self) -> None:
        data = _source_ref_data()
        del data["source_span"]

        with self.assertRaises(ValidationError):
            SourceRef.from_mapping(data)

    def test_relation_from_mapping_uses_closed_relation_types(self) -> None:
        relation = Relation.from_mapping(_relation_data())

        self.assertEqual(relation.relation_type, RelationType.SUPPORTS)
        self.assertEqual(relation.confidence, Confidence.HIGH)

    def test_relation_rejects_unknown_type(self) -> None:
        data = _relation_data()
        data["relation_type"] = "causes"

        with self.assertRaises(ValidationError):
            Relation.from_mapping(data)

    def test_knowledge_unit_from_mapping_creates_typed_nested_objects(self) -> None:
        unit = KnowledgeUnit.from_mapping(_unit_data(type="concept"))

        self.assertEqual(unit.type, UnitType.CONCEPT)
        self.assertEqual(unit.status, Status.SEEDLING)
        self.assertIsInstance(unit.source_refs[0], SourceRef)
        self.assertIsInstance(unit.relations[0], Relation)

    def test_knowledge_unit_rejects_missing_required_field(self) -> None:
        data = _unit_data(type="concept")
        del data["schema_version"]

        with self.assertRaises(ValidationError):
            KnowledgeUnit.from_mapping(data)

    def test_claim_requires_source_refs_or_unsupported_flag(self) -> None:
        data = _unit_data(type="claim", source_refs=[])

        with self.assertRaises(ValidationError):
            KnowledgeUnit.from_mapping(data)

        unsupported_claim = KnowledgeUnit.from_mapping(
            _unit_data(type="claim", source_refs=[], unsupported=True)
        )
        self.assertTrue(unsupported_claim.unsupported)

    def test_patch_requires_user_review(self) -> None:
        data = _patch_data()
        data["requires_user_review"] = False

        with self.assertRaises(ValidationError):
            KnowledgePatch.from_mapping(data)

    def test_patch_requires_operations(self) -> None:
        data = _patch_data()
        data["operations"] = []

        with self.assertRaises(ValidationError):
            KnowledgePatch.from_mapping(data)

    def test_create_note_operation_requires_typed_unit_and_path(self) -> None:
        operation = PatchOperation.from_mapping(_create_note_operation_data())

        self.assertEqual(operation.operation_type, PatchOperationType.CREATE_NOTE)
        self.assertIsInstance(operation.unit, KnowledgeUnit)
        self.assertEqual(operation.target_path, "40-concepts/example.md")

    def test_add_relation_operation_requires_relation(self) -> None:
        with self.assertRaises(ValidationError):
            PatchOperation.from_mapping({"operation_type": "add_relation"})

    def test_patch_from_mapping_creates_typed_operations(self) -> None:
        patch = KnowledgePatch.from_mapping(_patch_data())

        self.assertEqual(patch.patch_id, "patch_20260510_schema_ab12cd")
        self.assertIsInstance(patch.operations[0], PatchOperation)


def _source_ref_data() -> dict:
    return {
        "source_id": "raw_essay_1",
        "source_path": "00-inbox/example.md",
        "source_span": "paragraph 1",
        "origin": "user_text",
        "is_approximate": True,
    }


def _relation_data() -> dict:
    return {
        "source_id": "unit_1",
        "relation_type": "supports",
        "target_id": "unit_2",
        "confidence": "high",
        "reason": "The evidence supports the claim.",
    }


def _unit_data(
    *,
    type: str,
    source_refs: list[dict] | None = None,
    unsupported: bool = False,
) -> dict:
    return {
        "id": "unit_20260510_example_ab12cd",
        "type": type,
        "title": "Example unit",
        "content": "A concise example unit.",
        "status": "seedling",
        "source_refs": [_source_ref_data()] if source_refs is None else source_refs,
        "relations": [_relation_data()],
        "confidence": "medium",
        "created_at": "2026-05-10T00:00:00Z",
        "updated_at": "2026-05-10T00:00:00Z",
        "schema_version": "0.1.0",
        "unsupported": unsupported,
    }


def _create_note_operation_data() -> dict:
    return {
        "operation_type": "create_note",
        "target_path": "40-concepts/example.md",
        "unit": _unit_data(type="concept"),
    }


def _patch_data() -> dict:
    return {
        "patch_id": "patch_20260510_schema_ab12cd",
        "created_at": "2026-05-10T00:00:00Z",
        "source_input_ids": ["raw_essay_1"],
        "operations": [_create_note_operation_data()],
        "risks": ["review required before formal write"],
        "requires_user_review": True,
    }


if __name__ == "__main__":
    unittest.main()
