import unittest

from diamonddust.ai import EXTRACTION_TASK
from diamonddust.application import (
    ProviderIntegrationDecisionSet,
    ProviderIntegrationReadinessError,
    ProviderIntegrationReadinessStatus,
    assess_provider_integration_readiness,
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
