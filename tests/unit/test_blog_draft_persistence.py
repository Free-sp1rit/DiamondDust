import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.application import (
    BlogDraft,
    BlogDraftPackage,
    BlogMode,
    BlogQualityReport,
    BlogQualityStatus,
    ClaimInventoryItem,
    EvidenceCoverageItem,
)
from diamonddust.domain import SourceOrigin, SourceRef
from diamonddust.storage import (
    AI_BLOG_DRAFTS_DIR,
    AI_BLOG_QUALITY_REPORTS_DIR,
    BlogDraftArtifactContext,
    BlogDraftPersistenceError,
    BlogQualityReportContext,
    render_blog_draft_markdown,
    render_blog_quality_report,
    write_blog_draft_package,
)


class BlogDraftPersistenceTests(unittest.TestCase):
    def test_renders_blog_draft_markdown_with_review_boundaries(self) -> None:
        package = _blog_package()

        artifact = render_blog_draft_markdown(package)

        self.assertEqual(artifact.draft_id, package.draft.id)
        self.assertEqual(
            artifact.relative_path,
            f"{AI_BLOG_DRAFTS_DIR}/{package.draft.id}/draft.md",
        )
        self.assertFalse(artifact.formal_write_allowed)
        self.assertFalse(artifact.publication_ready)
        self.assertEqual(artifact.source_unit_count, 2)
        self.assertIn("artifact_type: blog_draft", artifact.content)
        self.assertIn("formal_write: false", artifact.content)
        self.assertIn("publication_ready: false", artifact.content)
        self.assertIn("requires_user_review: true", artifact.content)
        self.assertIn(package.draft.content.strip(), artifact.content)

    def test_renders_blog_draft_markdown_with_scope_context(self) -> None:
        package = _blog_package()

        artifact = render_blog_draft_markdown(
            package,
            context=BlogDraftArtifactContext(
                draft_scope="provider_free_fixture",
                real_ai_generation_validated=False,
            ),
        )

        self.assertIn('draft_scope: "provider_free_fixture"', artifact.content)
        self.assertIn("real_ai_generation_validated: false", artifact.content)
        self.assertTrue(artifact.requires_user_review)

    def test_renders_quality_report_with_unsupported_claims(self) -> None:
        package = _blog_package(unsupported=True)

        artifact = render_blog_quality_report(package)

        self.assertEqual(artifact.report_id, package.quality_report.id)
        self.assertEqual(artifact.draft_id, package.draft.id)
        self.assertEqual(artifact.quality_status, "warning")
        self.assertEqual(artifact.unsupported_claim_count, 1)
        self.assertEqual(
            artifact.relative_path,
            f"{AI_BLOG_QUALITY_REPORTS_DIR}/{package.draft.id}.md",
        )
        self.assertIn("# Blog Quality Report", artifact.content)
        self.assertIn("artifact_type: blog_quality_report", artifact.content)
        self.assertIn("quality_status: \"warning\"", artifact.content)
        self.assertIn("publication_ready: false", artifact.content)
        self.assertIn("requires_user_review: true", artifact.content)
        self.assertIn("- quality_status: warning", artifact.content)
        self.assertIn("unit_blog_claim_ab12cd", artifact.content)
        self.assertIn("role=claim", artifact.content)
        self.assertIn("unsupported=true", artifact.content)

    def test_renders_fixture_quality_report_with_trial_scope(self) -> None:
        package = _blog_package()

        artifact = render_blog_quality_report(
            package,
            context=BlogQualityReportContext(
                trial_id="trial_blog_fixture_ab12cd",
                report_scope="provider_free_fixture",
                real_ai_generation_validated=False,
                product_owner_verdict="pending",
                created_at="2026-05-11T00:00:00Z",
                fixture_driven=True,
            ),
        )

        self.assertEqual(artifact.risk_count, 4)
        self.assertTrue(artifact.requires_user_review)
        self.assertIn("artifact_type: blog_quality_report", artifact.content)
        self.assertIn('trial_id: "trial_blog_fixture_ab12cd"', artifact.content)
        self.assertIn('report_scope: "provider_free_fixture"', artifact.content)
        self.assertIn("real_ai_generation_validated: false", artifact.content)
        self.assertIn('quality_status: "passed"', artifact.content)
        self.assertIn('product_owner_verdict: "pending"', artifact.content)
        self.assertIn('created_at: "2026-05-11T00:00:00Z"', artifact.content)
        self.assertIn("- quality_status: passed", artifact.content)
        self.assertIn("- product_owner_verdict: pending", artifact.content)
        self.assertIn(
            "- quality_summary: 2 source units covered; 0 unsupported claims "
            "reported in this fixture-driven local trial",
            artifact.content,
        )
        self.assertIn(
            "not real AI generation quality",
            artifact.content,
        )
        self.assertIn(
            "- none detected in this fixture-driven local trial",
            artifact.content,
        )
        self.assertIn(
            "- Do not publish without a separate publication approval flow.",
            artifact.content,
        )

    def test_writes_blog_package_without_formal_publication_mutation(self) -> None:
        package = _blog_package()
        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp)

            export = write_blog_draft_package(package, vault_root=vault_root)

            draft_path = vault_root / export.draft_artifact.relative_path
            report_path = vault_root / export.quality_report_artifact.relative_path
            formal_publication_path = vault_root / "70-publications" / f"{package.draft.id}.md"

            self.assertTrue(draft_path.exists())
            self.assertTrue(report_path.exists())
            self.assertFalse(formal_publication_path.exists())
            self.assertFalse(export.formal_write_allowed)
            self.assertFalse(export.publication_ready)
            self.assertEqual(
                export.written_paths,
                (
                    export.draft_artifact.relative_path,
                    export.quality_report_artifact.relative_path,
                ),
            )
            self.assertTrue(
                draft_path.resolve().is_relative_to(
                    (vault_root / AI_BLOG_DRAFTS_DIR).resolve()
                )
            )
            self.assertTrue(
                report_path.resolve().is_relative_to(
                    (vault_root / AI_BLOG_QUALITY_REPORTS_DIR).resolve()
                )
            )

    def test_unsafe_draft_id_cannot_be_persisted(self) -> None:
        package = _blog_package(draft_id="../escape")

        with self.assertRaises(BlogDraftPersistenceError):
            render_blog_draft_markdown(package)

        with self.assertRaises(BlogDraftPersistenceError):
            render_blog_quality_report(package)

    def test_unsafe_quality_report_id_cannot_be_persisted(self) -> None:
        package = _blog_package(report_id="../report")

        with self.assertRaises(BlogDraftPersistenceError):
            render_blog_draft_markdown(package)


