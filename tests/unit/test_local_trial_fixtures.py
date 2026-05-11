import contextlib
import io
import json
import unittest
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


class LocalTrialFixtureTests(unittest.TestCase):
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


def _load_fixture_extraction() -> dict:
    return json.loads(EXTRACTION_PATH.read_text(encoding="utf-8"))


def _written_paths_from_output(output: str) -> tuple[str, ...]:
    paths: list[str] = []
    for line in output.splitlines():
        if line.startswith("- _ai_"):
            paths.append(line.removeprefix("- "))
    return tuple(paths)


if __name__ == "__main__":
    unittest.main()
