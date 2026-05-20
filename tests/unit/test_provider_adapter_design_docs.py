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
        self.assertIn("first_provider: openai", design)
        self.assertIn("default_model: pending_owner_selection", design)
        self.assertIn("SDK Vs Direct HTTP Comparison", design)
        self.assertIn("Adapter Mapping Plan", design)
        self.assertIn("CLI Safety Valve Design", design)
        self.assertIn("CI Policy Design", design)
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
            "per_run_cost_limit",
            "per_day_cost_limit",
            "fallback_behavior",
            "raw_output_retention",
            "allowed_tasks",
        )
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, template)

        self.assertIn("records_real_provider_approval: false", template)
        self.assertIn("live_smoke_approval_status: pending", template)
        self.assertIn("[x] approved for real provider code implementation preparation", template)
        self.assertIn("[ ] approved for actual real provider code implementation", template)
        self.assertIn("[ ] approved for one manual live smoke run", template)
        self.assertIn("first_provider: openai", template)
        self.assertIn("default_model: pending_owner_selection", template)
        self.assertIn("integration_style: pending_comparison", template)
        self.assertIn("provider_sdk_dependency_approved: false", template)
        self.assertIn("api_key_env_var: DIAMONDDUST_OPENAI_API_KEY", template)
        self.assertIn("key_reading_allowed_in_real_provider_run: false", template)
        self.assertIn("provider_json_schema_if_supported", template)
        self.assertIn("stop_behavior_on_cost_limit: fail_closed", template)
        self.assertIn("full_raw_requires_explicit_approval", template)
        self.assertIn("key_value_in_package: forbidden", template)
        self.assertIn("domain core imports no provider SDK", template)
        self.assertIn("provider-specific request/response mapping is contained", template)
        self.assertIn("no provider-specific types leak", template)
        self.assertIn("payload preview shows what would be sent externally", template)
        self.assertIn("default CI does not call real provider", template)
        self.assertIn("actual real provider adapter implementation: not approved", template)

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
