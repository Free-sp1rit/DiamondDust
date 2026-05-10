import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.application import (
    MVPReleaseError,
    MVPReleaseSample,
    MVPReleaseStatus,
    BlogMode,
    run_mvp_release_readiness,
    scan_critical_architecture_violations,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "mvp_release"
CREATED_AT = "2026-05-10T00:00:00Z"


class MVPReleaseReadinessTests(unittest.TestCase):
    def test_five_sample_essays_pass_end_to_end(self) -> None:
        report = run_mvp_release_readiness(_samples(), root=ROOT, created_at=CREATED_AT)

        self.assertEqual(report.status, MVPReleaseStatus.PASSED)
        self.assertTrue(report.is_ready)
        self.assertEqual(report.total_samples, 5)
        self.assertEqual(report.passed_sample_count, 5)
        self.assertEqual(report.release_errors, ())
        self.assertEqual(report.critical_architecture_violations, ())
        self.assertTrue(all(result.ingested for result in report.sample_results))
        self.assertTrue(all(result.extraction_valid for result in report.sample_results))
        self.assertTrue(all(result.patch_reviewed for result in report.sample_results))
        self.assertTrue(
            all(result.blog_draft_generated for result in report.sample_results)
        )
        self.assertTrue(all(result.source_unit_ids for result in report.sample_results))

    def test_requires_at_least_five_samples(self) -> None:
        report = run_mvp_release_readiness(_samples()[:4], root=ROOT, created_at=CREATED_AT)

        self.assertEqual(report.status, MVPReleaseStatus.FAILED)
        self.assertFalse(report.is_ready)
        self.assertEqual(report.total_samples, 4)
        self.assertIn("at least 5 sample essays", report.release_errors[0])

    def test_source_id_mismatch_fails_safely_before_extraction(self) -> None:
        samples = _samples()
        samples[0] = _sample(1, source_id="raw_essay_wrong_source")

        report = run_mvp_release_readiness(samples, root=ROOT, created_at=CREATED_AT)
        failed = report.sample_results[0]

        self.assertEqual(report.status, MVPReleaseStatus.FAILED)
        self.assertFalse(failed.passed)
        self.assertTrue(failed.ingested)
        self.assertFalse(failed.extraction_valid)
        self.assertFalse(failed.patch_reviewed)
        self.assertIn("does not match ingested source_id", failed.errors[0])

    def test_failed_extraction_validation_fails_release(self) -> None:
        samples = _samples()
        invalid_output = _output(1)
        first_unit = dict(invalid_output["unit_candidates"][0])  # type: ignore[index]
        first_unit["source_refs"] = []
        invalid_output["unit_candidates"][0] = first_unit  # type: ignore[index]
        samples[0] = MVPReleaseSample(
            sample_id="mvp_01",
            essay_path=_fixture_path(1),
            extraction_output=invalid_output,
            blog_title="MVP Sample 01",
            blog_mode=BlogMode.EXPLANATION,
            audience="knowledge workers",
            reader_problem="checking a complete local-first flow",
        )

        report = run_mvp_release_readiness(samples, root=ROOT, created_at=CREATED_AT)
        failed = report.sample_results[0]

        self.assertEqual(report.status, MVPReleaseStatus.FAILED)
        self.assertFalse(failed.passed)
        self.assertTrue(failed.ingested)
        self.assertFalse(failed.extraction_valid)
        self.assertFalse(failed.patch_reviewed)
        self.assertIn("must preserve source_refs", failed.errors[0])

    def test_release_readiness_does_not_write_fixture_or_vault_files(self) -> None:
        before = _fixture_file_state()
        before_vault = _path_state(ROOT / "knowledge-vault")

        report = run_mvp_release_readiness(_samples(), root=ROOT, created_at=CREATED_AT)

        self.assertTrue(report.is_ready)
        self.assertEqual(_fixture_file_state(), before)
        self.assertEqual(_path_state(ROOT / "knowledge-vault"), before_vault)

    def test_sample_requires_explicit_blog_mode(self) -> None:
        with self.assertRaises(MVPReleaseError):
            MVPReleaseSample(
                sample_id="mvp_bad_mode",
                essay_path=_fixture_path(1),
                extraction_output=_output(1),
                blog_title="Bad Mode",
                blog_mode="explanation",  # type: ignore[arg-type]
                audience="knowledge workers",
                reader_problem="checking explicit mode validation",
            )

    def test_architecture_scan_detects_forbidden_domain_import(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            domain_root = root / "src" / "diamonddust" / "domain"
            domain_root.mkdir(parents=True)
            (domain_root / "__init__.py").write_text("", encoding="utf-8")
            (domain_root / "bad.py").write_text("import openai\n", encoding="utf-8")

            violations = scan_critical_architecture_violations(root)

        self.assertEqual(
            violations,
            ("src/diamonddust/domain/bad.py: forbidden domain import openai",),
        )


def _samples() -> list[MVPReleaseSample]:
    return [_sample(index) for index in range(1, 6)]


def _sample(index: int, source_id: str | None = None) -> MVPReleaseSample:
    return MVPReleaseSample(
        sample_id=f"mvp_{index:02d}",
        essay_path=_fixture_path(index),
        extraction_output=_output(index, source_id=source_id),
        blog_title=f"MVP Sample {index:02d}",
        blog_mode=BlogMode.EXPLANATION,
        audience="knowledge workers",
        reader_problem="checking a complete local-first flow",
    )


def _output(index: int, source_id: str | None = None) -> dict[str, object]:
    source_id = source_id or f"raw_essay_20260510_mvp_{index:02d}"
    concept_id = f"unit_20260510_mvp_{index:02d}_concept"
    claim_id = f"unit_20260510_mvp_{index:02d}_claim"
    source_ref = _source_ref(index, source_id)

    return {
        "source_input_id": source_id,
        "unit_candidates": [
            {
                "id": concept_id,
                "type": "concept",
                "title": f"MVP Concept {index:02d}",
                "content": f"Concept extracted from MVP sample {index:02d}.",
                "status": "seedling",
                "source_refs": [source_ref],
                "relations": [],
                "confidence": "medium",
                "created_at": CREATED_AT,
                "updated_at": CREATED_AT,
                "schema_version": "0.1.0",
            },
            {
                "id": claim_id,
                "type": "claim",
                "title": f"MVP Claim {index:02d}",
                "content": f"Claim extracted from MVP sample {index:02d}.",
                "status": "seedling",
                "source_refs": [source_ref],
                "relations": [],
                "confidence": "medium",
                "created_at": CREATED_AT,
                "updated_at": CREATED_AT,
                "schema_version": "0.1.0",
            },
        ],
        "relation_candidates": [
            {
                "source_id": claim_id,
                "relation_type": "supports",
                "target_id": concept_id,
                "confidence": "medium",
                "reason": "The sample claim supports the extracted concept.",
            }
        ],
    }


def _source_ref(index: int, source_id: str) -> dict[str, object]:
    return {
        "source_id": source_id,
        "source_path": _fixture_path(index),
        "source_span": "lines 8-10",
        "origin": "user_text",
        "line_start": 8,
        "line_end": 10,
    }


def _fixture_path(index: int) -> str:
    return f"tests/fixtures/mvp_release/sample_{index:02d}.md"


def _fixture_file_state() -> tuple[str, ...]:
    return _path_state(FIXTURE_DIR)


def _path_state(path: Path) -> tuple[str, ...]:
    if not path.exists():
        return ()
    return tuple(sorted(item.relative_to(ROOT).as_posix() for item in path.rglob("*")))


if __name__ == "__main__":
    unittest.main()
