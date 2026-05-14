import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from diamonddust.storage import (
    LocalTrialFeedbackReportError,
    LocalTrialFeedbackReportInput,
    render_local_trial_feedback_report,
    render_local_trial_outcome,
    write_local_trial_feedback_report,
    write_local_trial_outcome,
)


CREATED_AT = "2026-05-14T00:00:00Z"


class LocalTrialFeedbackReportTests(unittest.TestCase):
    def test_render_report_keeps_boundaries_and_reading_order(self) -> None:
        report = render_local_trial_feedback_report(
            _report_input(
                written_paths=(
                    "_ai_reports/blog-quality/draft_trial.md",
                    "_ai_runs/run_trial.json",
                    "_ai_reports/local-trials/trial_report.md",
                )
            ),
            created_at=CREATED_AT,
        )

        self.assertEqual(report.relative_path, "_ai_reports/local-trials/trial_report.md")
        self.assertFalse(report.formal_write_performed)
        self.assertFalse(report.provider_called)
        self.assertIn("artifact_schema_version: \"0.1.0\"", report.content)
        self.assertIn("- formal_write_performed: false", report.content)
        self.assertIn("## Feedback Capture", report.content)
        self.assertIn("- trial_verdict: [ ] usable [ ] needs_changes [ ] blocked", report.content)
        self.assertIn("- formal_write_approval: false", report.content)
        self.assertIn("- patch_acceptance: false", report.content)
        self.assertLess(
            report.content.index("_ai_reports/local-trials/trial_report.md"),
            report.content.index("_ai_runs/run_trial.json"),
        )

    def test_write_report_stays_in_ai_reports_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp)
            report = write_local_trial_feedback_report(
                _report_input(),
                vault_root=vault_root,
                created_at=CREATED_AT,
            )

            output_path = vault_root / "_ai_reports/local-trials/trial_report.md"
            self.assertEqual(report.relative_path, "_ai_reports/local-trials/trial_report.md")
            self.assertTrue(output_path.exists())
            self.assertIn("# Local Trial Feedback Report", output_path.read_text(encoding="utf-8"))

    def test_render_outcome_keeps_machine_readable_boundaries(self) -> None:
        outcome = render_local_trial_outcome(
            _report_input(
                written_paths=(
                    "_ai_reports/local-trials/trial_report.md",
                    "_ai_reports/local-trials/trial_report.json",
                    "_ai_runs/run_trial.json",
                ),
            ),
            created_at=CREATED_AT,
        )

        payload = json.loads(outcome.content)
        self.assertEqual(outcome.relative_path, "_ai_reports/local-trials/trial_report.json")
        self.assertEqual(payload["artifact_type"], "local_trial_outcome")
        self.assertEqual(payload["artifact_schema_version"], "0.1.0")
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["paths"]["review_start"], "_ai_reports/local-trials/trial_report.md")
        self.assertEqual(payload["paths"]["json_outcome"], outcome.relative_path)
        self.assertEqual(payload["artifact_count"], 3)
        self.assertFalse(payload["boundaries"]["formal_write_performed"])
        self.assertFalse(payload["boundaries"]["provider_called"])
        self.assertFalse(payload["boundaries"]["formal_write_approval"])
        self.assertFalse(payload["boundaries"]["patch_acceptance"])
        self.assertEqual(payload["feedback_capture"]["status"], "pending_user_input")

    def test_write_outcome_stays_in_ai_reports_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            vault_root = Path(tmp)
            outcome = write_local_trial_outcome(
                _report_input(
                    written_paths=(
                        "_ai_reports/local-trials/trial_report.md",
                        "_ai_reports/local-trials/trial_report.json",
                    ),
                ),
                vault_root=vault_root,
                created_at=CREATED_AT,
            )

            output_path = vault_root / "_ai_reports/local-trials/trial_report.json"
            self.assertEqual(outcome.relative_path, "_ai_reports/local-trials/trial_report.json")
            self.assertTrue(output_path.exists())
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["paths"]["markdown_report"], "_ai_reports/local-trials/trial_report.md")

    def test_report_rejects_formal_writes(self) -> None:
        with self.assertRaises(LocalTrialFeedbackReportError):
            _report_input(formal_write_performed=True)


def _report_input(
    *,
    written_paths: tuple[str, ...] = ("_ai_reports/local-trials/trial_report.md",),
    formal_write_performed: bool = False,
) -> LocalTrialFeedbackReportInput:
    return LocalTrialFeedbackReportInput(
        trial_id="trial_report",
        source_input_id="raw_essay_report",
        passed=True,
        summary="passed: local trial trial_report wrote 1 artifacts",
        errors=(),
        written_paths=written_paths,
        patch_id="patch_trial_report",
        draft_id="draft_trial_report",
        unsupported_claims=(),
        formal_write_performed=formal_write_performed,
        provider_called=False,
    )


if __name__ == "__main__":
    unittest.main()
