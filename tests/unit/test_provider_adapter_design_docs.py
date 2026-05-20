import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = ROOT / "docs" / "designs" / "2026-05-20-first-provider-adapter-design.md"
TEMPLATE_PATH = (
    ROOT / "docs" / "templates" / "PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md"
)
AI_CONTRACT_PATH = ROOT / "docs" / "06_AI_PIPELINE_CONTRACT.md"
README_PATH = ROOT / "README.md"


class ProviderAdapterDesignDocsTests(unittest.TestCase):
    def test_adapter_design_preserves_provider_boundaries(self) -> None:
        design = DESIGN_PATH.read_text(encoding="utf-8")

        self.assertIn("Status: design input only.", design)
        self.assertIn("task: `extract_units`", design)
        self.assertIn("ProviderExecutionClient.generate", design)
        self.assertIn("ProviderExecutionRequest", design)
        self.assertIn("ProviderResult", design)
        self.assertIn("It must not import", design)
        self.assertIn("storage adapters", design)
        self.assertIn("must not re-render prompts", design)
        self.assertIn("raw_output_persisted: false", design)
        self.assertIn("Live provider smoke must be opt-in", design)
        self.assertIn("PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md", design)

    def test_decision_package_template_requires_product_owner_approvals(self) -> None:
        template = TEMPLATE_PATH.read_text(encoding="utf-8")

        required_fields = (
            "first_provider",
            "default_model",
            "provider_sdk_dependency",
            "api_key_env_var",
            "real_provider_calls_approved",
            "real_network_calls_approved",
            "prompt_text_external_approved",
            "structured_output_mechanism",
            "timeout_seconds",
            "max_retries",
            "cost_limit",
            "fallback_behavior",
            "raw_output_retention",
            "allowed_tasks",
        )
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, template)

        self.assertIn("records_real_provider_approval: false", template)
        self.assertIn("key_value_in_package: forbidden", template)
        self.assertIn("domain core imports no provider SDK", template)
        self.assertIn("default CI does not call real provider", template)
        self.assertIn("approved for first real provider implementation", template)

    def test_readme_and_ai_contract_point_to_design_package(self) -> None:
        readme = README_PATH.read_text(encoding="utf-8")
        contract = AI_CONTRACT_PATH.read_text(encoding="utf-8")

        self.assertIn("2026-05-20-first-provider-adapter-design.md", readme)
        self.assertIn("PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md", readme)
        self.assertIn("Provider Adapter Design Package", contract)
        self.assertIn("2026-05-20-first-provider-adapter-design.md", contract)
        self.assertIn("PROVIDER_ADAPTER_DECISION_PACKAGE_TEMPLATE.md", contract)


if __name__ == "__main__":
    unittest.main()
