import unittest

from diamonddust.ai import (
    EXTRACTION_OUTPUT_SCHEMA_ID,
    EXTRACTION_OUTPUT_SCHEMA_VERSION,
    EXTRACT_UNITS_PROMPT_VERSION,
    ModelPolicyError,
    PromptRenderError,
    ProviderModelSettings,
    ProviderRequest,
    compute_ai_output_hash,
    extraction_output_json_schema,
    render_extract_units_prompt,
)
from diamonddust.application import (
    ExtractUnitsProviderRequestSpec,
    build_extract_units_provider_request,
)
from diamonddust.storage import ingest_markdown_text


class PromptRendererTests(unittest.TestCase):
    def test_renders_extract_units_prompt_from_provider_request(self) -> None:
        request = _request()

        prompt = render_extract_units_prompt(request)

        self.assertEqual(prompt.run_id, request.run_id)
        self.assertEqual(prompt.task, "extract_units")
        self.assertEqual(prompt.prompt_version, EXTRACT_UNITS_PROMPT_VERSION)
        self.assertEqual(prompt.schema_version, EXTRACTION_OUTPUT_SCHEMA_VERSION)
        self.assertEqual(prompt.input_hash, request.input_hash)
        self.assertEqual(prompt.source_input_id, "raw_essay_prompt_renderer_ab12cd")
        self.assertEqual(prompt.source_path, "00-inbox/prompt-renderer.md")
        self.assertEqual(prompt.output_schema_id, EXTRACTION_OUTPUT_SCHEMA_ID)
        self.assertEqual(prompt.output_schema_version, EXTRACTION_OUTPUT_SCHEMA_VERSION)
        self.assertEqual(
            prompt.output_schema_hash,
            compute_ai_output_hash(extraction_output_json_schema()),
        )
        self.assertEqual(
            prompt.output_schema["$id"],
            "diamonddust.extract_units.output.v0",
        )
        self.assertTrue(prompt.prompt_hash.startswith("sha256:"))
        self.assertIn("Return structured JSON only.", prompt.system_prompt)
        self.assertIn("Put note background, domain, scope", prompt.system_prompt)
        self.assertIn("Do not omit required fields.", prompt.system_prompt)
        self.assertIn("Do not generate KnowledgePatch", prompt.system_prompt)
        self.assertIn("source_input_id as immutable request context", prompt.system_prompt)
        self.assertIn("source_input_id: raw_essay_prompt_renderer_ab12cd", prompt.user_prompt)
        self.assertIn(
            "unit_id_prefix: unit_raw_essay_prompt_renderer_ab12cd_",
            prompt.user_prompt,
        )
        self.assertIn(
            "top-level source_input_id must be exactly: raw_essay_prompt_renderer_ab12cd",
            prompt.user_prompt,
        )
        self.assertIn(
            "source_context.source_input_id must be exactly: raw_essay_prompt_renderer_ab12cd",
            prompt.user_prompt,
        )
        self.assertIn("source_context stores whole-note background", prompt.user_prompt)
        self.assertIn(
            "every unit candidate id must be non-empty and begin with: unit_raw_essay_prompt_renderer_ab12cd_",
            prompt.user_prompt,
        )
        self.assertIn(
            "every unit candidate source_refs item must use source_id exactly: raw_essay_prompt_renderer_ab12cd",
            prompt.user_prompt,
        )
        self.assertIn('"id": "raw_essay_prompt_renderer_ab12cd"', prompt.user_prompt)
        self.assertIn('"origin": "user_text"', prompt.user_prompt)
        self.assertIn("Markdown body:", prompt.user_prompt)
        self.assertIn("Prompt rendering preserves source context.", prompt.user_prompt)
        self.assertIn("unit_candidates", prompt.output_instructions)
        self.assertIn("source_context", prompt.output_instructions)
        self.assertIn("Do not create raw_essay unit candidates", prompt.output_instructions)
        self.assertIn("relation_candidates may be empty", prompt.output_instructions)
        self.assertIn(
            "source_input_id value must exactly equal the source_input_id",
            prompt.output_instructions,
        )
        self.assertIn(
            "Every unit_candidates item must include a non-empty id field.",
            prompt.output_instructions,
        )
        self.assertIn(
            "unit_raw_essay_prompt_renderer_ab12cd_<short_label>",
            prompt.output_instructions,
        )
        self.assertIn("Knowledge language policy:", prompt.output_instructions)
        self.assertIn(
            "Write generated user-facing knowledge fields in Simplified Chinese",
            prompt.output_instructions,
        )
        self.assertIn(
            "source_context.knowledge_domains, source_context.background",
            prompt.output_instructions,
        )
        self.assertIn(
            "Preserve code, commands, identifiers, product names, file paths, and API names",
            prompt.output_instructions,
        )
        self.assertIn(
            "Keep JSON field names, enum values, schema_version values, and candidate ids",
            prompt.output_instructions,
        )
        self.assertIn(
            "All enum-valued fields must be JSON strings",
            prompt.output_instructions,
        )
        self.assertIn(
            'source_context.source_shape must be one of: "engineering_procedure_note", "study_note", "scratch_note", "long_article", "experiment_record", "reflection"',
            prompt.output_instructions,
        )
        self.assertIn(
            'unit_candidates[].type must be one of: "raw_essay", "question", "evidence", "concept", "claim", "synthesis", "map", "article"',
            prompt.output_instructions,
        )
        self.assertIn(
            'unit_candidates[].status must be one of: "seedling", "budding", "evergreen", "outdated", "superseded"',
            prompt.output_instructions,
        )
        self.assertIn("source_ref fields exactly", prompt.output_instructions)
        self.assertIn(
            "Output schema id: diamonddust.extract_units.output.v0",
            prompt.output_instructions,
        )
        self.assertIn(prompt.output_schema_hash, prompt.output_instructions)
        self.assertIn(
            '"$id": "diamonddust.extract_units.output.v0"',
            prompt.output_instructions,
        )

        mapping = prompt.to_mapping()
        self.assertEqual(mapping["prompt_hash"], prompt.prompt_hash)
        self.assertEqual(mapping["source_path"], "00-inbox/prompt-renderer.md")
        self.assertEqual(mapping["output_schema_id"], EXTRACTION_OUTPUT_SCHEMA_ID)
        self.assertEqual(mapping["output_schema_hash"], prompt.output_schema_hash)
        self.assertEqual(
            mapping["output_schema"]["$id"],
            prompt.output_schema["$id"],
        )

    def test_prompt_hash_is_stable_for_same_request(self) -> None:
        request = _request()

        first = render_extract_units_prompt(request)
        second = render_extract_units_prompt(request)

        self.assertEqual(first.prompt_hash, second.prompt_hash)

    def test_prompt_renderer_rejects_unsupported_prompt_version(self) -> None:
        request = build_extract_units_provider_request(
            _essay(),
            _spec(prompt_version="extract_units.experimental"),
        )

        with self.assertRaises(PromptRenderError):
            render_extract_units_prompt(request)

    def test_prompt_renderer_rejects_unsupported_output_schema_version(self) -> None:
        request = build_extract_units_provider_request(
            _essay(),
            _spec(schema_version="0.1.0"),
        )

        with self.assertRaises(PromptRenderError):
            render_extract_units_prompt(request)

    def test_prompt_renderer_validates_model_policy_before_rendering(self) -> None:
        request = _direct_request(
            settings=ProviderModelSettings(
                provider="future-provider",
                model="future-model",
                prompt_version=EXTRACT_UNITS_PROMPT_VERSION,
                schema_version=EXTRACTION_OUTPUT_SCHEMA_VERSION,
                real_provider_calls_enabled=True,
            )
        )

        with self.assertRaises(ModelPolicyError):
            render_extract_units_prompt(request)

    def test_prompt_renderer_rejects_invalid_payload_shape(self) -> None:
        payload = dict(_request().input_payload)
        payload.pop("source_ref")
        request = _direct_request(input_payload=payload)

        with self.assertRaises(PromptRenderError):
            render_extract_units_prompt(request)


