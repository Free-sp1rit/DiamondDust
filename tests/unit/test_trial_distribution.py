import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile

from diamonddust.interface.trial_distribution import (
    TRIAL_DISTRIBUTION_ARTIFACT_TYPE,
    TrialDistributionConfig,
    TrialDistributionError,
    build_trial_distribution,
    trial_distribution_relative_paths,
)


class TrialDistributionTests(unittest.TestCase):
    def test_build_trial_distribution_writes_manifest_and_zip(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            _write_minimal_repo(root, include_frontend_dist=True)
            output_root = Path(tmp) / "dist"

            result = build_trial_distribution(
                TrialDistributionConfig(
                    repo_root=root,
                    output_root=output_root,
                    version="alpha-test",
                    created_at="2026-05-28T10:00:00+08:00",
                )
            )

            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
            start_here = (result.package_dir / "START_HERE.md").read_text(
                encoding="utf-8"
            )
            package_prefix = result.package_dir.name + "/"
            with zipfile.ZipFile(result.zip_path) as archive:
                zip_names = set(archive.namelist())

        self.assertEqual(manifest["artifact_type"], TRIAL_DISTRIBUTION_ARTIFACT_TYPE)
        self.assertEqual(manifest["version"], "alpha-test")
        self.assertTrue(manifest["include_frontend_dist"])
        self.assertFalse(manifest["boundaries"]["api_key_values_included"])
        self.assertFalse(manifest["boundaries"]["knowledge_vault_included"])
        self.assertFalse(manifest["boundaries"]["trial_runtime_dir_included"])
        self.assertFalse(manifest["boundaries"]["trial_run_settings_included"])
        self.assertFalse(manifest["boundaries"]["formal_write_enabled"])
        self.assertIn(".diamonddust-trial", start_here)
        self.assertIn(".diamonddust-trial/secrets/provider-secrets.env", start_here)
        self.assertIn(".diamonddust-trial/trial-client-settings.json", start_here)
        self.assertIn("trial-client-launch.log", start_here)
        self.assertIn("DIAMONDDUST_TRIAL_PORT", start_here)
        self.assertIn("Python 3.13", start_here)
        self.assertIn(".diamonddust-trial", manifest["excluded_by_policy"])
        self.assertIn("frontend/trial-client/dist", manifest["included_paths"])
        self.assertIn(package_prefix + "START_HERE.md", zip_names)
        self.assertIn(package_prefix + "TRIAL_RELEASE_MANIFEST.json", zip_names)
        self.assertIn(package_prefix + "start-diamonddust-trial.cmd", zip_names)
        self.assertIn(package_prefix + "frontend/trial-client/dist/index.html", zip_names)
        self.assertFalse(
            any(
                "provider-secrets.env" in name
                or "knowledge-vault" in name
                or "node_modules" in name
                or ".diamonddust-trial" in name
                or ".egg-info" in name
                or "/.git/" in name
                for name in zip_names
            )
        )

    def test_frontend_dist_is_required_by_default(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            _write_minimal_repo(root, include_frontend_dist=False)

            with self.assertRaisesRegex(
                TrialDistributionError,
                "frontend/trial-client/dist",
            ):
                build_trial_distribution(
                    TrialDistributionConfig(
                        repo_root=root,
                        output_root=Path(tmp) / "dist",
                        version="alpha-test",
                    )
                )

    def test_forbidden_secret_file_inside_allowlisted_tree_blocks_package(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            _write_minimal_repo(root, include_frontend_dist=True)
            (root / "scripts/windows/provider-secrets.env").write_text(
                "DIAMONDDUST_DEEPSEEK_API_KEY=SECRET\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(TrialDistributionError, "forbidden secret file"):
                build_trial_distribution(
                    TrialDistributionConfig(
                        repo_root=root,
                        output_root=Path(tmp) / "dist",
                        version="alpha-test",
                    )
                )

    def test_skip_frontend_dist_removes_dist_from_required_paths(self) -> None:
        self.assertNotIn(
            "frontend/trial-client/dist",
            trial_distribution_relative_paths(include_frontend_dist=False),
        )


def _write_minimal_repo(root: Path, *, include_frontend_dist: bool) -> None:
    (root / "src/diamonddust").mkdir(parents=True)
    (root / "src/diamonddust/__init__.py").write_text("", encoding="utf-8")
    (root / "src/diamonddust.egg-info").mkdir(parents=True)
    (root / "src/diamonddust.egg-info/PKG-INFO").write_text(
        "cached metadata\n",
        encoding="utf-8",
    )
    (root / "scripts/windows").mkdir(parents=True)
    (root / "scripts/windows/start-trial-client.cmd").write_text(
        "@echo off\n",
        encoding="utf-8",
    )
    (root / "scripts/windows/start-trial-client.ps1").write_text(
        'Write-Host "start"\n',
        encoding="utf-8",
    )
    (root / "docs/guides").mkdir(parents=True)
    (root / "docs/guides/trial-client.md").write_text("trial client\n", encoding="utf-8")
    (root / "docs/guides/trial-client-alpha-distribution.md").write_text(
        "distribution\n",
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text("[project]\nname='fake'\n", encoding="utf-8")
    (root / "README.md").write_text("# fake\n", encoding="utf-8")
    if include_frontend_dist:
        (root / "frontend/trial-client/dist").mkdir(parents=True)
        (root / "frontend/trial-client/dist/index.html").write_text(
            "<!doctype html>\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
