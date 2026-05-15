import unittest

from diamonddust.ai import AIRunMetadata, validate_extraction_output
from diamonddust.application import (
    BlogDraftError,
    BlogMode,
    BlogQualityStatus,
    PatchReviewDecision,
    generate_blog_draft_from_review,
    generate_patch_from_extraction,
    review_patch,
)
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
)


class BlogDraftWorkflowTests(unittest.TestCase):
    def test_generates_blog_draft_from_accepted_review_result(self) -> None:
        package = generate_blog_draft_from_review(
            _accepted_review(),
            title="Patch Review for Writers",
            mode=BlogMode.EXPLANATION,
            audience="knowledge workers",
            reader_problem="understanding why reviewable patches matter",
        )

        self.assertEqual(package.draft.title, "Patch Review for Writers")
        self.assertEqual(package.draft.mode, BlogMode.EXPLANATION)
        self.assertEqual(package.draft.quality_report_id, package.quality_report.id)
        self.assertEqual(package.quality_report.target_id, package.draft.id)
        self.assertEqual(package.quality_report.validation_status, BlogQualityStatus.PASSED)
        self.assertEqual(len(package.draft.claim_inventory), 2)
        self.assertEqual(package.draft.claim_inventory[0].role, "supporting_concept")
        self.assertEqual(package.draft.claim_inventory[1].role, "claim")
        self.assertEqual(package.draft.unsupported_claims, ())
        self.assertIn("## Claim Inventory", package.draft.content)
        self.assertIn("supporting concept; supported", package.draft.content)
        self.assertIn("## Source Units", package.draft.content)
        self.assertEqual(
            set(package.draft.source_unit_ids),
            {
                "unit_20260510_blog_context_ab12cd",
                "unit_20260510_blog_claim_cd34ef",
            },
        )

    def test_rejected_review_result_cannot_generate_blog_draft(self) -> None:
        patch = _valid_patch()
        rejected = review_patch(patch, PatchReviewDecision.REJECTED)

        with self.assertRaises(BlogDraftError):
            generate_blog_draft_from_review(
                rejected,
                title="Rejected Patch Draft",
                mode=BlogMode.ESSAY,
                audience="reviewers",
                reader_problem="using rejected patches",
            )

    def test_claim_inventory_preserves_source_refs(self) -> None:
        package = generate_blog_draft_from_review(
            _accepted_review(),
            title="Claim Inventory",
            mode=BlogMode.REFERENCE,
            audience="maintainers",
            reader_problem="checking claims before publication",
        )

        claim = next(
            item for item in package.draft.claim_inventory if item.role == "claim"
        )

        self.assertEqual(claim.claim_id, "unit_20260510_blog_claim_cd34ef")
        self.assertFalse(claim.unsupported)
        self.assertEqual(claim.source_refs[0].source_id, "raw_essay_20260510_blog_ab12cd")
        self.assertEqual(claim.source_unit_id, claim.claim_id)

    def test_unsupported_claims_are_reported_in_draft_and_quality_report(self) -> None:
        package = generate_blog_draft_from_review(
            _accepted_review_with_unsupported_claim(),
            title="Unsupported Claims",
            mode=BlogMode.ESSAY,
            audience="editors",
            reader_problem="spotting unsupported claims",
        )

        self.assertEqual(len(package.draft.unsupported_claims), 1)
        self.assertIn("UNSUPPORTED", package.draft.content)
        self.assertEqual(
            package.quality_report.unsupported_claims,
            ("unit_20260510_unsupported_claim_ab12cd",),
        )
        self.assertEqual(package.quality_report.validation_status, BlogQualityStatus.WARNING)
        self.assertIn("unsupported claims", package.quality_report.risks[0])

    def test_quality_report_contains_evidence_coverage_for_each_source_unit(self) -> None:
        package = generate_blog_draft_from_review(
            _accepted_review(),
            title="Evidence Coverage",
            mode=BlogMode.CASE_STUDY,
            audience="reviewers",
            reader_problem="checking coverage",
        )

        coverage_ids = {item.unit_id for item in package.quality_report.evidence_coverage}

        self.assertEqual(coverage_ids, set(package.draft.source_unit_ids))
        self.assertTrue(all(item.has_source_refs for item in package.quality_report.evidence_coverage))
        self.assertTrue(all(item.source_ref_count == 1 for item in package.quality_report.evidence_coverage))

    def test_claim_inventory_cannot_reference_sources_outside_draft(self) -> None:
        package = generate_blog_draft_from_review(
            _accepted_review(),
            title="No Invented Sources",
            mode=BlogMode.EXPLANATION,
            audience="maintainers",
            reader_problem="checking source boundaries",
        )

        source_ids = set(package.draft.source_unit_ids)

        self.assertTrue(
            all(item.source_unit_id in source_ids for item in package.draft.claim_inventory)
        )

    def test_mode_must_be_explicit_blog_mode(self) -> None:
        with self.assertRaises(BlogDraftError):
            generate_blog_draft_from_review(
                _accepted_review(),
                title="Bad Mode",
                mode="essay",  # type: ignore[arg-type]
                audience="writers",
                reader_problem="mode validation",
            )

    def test_patch_without_create_note_units_cannot_generate_blog_draft(self) -> None:
        patch = KnowledgePatch(
            patch_id="patch_no_units",
            created_at="2026-05-10T00:00:00Z",
            source_input_ids=("raw_essay_20260510_blog_ab12cd",),
            operations=(
                PatchOperation(
                    operation_type=PatchOperationType.ADD_RELATION,
                    relation=_relation(),
                ),
            ),
            risks=("review required",),
            requires_user_review=True,
        )
        accepted = review_patch(patch, PatchReviewDecision.ACCEPTED)

        with self.assertRaises(BlogDraftError):
            generate_blog_draft_from_review(
                accepted,
                title="No Units",
                mode=BlogMode.ESSAY,
                audience="writers",
                reader_problem="missing source units",
            )


