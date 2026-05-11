import contextlib
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.application import BlogMode, LocalTrialSpec, run_local_trial
from diamonddust.cli import main as cli_main


CREATED_AT = "2026-05-11T00:00:00Z"
SOURCE_ID = "raw_essay_local_trial_ab12cd"


class LocalTrialHarnessTests(unittest.TestCase):
    def test_local_trial_writes_all_inspectable_artifacts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            essay_path = _write_essay(root)
            vault_root = root / "knowledge-vault"

            result = run_local_trial(
                _trial_spec(essay_path.as_posix()),
                root=root,
                vault_root=vault_root,
                created_at=CREATED_AT,
            )

            self.assertTrue(result.passed)
            self.assertTrue(result.ingested)
            self.assertTrue(result.extraction_valid)
            self.assertTrue(result.ai_run_log_written)
            self.assertTrue(result.review_package_written)
            self.assertTrue(result.blog_draft_package_written)
            self.assertTrue(result.simulated_patch_acceptance)
            self.assertFalse(result.formal_write_performed)
            self.assertFalse(result.provider_called)
            self.assertEqual(result.source_input_id, SOURCE_ID)
            self.assertTrue(result.patch_id.startswith("patch_"))
            self.assertEqual(result.draft_id, "draft_trial_local_ab12cd")
            self.assertEqual(result.errors, ())
            self.assertTrue(any(path.startswith("_ai_runs/") for path in result.written_paths))
            self.assertTrue(any(path.startswith("_ai_suggestions/patches/") for path in result.written_paths))
            self.assertTrue(any(path.startswith("_ai_reports/patch-reviews/") for path in result.written_paths))
            self.assertIn(
                "_ai_suggestions/blog-drafts/draft_trial_local_ab12cd/draft.md",
                result.written_paths,
            )
            self.assertIn(
                "_ai_reports/blog-quality/draft_trial_local_ab12cd.md",
                result.written_paths,
            )
            self.assertTrue(all((vault_root / path).exists() for path in result.written_paths))
            self.assertFalse(
                (vault_root / "70-publications" / "draft_trial_local_ab12cd.md").exists()
            )

    def test_invalid_extraction_fails_safely_and_persists_run_log(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            essay_path = _write_essay(root)
            vault_root = root / "knowledge-vault"
            spec = _trial_spec(essay_path.as_posix(), extraction_output="free form")

            result = run_local_trial(
                spec,
                root=root,
                vault_root=vault_root,
                created_at=CREATED_AT,
            )

            self.assertFalse(result.passed)
            self.assertTrue(result.ingested)
            self.assertFalse(result.extraction_valid)
            self.assertTrue(result.ai_run_log_written)
            self.assertFalse(result.review_package_written)
            self.assertFalse(result.blog_draft_package_written)
            self.assertEqual(len(result.written_paths), 1)
            self.assertTrue(result.written_paths[0].startswith("_ai_runs/"))
            self.assertIn("extraction output must be a structured mapping", result.errors[0])

    def test_source_id_mismatch_stops_before_review_artifacts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            essay_path = _write_essay(root)
            vault_root = root / "knowledge-vault"
            output = dict(_valid_extraction_output())
            output["source_input_id"] = "raw_essay_other"
            for unit in output["unit_candidates"]:
                unit["source_refs"] = [
                    {
                        **unit["source_refs"][0],
                        "source_id": "raw_essay_other",
                    }
                ]

            result = run_local_trial(
                _trial_spec(essay_path.as_posix(), extraction_output=output),
                root=root,
                vault_root=vault_root,
                created_at=CREATED_AT,
            )

            self.assertFalse(result.passed)
            self.assertTrue(result.extraction_valid)
            self.assertTrue(result.ai_run_log_written)
            self.assertFalse(result.review_package_written)
            self.assertIn("does not match ingested source_id", result.errors[0])

    def test_cli_local_trial_smoke(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            essay_path = _write_essay(root)
            extraction_path = root / "extraction.json"
            extraction_path.write_text(
                json.dumps(_valid_extraction_output()),
                encoding="utf-8",
            )
            vault_root = root / "knowledge-vault"
            stdout = io.StringIO()
            stderr = io.StringIO()

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = cli_main(
                    [
                        "local-trial",
                        "--trial-id",
                        "trial_local_ab12cd",
                        "--essay",
                        essay_path.as_posix(),
                        "--extraction-json",
                        extraction_path.as_posix(),
                        "--root",
                        root.as_posix(),
                        "--vault-root",
                        vault_root.as_posix(),
                        "--title",
                        "Local Trial",
                        "--mode",
                        "explanation",
                        "--audience",
                        "product owner",
                        "--reader-problem",
                        "checking local artifacts",
                        "--created-at",
                        CREATED_AT,
                    ]
                )

            self.assertEqual(exit_code, 0, stderr.getvalue())
            self.assertIn("passed: local trial trial_local_ab12cd", stdout.getvalue())
            self.assertIn("formal_write_performed: false", stdout.getvalue())
            self.assertIn("_ai_reports/blog-quality/draft_trial_local_ab12cd.md", stdout.getvalue())


def _trial_spec(
    essay_path: str,
    *,
    extraction_output: object | None = None,
) -> LocalTrialSpec:
    return LocalTrialSpec(
        trial_id="trial_local_ab12cd",
        essay_path=essay_path,
        extraction_output=(
            _valid_extraction_output() if extraction_output is None else extraction_output
        ),
        blog_title="Local Trial",
        blog_mode=BlogMode.EXPLANATION,
        audience="product owner",
        reader_problem="checking local artifacts",
    )


def _write_essay(root: Path) -> Path:
    inbox = root / "00-inbox"
    inbox.mkdir(parents=True)
    path = inbox / "local-trial.md"
    path.write_text(
        "---\n"
        f"id: {SOURCE_ID}\n"
        "---\n\n"
        "Local trial artifacts should make review boundaries visible.\n",
        encoding="utf-8",
    )
    return path


def _valid_extraction_output() -> dict:
    concept_id = "unit_local_trial_concept_ab12cd"
    claim_id = "unit_local_trial_claim_cd34ef"
    return {
        "source_input_id": SOURCE_ID,
        "unit_candidates": [
            _unit_data(
                id=concept_id,
                type="concept",
                title="Local trial artifacts",
                content="Local trial artifacts make generated outputs inspectable.",
            ),
            _unit_data(
                id=claim_id,
                type="claim",
                title="Review boundaries stay visible",
                content="Review boundaries stay visible when trial artifacts are separated.",
            ),
        ],
        "relation_candidates": [
            {
                "source_id": claim_id,
                "relation_type": "supports",
                "target_id": concept_id,
                "confidence": "medium",
                "reason": "The claim supports the local trial artifact concept.",
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
        "source_id": SOURCE_ID,
        "source_path": "00-inbox/local-trial.md",
        "source_span": "lines 5-5",
        "origin": "user_text",
        "line_start": 5,
        "line_end": 5,
        "content_hash": "sha256:source",
    }


if __name__ == "__main__":
    unittest.main()