def _blog_package(
    *,
    draft_id: str = "blog_draft_trial_ab12cd",
    report_id: str = "report_blog_draft_trial_ab12cd",
    unsupported: bool = False,
) -> BlogDraftPackage:
    claim = ClaimInventoryItem(
        claim_id="unit_blog_claim_ab12cd",
        title="Draft packages keep evidence visible",
        source_unit_id="unit_blog_claim_ab12cd",
        source_refs=() if unsupported else (_source_ref(),),
        unsupported=unsupported,
    )
    unsupported_claims = (claim,) if unsupported else ()
    source_unit_ids = ("unit_blog_context_ab12cd", "unit_blog_claim_ab12cd")
    draft = BlogDraft(
        id=draft_id,
        title="Blog Draft Persistence",
        mode=BlogMode.EXPLANATION,
        audience="knowledge workers",
        reader_problem="reviewing generated drafts before publishing",
        outline=("Blog draft package", "Evidence coverage"),
        claim_inventory=(claim,),
        content=(
            "# Blog Draft Persistence\n\n"
            "## Draft\n"
            "Durable draft packages make review artifacts inspectable.\n"
        ),
        unsupported_claims=unsupported_claims,
        source_unit_ids=source_unit_ids,
        quality_report_id=report_id,
    )
    quality_report = BlogQualityReport(
        id=report_id,
        target_id=draft_id,
        target_type="blog_draft",
        summary=(
            "warning: 2 source units covered; 1 unsupported claims reported"
            if unsupported
            else "passed: 2 source units covered; 0 unsupported claims reported"
        ),
        validation_status=BlogQualityStatus.WARNING if unsupported else BlogQualityStatus.PASSED,
        risks=(
            ("unsupported claims are present and must be reviewed",)
            if unsupported
            else ()
        ),
        unsupported_claims=(claim.claim_id,) if unsupported else (),
        evidence_coverage=(
            EvidenceCoverageItem(
                unit_id="unit_blog_context_ab12cd",
                has_source_refs=True,
                source_ref_count=1,
                unsupported=False,
            ),
            EvidenceCoverageItem(
                unit_id=claim.claim_id,
                has_source_refs=not unsupported,
                source_ref_count=0 if unsupported else 1,
                unsupported=unsupported,
            ),
        ),
        suggested_actions=(
            ("review unsupported claims before publication",)
            if unsupported
            else ("review draft tone and structure before publication",)
        ),
    )
    return BlogDraftPackage(draft=draft, quality_report=quality_report)


def _source_ref() -> SourceRef:
    return SourceRef(
        source_id="raw_essay_blog_draft_ab12cd",
        source_path="00-inbox/blog-draft.md",
        source_span="lines 1-3",
        origin=SourceOrigin.USER_TEXT,
        line_start=1,
        line_end=3,
        content_hash="sha256:source",
    )


if __name__ == "__main__":
    unittest.main()
