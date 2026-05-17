import os
import unittest

from diamonddust.ai import EXTRACTION_TASK
from diamonddust.application import (
    ProviderIntegrationDecisionSet,
    ProviderIntegrationReadinessError,
    ProviderIntegrationReadinessStatus,
    assess_provider_integration_readiness,
    provider_integration_decision_template_mapping,
    provider_integration_decisions_from_mapping,
    render_provider_integration_escalation_request_markdown,
    render_provider_integration_readiness_markdown,
)


class ProviderIntegrationReadinessTests(unittest.TestCase):
    def test_ready_when_all_provider_decisions_are_explicit(self) -> None:
        report = assess_provider_integration_readiness(_ready_decisions())

        self.assertTrue(report.is_ready)
        self.assertEqual(report.status, ProviderIntegrationReadinessStatus.READY)
        self.assertEqual(report.blockers, ())

    def test_missing_decisions_fail_closed(self) -> None:
        report = assess_provider_integration_readiness(ProviderIntegrationDecisionSet())

        self.assertFalse(report.is_ready)
        self.assertEqual(report.status, ProviderIntegrationReadinessStatus.BLOCKED)
        self.assertIn("first provider must be selected", report.blockers)
        self.assertIn("default model must be selected", report.blockers)
        self.assertIn("real provider calls must be approved", report.blockers)
        self.assertIn("cost limit must be set", report.blockers)
        self.assertIn("timeout policy must be set", report.blockers)
        self.assertIn("retry policy must be set", report.blockers)

    def test_invalid_api_key_env_var_blocks_readiness_without_reading_key(self) -> None:
        decisions = _ready_decisions(api_key_env_var="provider-key")

        report = assess_provider_integration_readiness(decisions)

        self.assertFalse(report.is_ready)
        self.assertIn(
            "API key environment variable must be uppercase snake case",
            report.blockers,
        )

    def test_disallowed_task_scope_blocks_readiness(self) -> None:
        decisions = _ready_decisions(allowed_tasks=(EXTRACTION_TASK, "generate_patch"))

        report = assess_provider_integration_readiness(decisions)

        self.assertFalse(report.is_ready)
        self.assertIn(
            "first real-provider task scope must be extract_units only",
            report.blockers,
        )

    def test_invalid_decision_shape_raises(self) -> None:
        with self.assertRaises(ProviderIntegrationReadinessError):
            ProviderIntegrationDecisionSet(timeout_seconds=0)

        with self.assertRaises(ProviderIntegrationReadinessError):
            assess_provider_integration_readiness("not decisions")

    def test_renders_blocked_readiness_report(self) -> None:
        report = assess_provider_integration_readiness(ProviderIntegrationDecisionSet())

        markdown = render_provider_integration_readiness_markdown(report)

        self.assertIn("# Provider Integration Readiness Report", markdown)
        self.assertIn("- readiness_status: blocked", markdown)
        self.assertIn("- first_provider: pending", markdown)
        self.assertIn("- default model must be selected", markdown)
        self.assertIn("- [ ] real provider calls approved", markdown)
        self.assertIn(
            "This report does not read API keys or environment variable values.",
            markdown,
        )
        self.assertIn(
            "Resolve blockers through explicit product-owner decisions",
            markdown,
        )

    def test_renders_ready_readiness_report_without_approving_integration(self) -> None:
        secret_value = "DO_NOT_RENDER_THIS_SECRET_VALUE"
        previous_secret = os.environ.get("DIAMONDDUST_PROVIDER_API_KEY")
        os.environ["DIAMONDDUST_PROVIDER_API_KEY"] = secret_value
        report = assess_provider_integration_readiness(_ready_decisions())

        try:
            markdown = render_provider_integration_readiness_markdown(report)
        finally:
            if previous_secret is None:
                os.environ.pop("DIAMONDDUST_PROVIDER_API_KEY", None)
            else:
                os.environ["DIAMONDDUST_PROVIDER_API_KEY"] = previous_secret

        self.assertIn("- readiness_status: ready", markdown)
        self.assertIn("- first_provider: approved-provider", markdown)
        self.assertIn("- allowed_tasks: extract_units", markdown)
        self.assertIn("- api_key_env_var: DIAMONDDUST_PROVIDER_API_KEY", markdown)
        self.assertNotIn(secret_value, markdown)
        self.assertIn("- none", markdown)
        self.assertIn("- [x] provider SDK dependency approved", markdown)
        self.assertIn(
            "- real_provider_integration_approved_by_this_report: false",
            markdown,
        )
        self.assertIn(
            "Create a separate first-provider implementation plan",
            markdown,
        )

    def test_readiness_report_renderer_rejects_invalid_input(self) -> None:
        with self.assertRaises(ProviderIntegrationReadinessError):
            render_provider_integration_readiness_markdown("not a report")

    def test_renders_blocked_escalation_request(self) -> None:
        report = assess_provider_integration_readiness(ProviderIntegrationDecisionSet())

        markdown = render_provider_integration_escalation_request_markdown(report)

        self.assertIn(
            "# Escalation Request: First Real Provider Integration",
            markdown,
        )
        self.assertIn("## Blocked Goal", markdown)
        self.assertIn("- readiness_status: blocked", markdown)
        self.assertIn("- first provider must be selected", markdown)
        self.assertIn("- approval_recorded_by_this_request: false", markdown)
        self.assertIn("## Exact User Decision Needed", markdown)
        self.assertIn("Please approve or deny this change.", markdown)

    def test_renders_escalation_request_without_secret_values(self) -> None:
        secret_value = "DO_NOT_RENDER_THIS_SECRET_VALUE"
        previous_secret = os.environ.get("DIAMONDDUST_PROVIDER_API_KEY")
        os.environ["DIAMONDDUST_PROVIDER_API_KEY"] = secret_value
        report = assess_provider_integration_readiness(_ready_decisions())

        try:
            markdown = render_provider_integration_escalation_request_markdown(report)
        finally:
            if previous_secret is None:
                os.environ.pop("DIAMONDDUST_PROVIDER_API_KEY", None)
            else:
                os.environ["DIAMONDDUST_PROVIDER_API_KEY"] = previous_secret

        self.assertIn("- readiness_status: ready", markdown)
        self.assertIn("- first_provider: approved-provider", markdown)
        self.assertIn("- api_key_env_var: DIAMONDDUST_PROVIDER_API_KEY", markdown)
        self.assertIn("- real_provider_calls_approved: true", markdown)
        self.assertIn("- allowed_tasks: extract_units", markdown)
        self.assertNotIn(secret_value, markdown)

    def test_escalation_request_renderer_rejects_invalid_input(self) -> None:
        with self.assertRaises(ProviderIntegrationReadinessError):
            render_provider_integration_escalation_request_markdown("not a report")

    def test_parses_provider_decisions_from_strict_mapping(self) -> None:
        decisions = provider_integration_decisions_from_mapping(
            {
                "first_provider": "approved-provider",
                "default_model": "approved-model",
                "provider_sdk_dependency": "approved-provider-sdk",
                "provider_sdk_dependency_approved": True,
                "api_key_env_var": "DIAMONDDUST_PROVIDER_API_KEY",
                "api_key_env_var_approved": True,
                "real_provider_calls_approved": True,
                "real_network_calls_approved": True,
                "prompt_text_external_approved": True,
                "structured_output_mechanism": "json_schema",
                "structured_output_mechanism_approved": True,
                "cost_limit": 1.0,
                "cost_limit_approved": True,
                "timeout_seconds": 30,
                "timeout_policy_approved": True,
                "max_retries": 1,
                "retry_policy_approved": True,
                "raw_output_retention": "do_not_persist",
                "raw_output_retention_approved": True,
                "fallback_behavior": "disabled",
                "fallback_behavior_approved": True,
                "allowed_tasks": [EXTRACTION_TASK],
            }
        )

        report = assess_provider_integration_readiness(decisions)

        self.assertTrue(report.is_ready)
        self.assertEqual(decisions.allowed_tasks, (EXTRACTION_TASK,))

    def test_provider_decision_mapping_rejects_unknown_fields(self) -> None:
        with self.assertRaises(ProviderIntegrationReadinessError):
            provider_integration_decisions_from_mapping({"unknown": "value"})

    def test_provider_decision_mapping_rejects_invalid_allowed_tasks_shape(self) -> None:
        with self.assertRaises(ProviderIntegrationReadinessError):
            provider_integration_decisions_from_mapping(
                {"allowed_tasks": "extract_units"}
            )

    def test_provider_decision_template_is_blocked_and_parseable(self) -> None:
        template = provider_integration_decision_template_mapping()

        decisions = provider_integration_decisions_from_mapping(template)
        report = assess_provider_integration_readiness(decisions)

        self.assertFalse(report.is_ready)
        self.assertEqual(decisions.allowed_tasks, (EXTRACTION_TASK,))
        self.assertIsNone(decisions.first_provider)
        self.assertIsNone(decisions.default_model)
        self.assertIsNone(decisions.api_key_env_var)
        self.assertFalse(decisions.real_provider_calls_approved)
        self.assertIn("first provider must be selected", report.blockers)
        self.assertEqual(
            set(template),
            set(ProviderIntegrationDecisionSet.__dataclass_fields__),
        )


def _ready_decisions(**overrides) -> ProviderIntegrationDecisionSet:
    values = {
        "first_provider": "approved-provider",
        "default_model": "approved-model",
        "provider_sdk_dependency": "approved-provider-sdk",
        "provider_sdk_dependency_approved": True,
        "api_key_env_var": "DIAMONDDUST_PROVIDER_API_KEY",
        "api_key_env_var_approved": True,
        "real_provider_calls_approved": True,
        "real_network_calls_approved": True,
        "prompt_text_external_approved": True,
        "structured_output_mechanism": "json_schema",
        "structured_output_mechanism_approved": True,
        "cost_limit": 1.0,
        "cost_limit_approved": True,
        "timeout_seconds": 30,
        "timeout_policy_approved": True,
        "max_retries": 1,
        "retry_policy_approved": True,
        "raw_output_retention": "do_not_persist",
        "raw_output_retention_approved": True,
        "fallback_behavior": "disabled",
        "fallback_behavior_approved": True,
    }
    values.update(overrides)
    return ProviderIntegrationDecisionSet(**values)


if __name__ == "__main__":
    unittest.main()
