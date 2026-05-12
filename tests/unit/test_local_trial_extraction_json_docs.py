import json
import unittest
from pathlib import Path

from diamonddust.ai import AIRunMetadata, validate_extraction_output


ROOT = Path(__file__).resolve().parents[2]
GUIDE_PATH = ROOT / "docs" / "guides" / "local-trial-extraction-json.md"
README_PATH = ROOT / "README.md"
EXAMPLE_START = "<!-- extraction-json-example:start -->"
EXAMPLE_END = "<!-- extraction-json-example:end -->"


class LocalTrialExtractionJsonDocsTests(unittest.TestCase):
    def test_guide_embedded_example_validates_as_extraction_output(self) -> None:
        example = _embedded_example()

        result = validate_extraction_output(
            example,
            AIRunMetadata(
                run_id="run_doc_example_validation",
                task="extract_units",
                provider="docs",
                model="structured-json-example",
                prompt_version="extract_units.v1",
                schema_version="0.1.0",
                input_hash="sha256:doc-example-input",
            ),
        )

        self.assertTrue(result.is_valid, result.errors)
        self.assertIsNotNone(result.proposal)
        self.assertEqual(len(result.proposal.unit_candidates), 2)
        self.assertEqual(len(result.proposal.relation_candidates), 1)

    def test_readme_links_to_extraction_json_guide(self) -> None:
        readme = README_PATH.read_text(encoding="utf-8")
        guide = GUIDE_PATH.read_text(encoding="utf-8")

        self.assertIn("docs/guides/local-trial-extraction-json.md", readme)
        self.assertIn("tests/fixtures/local_trial/extraction.json", guide)


def _embedded_example() -> object:
    guide = GUIDE_PATH.read_text(encoding="utf-8")
    section = guide.split(EXAMPLE_START, 1)[1].split(EXAMPLE_END, 1)[0]
    json_text = section.split("```json", 1)[1].split("```", 1)[0]
    return json.loads(json_text)


if __name__ == "__main__":
    unittest.main()
