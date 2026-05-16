import unittest

from diamonddust.ai import (
    APIKeyEnvVarPolicy,
    CostPolicy,
    EXTRACTION_TASK,
    FIRST_PROVIDER_UNDECIDED,
    InvalidOutputBehavior,
    LoggingPolicy,
    ModelFallbackMode,
    ModelPolicy,
    ModelPolicyError,
    ProviderErrorType,
    ProviderModelSettings,
    ProviderRequest,
    RawProviderOutputRetentionMode,
    RawProviderOutputRetentionPolicy,
    TimeoutPolicy,
    default_model_policy,
    validate_provider_request_policy,
)


class ModelPolicyTests(unittest.TestCase):
    def test_default_model_policy_is_conservative(self) -> None:
        policy = default_model_policy()

        self.assertEqual(policy.first_provider, FIRST_PROVIDER_UNDECIDED)
        self.assertTrue(policy.real_provider_calls_require_user_approval)
        self.assertFalse(policy.real_provider_calls_approved)
        self.assertTrue(policy.provider_sdk_requires_escalation)
        self.assertFalse(policy.api_key_env_var_policy.read_allowed)
        self.assertEqual(policy.allowed_tasks, (EXTRACTION_TASK,))
        self.assertIn("suggest_relations", policy.disallowed_tasks)
        self.assertEqual(
            policy.invalid_output_behavior,
            InvalidOutputBehavior.FAIL_CLOSED,
        )
        self.assertIn(ProviderErrorType.TIMEOUT, policy.retry_policy.retryable_errors)
        self.assertEqual(policy.metrics_policy.latency_unit, "milliseconds")
        self.assertEqual(
            policy.raw_provider_output_retention_policy.mode,
            RawProviderOutputRetentionMode.DO_NOT_PERSIST,
        )
        self.assertFalse(policy.raw_provider_output_retention_policy.persist_raw_output)
        self.assertEqual(policy.model_fallback_policy.mode, ModelFallbackMode.DISABLED)
        self.assertFalse(policy.logging_policy.log_raw_provider_output)
        self.assertFalse(policy.logging_policy.log_api_key)

    def test_default_policy_allows_fixture_safe_extract_units_request(self) -> None:
        validate_provider_request_policy(_request())

    def test_default_policy_rejects_unapproved_real_provider_call(self) -> None:
        with self.assertRaises(ModelPolicyError):
            validate_provider_request_policy(
                _request(
                    settings=ProviderModelSettings(
                        provider="future-provider",
                        model="future-model",
                        prompt_version="extract_units.v1",
                        schema_version="0.1.0",
                        real_provider_calls_enabled=True,
                    )
                )
            )

    def test_policy_can_represent_explicit_real_call_approval(self) -> None:
        policy = ModelPolicy(real_provider_calls_approved=True)

        validate_provider_request_policy(
            _request(
                settings=ProviderModelSettings(
                    provider="future-provider",
                    model="future-model",
                    prompt_version="extract_units.v1",
                    schema_version="0.1.0",
                    real_provider_calls_enabled=True,
                )
            ),
            policy,
        )

    def test_policy_rejects_disallowed_tasks(self) -> None:
        with self.assertRaises(ModelPolicyError):
            default_model_policy().ensure_task_allowed("suggest_relations")

        with self.assertRaises(ModelPolicyError):
            ModelPolicy(allowed_tasks=("suggest_relations",))

    def test_policy_rejects_weakened_approval_requirements(self) -> None:
        with self.assertRaises(ModelPolicyError):
            ModelPolicy(real_provider_calls_require_user_approval=False)

        with self.assertRaises(ModelPolicyError):
            ModelPolicy(provider_sdk_requires_escalation=False)

        with self.assertRaises(ModelPolicyError):
            CostPolicy(real_costs_require_user_approval=False)

    def test_policy_rejects_raw_output_or_secret_logging(self) -> None:
        with self.assertRaises(ModelPolicyError):
            RawProviderOutputRetentionPolicy(persist_raw_output=True)

        with self.assertRaises(ModelPolicyError):
            LoggingPolicy(log_raw_provider_output=True)

        with self.assertRaises(ModelPolicyError):
            LoggingPolicy(log_api_key=True)

    def test_api_key_env_var_policy_is_shape_only_by_default(self) -> None:
        policy = APIKeyEnvVarPolicy()

        self.assertIsNone(policy.env_var_name)
        self.assertFalse(policy.read_allowed)
        self.assertTrue(policy.required_for_real_provider_calls)

        with self.assertRaises(ModelPolicyError):
            APIKeyEnvVarPolicy(read_allowed=True)

        with self.assertRaises(ModelPolicyError):
            APIKeyEnvVarPolicy(env_var_name="openai_api_key")

        APIKeyEnvVarPolicy(env_var_name="DIAMONDDUST_PROVIDER_API_KEY")

    def test_timeout_policy_can_cap_request_timeout(self) -> None:
        policy = ModelPolicy(
            timeout_policy=TimeoutPolicy(
                default_timeout_seconds=10,
                maximum_timeout_seconds=30,
            )
        )

        validate_provider_request_policy(
            _request(settings=_settings(timeout_seconds=30)),
            policy,
        )
        with self.assertRaises(ModelPolicyError):
            validate_provider_request_policy(
                _request(settings=_settings(timeout_seconds=31)),
                policy,
            )


def _settings(*, timeout_seconds: int | None = None) -> ProviderModelSettings:
    return ProviderModelSettings(
        provider="fake-provider",
        model="fake-structured-model",
        prompt_version="extract_units.v1",
        schema_version="0.1.0",
        timeout_seconds=timeout_seconds,
    )


def _request(
    *,
    settings: ProviderModelSettings | None = None,
) -> ProviderRequest:
    return ProviderRequest(
        run_id="run_model_policy_ab12cd",
        task=EXTRACTION_TASK,
        input_hash="sha256:input",
        input_payload={"source_input_id": "raw_essay_model_policy_ab12cd"},
        settings=settings or _settings(),
    )


if __name__ == "__main__":
    unittest.main()
