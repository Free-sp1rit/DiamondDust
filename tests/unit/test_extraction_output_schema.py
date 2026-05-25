import json
import unittest
from pathlib import Path

from diamonddust.ai import (
    EXTRACTION_OUTPUT_SCHEMA_ID,
    EXTRACTION_OUTPUT_SCHEMA_VERSION,
    AIRunMetadata,
    extraction_output_json_schema,
    validate_extraction_output,
)
from diamonddust.domain import Confidence, RelationType, SourceOrigin, Status, UnitType


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_EXTRACTION_JSON = ROOT / "tests" / "fixtures" / "local_trial" / "extraction.json"


class ExtractionOutputSchemaTests(unittest.TestCase):
    def test_schema_is_json_serializable_and_identified(self) -> None:
        schema = extraction_output_json_schema()

        encoded = json.dumps(schema, sort_keys=True)
        decoded = json.loads(encoded)

        self.assertEqual(decoded["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(decoded["$id"], EXTRACTION_OUTPUT_SCHEMA_ID)
        self.assertEqual(
            decoded["$defs"]["knowledge_unit"]["properties"]["schema_version"],
            {"const": EXTRACTION_OUTPUT_SCHEMA_VERSION},
        )

    def test_schema_top_level_shape_matches_extraction_output(self) -> None:
        schema = extraction_output_json_schema()

        self.assertEqual(schema["type"], "object")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            schema["required"],
            ["source_input_id", "unit_candidates", "relation_candidates"],
        )
        self.assertEqual(
            schema["properties"]["unit_candidates"]["items"]["$ref"],
            "#/$defs/knowledge_unit",
        )
        self.assertEqual(
            schema["properties"]["relation_candidates"]["items"]["$ref"],
            "#/$defs/relation",
        )

    def test_schema_enums_match_domain_enums(self) -> None:
        schema = extraction_output_json_schema()
        unit_properties = schema["$defs"]["knowledge_unit"]["properties"]
        relation_properties = schema["$defs"]["relation"]["properties"]
        source_ref_properties = schema["$defs"]["source_ref"]["properties"]

        self.assertEqual(
            unit_properties["type"]["enum"],
            [member.value for member in UnitType],
        )
        self.assertEqual(
            unit_properties["status"]["enum"],
            [member.value for member in Status],
        )
        self.assertEqual(
            unit_properties["confidence"]["enum"],
            [member.value for member in Confidence],
        )
        self.assertEqual(
            relation_properties["relation_type"]["enum"],
            [member.value for member in RelationType],
        )
        self.assertEqual(
            source_ref_properties["origin"]["enum"],
            [member.value for member in SourceOrigin],
        )

    def test_schema_documents_runtime_source_ref_boundary(self) -> None:
        schema = extraction_output_json_schema()
        unit_properties = schema["$defs"]["knowledge_unit"]["properties"]

        self.assertEqual(unit_properties["source_refs"]["minItems"], 1)
        self.assertIn("Required stable candidate id", unit_properties["id"]["description"])
        self.assertIn("unit_", unit_properties["id"]["description"])
        self.assertIn("source_ref whose source_id matches", schema["$comment"])
        self.assertIn("does not authorize provider calls", schema["$comment"])

    def test_checked_in_fixture_matches_runtime_contract(self) -> None:
        fixture = json.loads(FIXTURE_EXTRACTION_JSON.read_text(encoding="utf-8"))

        result = validate_extraction_output(
            fixture,
            AIRunMetadata(
                run_id="run_extraction_schema_fixture_validation",
                task="extract_units",
                provider="fixture",
                model="structured-json",
                prompt_version="extract_units.v1",
                schema_version=EXTRACTION_OUTPUT_SCHEMA_VERSION,
                input_hash="sha256:fixture-input",
            ),
        )

        self.assertTrue(result.is_valid, result.errors)


if __name__ == "__main__":
    unittest.main()
