import unittest

from diamonddust.ai import (
    EXTRACT_UNITS_PROMPT_VERSION,
    ModelPolicyError,
    PromptRenderError,
    ProviderModelSettings,
    ProviderRequest,
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
        self.assertEqual(prompt.schema_version, "0.1.0")
        self.assertEqual(prompt.input_hash, request.input_hash)
        self.assertEqual(prompt.source_input_id, "raw_essay_prompt_renderer_ab12cd")
        self.assertEqual(prompt.source_path, "00-inbox/prompt-renderer.md")
        self.assertTrue(prompt.prompt_hash.startswith("sha256:"))
        self.assertIn("Return structured JSON only.", prompt.system_prompt)
        self.assertIn("Do not generate KnowledgePatch", prompt.system_prompt)
        self.assertIn("source_input_id: raw_essay_prompt_renderer_ab12cd", prompt.user_prompt)
        self.assertIn('"id": "raw_essay_prompt_renderer_ab12cd"', prompt.user_prompt)
        self.assertIn('"origin": "user_text"', prompt.user_prompt)
        self.assertIn("Markdown body:", prompt.user_prompt)
        self.assertIn("Prompt rendering preserves source context.", prompt.user_prompt)
        self.assertIn("unit_candidates", prompt.output_instructions)
        self.assertIn("relation_candidates may be empty", prompt.output_instructions)

        mapping = prompt.to_mapping()
        self.assertEqual(mapping["prompt_hash"], prompt.prompt_hash)
        self.assertEqual(mapping["source_path"], "00-inbox/prompt-renderer.md")

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

    def test_prompt_renderer_validates_model_policy_before_rendering(self) -> None:
        request = _direct_request(
            settings=ProviderModelSettings(
                provider="future-provider",
                model="future-model",
                prompt_version=EXTRACT_UNITS_PROMPT_VERSION,
                schema_version="0.1.0",
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
) -> ExtractUnitsProviderRequestSpec:
    return ExtractUnitsProviderRequestSpec(
        run_id="run_prompt_renderer_ab12cd",
        provider="fake-provider",
        model="fake-structured-model",
        prompt_version=prompt_version,
        schema_version="0.1.0",
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
