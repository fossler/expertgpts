"""Tests for provider-specific reasoning and temperature parameters."""

import pytest

from lib.llm.llm_client import LLMClient
from lib.shared.constants import (
    LLM_PROVIDERS,
    get_fixed_temperature,
    resolve_reasoning_effort,
)


def _client(provider: str) -> LLMClient:
    """Create a client with a dummy key (no network calls are made)."""
    return LLMClient(provider, "test-key")


@pytest.mark.unit
class TestModelCatalog:
    """Consistency checks for LLM_PROVIDERS."""

    @pytest.mark.parametrize("provider", list(LLM_PROVIDERS))
    def test_default_model_exists(self, provider):
        config = LLM_PROVIDERS[provider]
        assert config["default_model"] in config["models"]

    @pytest.mark.parametrize(
        "provider,model",
        [(p, m) for p, c in LLM_PROVIDERS.items() for m in c["models"]],
    )
    def test_reasoning_default_is_supported(self, provider, model):
        model_config = LLM_PROVIDERS[provider]["models"][model]
        if "reasoning_efforts" in model_config:
            assert (
                model_config["reasoning_effort_default"]
                in model_config["reasoning_efforts"]
            )


@pytest.mark.unit
class TestOpenAIParams:
    """OpenAI must always send reasoning_effort and pin temperature to 1."""

    @pytest.mark.parametrize("model", ["gpt-6-luna", "gpt-5.6-terra"])
    def test_none_is_sent_explicitly(self, model):
        # Omitting reasoning_effort lets the API apply its own default, which
        # makes GPT-6 reason even though "none" was selected.
        extra, direct = _client("openai")._prepare_thinking_param(model, "none")
        assert extra == {}
        assert direct == {"reasoning_effort": "none"}

    @pytest.mark.parametrize("level", ["none", None, "max"])
    def test_unsupported_level_falls_back_to_default(self, level):
        # gpt-6.1-sol always reasons and has no "max" in Chat Completions
        _, direct = _client("openai")._prepare_thinking_param("gpt-6.1-sol", level)
        assert direct == {"reasoning_effort": "medium"}

    def test_supported_level_is_passed_through(self):
        _, direct = _client("openai")._prepare_thinking_param("gpt-6-astra", "xhigh")
        assert direct == {"reasoning_effort": "xhigh"}

    @pytest.mark.parametrize("model", ["gpt-6.1-sol", "gpt-6-luna", "gpt-5.4-mini"])
    def test_temperature_is_pinned(self, model):
        assert _client("openai")._effective_temperature(model, 0.2) == 1.0


@pytest.mark.unit
class TestOtherProviders:
    """DeepSeek, Z.AI and KIMI parameter mapping."""

    def test_deepseek_none_disables_thinking(self):
        extra, direct = _client("deepseek")._prepare_thinking_param(
            "deepseek-flash", "none"
        )
        assert extra == {"thinking": {"type": "disabled"}}
        assert direct == {}

    def test_deepseek_keeps_user_temperature(self):
        assert _client("deepseek")._effective_temperature("deepseek-flash", 0.2) == 0.2

    @pytest.mark.parametrize("level,expected", [("low", "low"), ("none", "max")])
    def test_glm_5_3_effort(self, level, expected):
        extra, direct = _client("zai")._prepare_thinking_param("glm-5.3", level)
        assert extra == {"thinking": {"type": "enabled"}}
        assert direct == {"reasoning_effort": expected}

    @pytest.mark.parametrize("level", ["low", "high", "max"])
    def test_kimi_k3_efforts(self, level):
        _, direct = _client("kimi")._prepare_thinking_param("kimi-k3", level)
        assert direct == {"reasoning_effort": level}

    @pytest.mark.parametrize("model", ["kimi-k2.7-code", "kimi-k2.7-code-highspeed"])
    def test_kimi_k2_7_code_never_disables_thinking(self, model):
        # The API rejects thinking.type=disabled for K2.7 Code
        extra, direct = _client("kimi")._prepare_thinking_param(model, "none")
        assert extra == {} and direct == {}
        assert get_fixed_temperature("kimi", model) == 1.0

    @pytest.mark.parametrize(
        "level,extra,temperature",
        [
            ("none", {"thinking": {"type": "disabled"}}, 0.6),
            ("medium", {"thinking": {"type": "enabled"}}, 1.0),
        ],
    )
    def test_kimi_k2_6_toggle_and_temperature(self, level, extra, temperature):
        # The API thinks by default, so "none" must disable thinking explicitly;
        # the only accepted temperature depends on the mode.
        client = _client("kimi")
        assert client._prepare_thinking_param("kimi-k2.6", level) == (extra, {})
        assert client._effective_temperature("kimi-k2.6", 0.2, level) == temperature


@pytest.mark.unit
class TestHelpers:
    def test_resolve_reasoning_effort_without_efforts(self):
        assert resolve_reasoning_effort("kimi", "kimi-k2.6", "high") is None

    def test_fixed_temperature_provider_wide(self):
        assert get_fixed_temperature("openai") == 1.0
        assert get_fixed_temperature("deepseek") is None