def _accepted_review():
    return review_patch(_valid_patch(), PatchReviewDecision.ACCEPTED)


def _valid_patch() -> KnowledgePatch:
    return generate_patch_from_extraction(
        _valid_proposal(),
        created_at="2026-05-10T00:00:00Z",
    )


def _valid_proposal():
    result = validate_extraction_output(_valid_output(), _metadata())
    if not result.proposal:
        raise AssertionError(result.errors)
    return result.proposal


def _accepted_review_with_unsupported_claim():
    patch = KnowledgePatch(
        patch_id="patch_unsupported_blog_claim",
        created_at="2026-05-10T00:00:00Z",
        source_input_ids=("raw_essay_20260510_blog_ab12cd",),
        operations=(
            PatchOperation(
                operation_type=PatchOperationType.CREATE_NOTE,
                target_path="40-concepts/unit_20260510_blog_context_ab12cd.md",
                unit=_concept_unit(),
            ),
            PatchOperation(
                operation_type=PatchOperationType.CREATE_NOTE,
                target_path="50-synthesis/claims/unit_20260510_unsupported_claim_ab12cd.md",
                unit=_unsupported_claim_unit(),
            ),
        ),
        risks=("review required",),
        requires_user_review=True,
    )
    return review_patch(patch, PatchReviewDecision.ACCEPTED)


def _metadata() -> AIRunMetadata:
    return AIRunMetadata(
        run_id="run_20260510_extract_blog_ab12cd",
        task="extract_units",
        provider="test-provider",
        model="test-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        input_hash="sha256:inputhash",
    )


def _valid_output() -> dict:
    return {
        "source_input_id": "raw_essay_20260510_blog_ab12cd",
        "unit_candidates": [
            {
                "id": "unit_20260510_blog_context_ab12cd",
                "type": "concept",
                "title": "Blog drafts need evidence",
                "content": "A blog draft should preserve links to source units.",
                "status": "seedling",
                "source_refs": [_source_ref_data()],
                "relations": [],
                "confidence": "medium",
                "created_at": "2026-05-10T00:00:00Z",
                "updated_at": "2026-05-10T00:00:00Z",
                "schema_version": "0.1.0",
            },
            {
                "id": "unit_20260510_blog_claim_cd34ef",
                "type": "claim",
                "title": "Claim inventories protect draft quality",
                "content": "A claim inventory makes unsupported claims visible.",
                "status": "seedling",
                "source_refs": [_source_ref_data()],
                "relations": [],
                "confidence": "medium",
                "created_at": "2026-05-10T00:00:00Z",
                "updated_at": "2026-05-10T00:00:00Z",
                "schema_version": "0.1.0",
            },
        ],
        "relation_candidates": [_relation_data()],
    }


def _concept_unit() -> KnowledgeUnit:
    return KnowledgeUnit(
        id="unit_20260510_blog_context_ab12cd",
        type=UnitType.CONCEPT,
        title="Blog drafts need evidence",
        content="A blog draft should preserve links to source units.",
        status=Status.SEEDLING,
        source_refs=(_source_ref(),),
        relations=(),
        confidence=Confidence.MEDIUM,
        created_at="2026-05-10T00:00:00Z",
        updated_at="2026-05-10T00:00:00Z",
        schema_version="0.1.0",
    )


def _unsupported_claim_unit() -> KnowledgeUnit:
    return KnowledgeUnit(
        id="unit_20260510_unsupported_claim_ab12cd",
        type=UnitType.CLAIM,
        title="This claim still needs support",
        content="This claim is intentionally marked unsupported.",
        status=Status.SEEDLING,
        source_refs=(),
        relations=(),
        confidence=Confidence.LOW,
        created_at="2026-05-10T00:00:00Z",
        updated_at="2026-05-10T00:00:00Z",
        schema_version="0.1.0",
        unsupported=True,
    )


def _relation():
    return Relation(
        source_id="unit_20260510_blog_claim_cd34ef",
        relation_type=RelationType.DEPENDS_ON,
        target_id="unit_20260510_blog_context_ab12cd",
        confidence=Confidence.MEDIUM,
        reason="The claim depends on evidence-aware drafting.",
    )


def _relation_data() -> dict:
    return {
        "source_id": "unit_20260510_blog_claim_cd34ef",
        "relation_type": "depends_on",
        "target_id": "unit_20260510_blog_context_ab12cd",
        "confidence": "medium",
        "reason": "The claim depends on evidence-aware drafting.",
    }


def _source_ref() -> SourceRef:
    return SourceRef(
        source_id="raw_essay_20260510_blog_ab12cd",
        source_path="00-inbox/blog.md",
        source_span="lines 1-3",
        origin=SourceOrigin.USER_TEXT,
        line_start=1,
        line_end=3,
        content_hash="sha256:source",
    )


def _source_ref_data() -> dict:
    return {
        "source_id": "raw_essay_20260510_blog_ab12cd",
        "source_path": "00-inbox/blog.md",
        "source_span": "lines 1-3",
        "origin": "user_text",
        "line_start": 1,
        "line_end": 3,
        "content_hash": "sha256:source",
    }


if __name__ == "__main__":
    unittest.main()
