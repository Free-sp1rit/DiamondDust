import unittest
from pathlib import Path


class CIWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow_path = Path(".github/workflows/ci.yml")
        self.workflow = self.workflow_path.read_text(encoding="utf-8")

    def test_ci_workflow_exists(self) -> None:
        self.assertTrue(self.workflow_path.is_file())

    def test_ci_runs_on_prs_and_pushes(self) -> None:
        self.assertIn("pull_request:", self.workflow)
        self.assertIn("push:", self.workflow)

    def test_ci_uses_supported_python_versions(self) -> None:
        self.assertIn('"3.11"', self.workflow)
        self.assertIn('"3.12"', self.workflow)
        self.assertIn("actions/setup-python@v5", self.workflow)

    def test_ci_runs_required_validation_gates(self) -> None:
        required_commands = (
            "python -m pip wheel . --no-deps --wheel-dir",
            "python -m pip install --force-reinstall",
            "python -m pip check",
            "python -m unittest discover -s tests",
            "python -m compileall src tests",
            "git diff --check",
            "diamonddust local-trial-fixture",
        )
        for command in required_commands:
            with self.subTest(command=command):
                self.assertIn(command, self.workflow)

    def test_ci_uses_read_only_repository_permissions(self) -> None:
        self.assertIn("permissions:", self.workflow)
        self.assertIn("contents: read", self.workflow)

    def test_ci_default_path_is_provider_free(self) -> None:
        self.assertNotIn("DIAMONDDUST_OPENAI_API_KEY", self.workflow)
        self.assertNotIn("openai-extract-units", self.workflow)
        self.assertNotIn("live-smoke", self.workflow)


if __name__ == "__main__":
    unittest.main()
