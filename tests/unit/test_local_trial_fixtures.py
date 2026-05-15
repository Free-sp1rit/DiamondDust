import contextlib
import io
import json
import os
import unittest
from importlib import resources
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.ai import AIRunMetadata, validate_extraction_output
from diamonddust.cli import main as cli_main
from diamonddust.storage import ARTIFACT_SCHEMA_VERSION, read_markdown_essay


CREATED_AT = "2026-05-11T00:00:00Z"
REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "local_trial"
ESSAY_PATH = FIXTURE_DIR / "trial-essay.md"
EXTRACTION_PATH = FIXTURE_DIR / "extraction.json"
PACKAGE_FIXTURE_PACKAGE = "diamonddust.fixtures.local_trial"


class LocalTrialFixtureTests(unittest.TestCase):
    def test_packaged_fixture_assets_match_repository_fixtures(self) -> None:
        package_fixtures = resources.files(PACKAGE_FIXTURE_PACKAGE)

        self.assertEqual(
            package_fixtures.joinpath("trial-essay.md").read_text(encoding="utf-8"),
            ESSAY_PATH.read_text(encoding="utf-8"),
        )
        self.assertEqual(
            json.loads(package_fixtures.joinpath("extraction.json").read_text(encoding="utf-8")),
            _load_fixture_extraction(),
        )

    def test_fixture_extraction_matches_ingested_essay_source_id(self) -> None:
        essay = read_markdown_essay(ESSAY_PATH, root=REPO_ROOT)
        extraction = _load_fixture_extraction()

        self.assertEqual(extraction["source_input_id"], essay.source_id)

        result = validate_extraction_output(
            extraction,
            AIRunMetadata(
                run_id="run_local_trial_fixture_validation",
                task="extract_units",
                provider="fixture",
                model="fixture-structured-json",
                prompt_version="extract_units.v1",
                schema_version="0.1.0",
                input_hash=essay.raw_content_hash,
            ),
        )

        self.assertTrue(result.is_valid, result.errors)
        self.assertIsNotNone(result.proposal)
        self.assertEqual(len(result.proposal.unit_candidates), 3)
        self.assertEqual(len(result.proposal.relation_candidates), 2)

    def test_fixture_cli_local_trial_writes_reviewable_artifacts(self) -> None:
        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp) / "knowledge-vault"
            stdout = io.StringIO()
            stderr = io.StringIO()

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = cli_main(
                    [
                        "local-trial",
                        "--trial-id",
                        "trial_fixture_ab12cd",
                        "--essay",
                        ESSAY_PATH.as_posix(),
                        "--extraction-json",
                        EXTRACTION_PATH.as_posix(),
                        "--root",
                        REPO_ROOT.as_posix(),
                        "--vault-root",
                        vault_root.as_posix(),
                        "--title",
                        "Reviewable Local Trial Artifacts",
                        "--mode",
                        "explanation",
                        "--audience",
                        "product owner",
                        "--reader-problem",
                        "inspecting generated artifacts before formal writes",
                        "--created-at",
                        CREATED_AT,
                    ]
                )

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0, stderr.getvalue())
            self.assertIn("passed: local trial trial_fixture_ab12cd", output)
            self.assertIn("formal_write_performed: false", output)
            self.assertIn("provider_called: false", output)
            self.assertIn("_ai_runs/run_trial_fixture_ab12cd_local_trial.json", output)
            self.assertIn("_ai_suggestions/patches/", output)
            self.assertIn("_ai_reports/patch-reviews/", output)
            self.assertIn("_ai_suggestions/blog-drafts/draft_trial_fixture_ab12cd/draft.md", output)
            self.assertIn("_ai_reports/blog-quality/draft_trial_fixture_ab12cd.md", output)
            self.assertIn("_ai_reports/local-trials/trial_fixture_ab12cd.md", output)
            self.assertIn("_ai_reports/local-trials/trial_fixture_ab12cd.json", output)
            self.assertFalse((vault_root / "70-publications").exists())

            for path in _written_paths_from_output(output):
                content = (vault_root / path).read_text(encoding="utf-8")
                self.assertTrue(
                    (
                        "artifact_schema_version" in content
                        or f"Artifact schema version: `{ARTIFACT_SCHEMA_VERSION}`" in content
                    ),
                    path,
                )
            run_log = json.loads(
                (
                    vault_root / "_ai_runs/run_trial_fixture_ab12cd_local_trial.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(run_log["trial_id"], "trial_fixture_ab12cd")
            self.assertEqual(run_log["stage_label"], "local_trial_artifact_pipeline")
            self.assertEqual(run_log["run_scope"], "provider_free_fixture")
            self.assertFalse(run_log["real_provider_call"])
            self.assertTrue(run_log["fixture_driven"])
            self.assertFalse(run_log["prompt_used"])
            self.assertFalse(run_log["metrics_scope"]["cost_applicable"])
            self.assertFalse(run_log["metrics_scope"]["latency_applicable"])
            self.assertEqual(
                run_log["source_input_id"], "raw_essay_local_trial_fixture_ab12cd"
            )
            manifest = (
                vault_root
                / "_ai_suggestions/candidate-notes"
                / "patch_raw_essay_local_trial_fixture_ab12cd_c2043bdc1b02"
                / "manifest.md"
            ).read_text(encoding="utf-8")
            self.assertIn("## Candidate Preview Boundary", manifest)
            self.assertIn("## Patch Operation Source of Truth", manifest)
            self.assertIn("## Fixture SourceRef Scope", manifest)
            patch_review = (
                vault_root
                / "_ai_reports/patch-reviews/patch_raw_essay_local_trial_fixture_ab12cd_c2043bdc1b02.md"
            ).read_text(encoding="utf-8")
            self.assertIn("artifact_type: patch_review_report", patch_review)
            self.assertIn('trial_id: "trial_fixture_ab12cd"', patch_review)
            self.assertIn('review_scope: "provider_free_fixture"', patch_review)
            self.assertIn("patch_acceptance: false", patch_review)
            self.assertIn('decision_status: "pending"', patch_review)
            self.assertIn("Candidate notes are fixture-driven previews", patch_review)
            self.assertIn("## Suggested Review Order", patch_review)
            self.assertIn("## Review Decision Prompt", patch_review)
            draft = (
                vault_root
                / "_ai_suggestions/blog-drafts/draft_trial_fixture_ab12cd/draft.md"
            ).read_text(encoding="utf-8")
            self.assertIn("requires_user_review: true", draft)
            self.assertIn('draft_scope: "provider_free_fixture"', draft)
            self.assertIn("real_ai_generation_validated: false", draft)
            self.assertIn(
                "unit_local_trial_visible_artifacts_ab12cd: "
                "Visible intermediate artifacts build trust "
                "(supporting concept; supported)",
                draft,
            )

    def test_fixture_shortcut_cli_writes_reviewable_artifacts(self) -> None:
        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp) / "knowledge-vault"
            stdout = io.StringIO()
            stderr = io.StringIO()

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = cli_main(
                    [
                        "local-trial-fixture",
                        "--root",
                        REPO_ROOT.as_posix(),
                        "--vault-root",
                        vault_root.as_posix(),
                        "--created-at",
                        CREATED_AT,
                    ]
                )

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0, stderr.getvalue())
            self.assertIn("passed: local trial trial_fixture_ab12cd", output)
            self.assertIn("formal_write_performed: false", output)
            self.assertIn("provider_called: false", output)
            self.assertIn("_ai_reports/local-trials/trial_fixture_ab12cd.md", output)
            self.assertIn("_ai_reports/local-trials/trial_fixture_ab12cd.json", output)
            self.assertFalse((vault_root / "70-publications").exists())
            self.assertTrue(
                (vault_root / "_ai_reports/local-trials/trial_fixture_ab12cd.md").exists()
            )
            self.assertTrue(
                (vault_root / "_ai_reports/local-trials/trial_fixture_ab12cd.json").exists()
            )

    def test_fixture_shortcut_cli_runs_outside_repository_root(self) -> None:
        with TemporaryDirectory() as tmp:
            outside_root = Path(tmp) / "outside"
            outside_root.mkdir()
            vault_root = Path(tmp) / "knowledge-vault"
            stdout = io.StringIO()
            stderr = io.StringIO()

            with _working_directory(outside_root):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = cli_main(
                        [
                            "local-trial-fixture",
                            "--vault-root",
                            vault_root.as_posix(),
                            "--created-at",
                            CREATED_AT,
                        ]
                    )

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0, stderr.getvalue())
            self.assertIn("passed: local trial trial_fixture_ab12cd", output)
            self.assertIn("formal_write_performed: false", output)
            self.assertIn("provider_called: false", output)
            self.assertTrue(
                (vault_root / "_ai_reports/local-trials/trial_fixture_ab12cd.md").exists()
            )
            self.assertTrue(
                (vault_root / "_ai_reports/local-trials/trial_fixture_ab12cd.json").exists()
            )
            self.assertFalse((outside_root / "tests/fixtures/local_trial/trial-essay.md").exists())


def _load_fixture_extraction() -> dict:
    return json.loads(EXTRACTION_PATH.read_text(encoding="utf-8"))


def _written_paths_from_output(output: str) -> tuple[str, ...]:
    paths: list[str] = []
    for line in output.splitlines():
        if line.startswith("- _ai_"):
            paths.append(line.removeprefix("- "))
    return tuple(paths)


@contextlib.contextmanager
def _working_directory(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
