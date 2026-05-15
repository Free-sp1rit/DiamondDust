import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GUIDE_PATH = ROOT / "docs" / "guides" / "local-trial-user-feedback.md"
README_PATH = ROOT / "README.md"


class LocalTrialUserFeedbackGuideTests(unittest.TestCase):
    def test_guide_points_to_fixture_trial_and_feedback_report(self) -> None:
        guide = GUIDE_PATH.read_text(encoding="utf-8")

        self.assertIn("python3 -m pip install -e .", guide)
        self.assertIn("diamonddust local-trial-fixture", guide)
        self.assertIn("diamonddust local-trial", guide)
        self.assertIn("PYTHONPATH=src python3 -m diamonddust local-trial-fixture", guide)
        self.assertIn("packaged provider-free fixture assets", guide)
        self.assertIn("from any working directory", guide)
        self.assertIn(
            "knowledge-vault/_ai_reports/local-trials/trial_fixture_ab12cd.md",
            guide,
        )
        self.assertIn("docs/guides/local-trial-extraction-json.md", guide)

    def test_guide_preserves_safety_boundaries(self) -> None:
        guide = GUIDE_PATH.read_text(encoding="utf-8")

        self.assertIn("AI working artifacts only", guide)
        self.assertIn("must not write formal vault notes", guide)
        self.assertIn("formal_write: false", guide)
        self.assertIn("provider_called: false", guide)
        self.assertIn("run_scope: \"provider_free_fixture\"", guide)
        self.assertIn("real_provider_call: false", guide)
        self.assertIn("fixture_driven: true", guide)
        self.assertIn("prompt_used: false", guide)
        self.assertIn("metrics_scope", guide)
        self.assertIn("patch_acceptance: false", guide)
        self.assertIn("formal_write_approval: false", guide)

    def test_readme_links_to_user_feedback_guide(self) -> None:
        readme = README_PATH.read_text(encoding="utf-8")

        self.assertIn("docs/guides/local-trial-user-feedback.md", readme)


if __name__ == "__main__":
    unittest.main()