def _essay():
    return ingest_markdown_text(
        """---
id: raw_essay_prompt_renderer_ab12cd
tags:
  - ai
  - prompt
---
# Prompt renderer

Prompt rendering preserves source context.
""",
        source_path="00-inbox/prompt-renderer.md",
        source_name="prompt-renderer",
    )


def _spec(
    *,
    prompt_version: str = EXTRACT_UNITS_PROMPT_VERSION,
    schema_version: str = EXTRACTION_OUTPUT_SCHEMA_VERSION,
) -> ExtractUnitsProviderRequestSpec:
    return ExtractUnitsProviderRequestSpec(
        run_id="run_prompt_renderer_ab12cd",
        provider="fake-provider",
        model="fake-structured-model",
        prompt_version=prompt_version,
        schema_version=schema_version,
    )


def _request() -> ProviderRequest:
    return build_extract_units_provider_request(_essay(), _spec())


def _direct_request(
    *,
    input_payload=None,
    settings: ProviderModelSettings | None = None,
) -> ProviderRequest:
    base_request = _request()
    return ProviderRequest(
        run_id=base_request.run_id,
        task=base_request.task,
        input_hash=base_request.input_hash,
        input_payload=input_payload or base_request.input_payload,
        settings=settings or base_request.settings,
        structured_output_required=True,
    )


if __name__ == "__main__":
    unittest.main()
