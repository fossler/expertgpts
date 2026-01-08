"""Application-wide constants for ExpertGPTs.

This module centralizes all magic numbers, thresholds, and configuration
values used throughout the application.
"""

# LLM Provider Configuration
LLM_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "icon_path": "icons/deepseek_icon_blue.png",
        "models": {
            "deepseek-chat": {
                "display_name": "DeepSeek Chat",
                "max_tokens": 128000,
                "thinking_param": {"thinking": {"type": "disabled"}},
            },
            "deepseek-reasoner": {
                "display_name": "DeepSeek Reasoner",
                "max_tokens": 128000,
                "thinking_param": {"thinking": {"type": "enabled"}},
            }
        }
    },
    "openai": {
        "name": "OpenAI",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-5",
        "icon_path": "icons/openai_logo.png",
        "models": {
            "gpt-5": {
                "display_name": "GPT-5",
                "max_tokens": 400000,
                "thinking_param": {"reasoning": {"effort": "none"}},
            },
            "gpt-5-mini": {
                "display_name": "GPT-5 Mini",
                "max_tokens": 200000,
                "thinking_param": {"reasoning": {"effort": "none"}},
            },
            "gpt-5-nano": {
                "display_name": "GPT-5 Nano",
                "max_tokens": 400000,
                "thinking_param": {"reasoning": {"effort": "none"}},
            }
        }
    },
    "zai": {
        "name": "Z.AI",
        "api_key_env": "ZAI_API_KEY",
        "base_url": "https://api.z.ai/api/paas/v4",
        "default_model": "glm-4.7",
        "icon_path": "icons/zai_logo.svg",
        "models": {
            "glm-4.7": {
                "display_name": "GLM-4.7",
                "max_tokens": 200000,
                "thinking_param": {"thinking": {"type": "disabled"}},
            }
        }
    }
}

# Global Defaults (stored in session state)
DEFAULT_LLM_PROVIDER = "deepseek"
DEFAULT_LLM_MODEL = "deepseek-chat"
DEFAULT_THINKING_ENABLED = False

# OpenAI Reasoning Effort Levels
OPENAI_REASONING_EFFORTS = ["none", "low", "medium", "high", "xhigh"]
OPENAI_REASONING_EFFORT_DEFAULT = "none"

# Model Context Limits
DEEPSEEK_MAX_CONTEXT_TOKENS = 128000
DEEPSEEK_DEFAULT_MODEL = "deepseek-chat"
OPENAI_DEFAULT_MODEL = "gpt-5"
ZAI_DEFAULT_MODEL = "glm-4.7"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TEMPERATURE = 1.0

# Example Experts Configuration
EXAMPLE_EXPERTS_COUNT = 7  # Number of default/example experts created during setup

# Context Usage Thresholds (percentages)
CONTEXT_USAGE_SAFE_THRESHOLD = 50
CONTEXT_USAGE_WARNING_THRESHOLD = 75
CONTEXT_USAGE_ALERT_THRESHOLD = 90

# Context Usage Colors (emojis for UI display)
CONTEXT_USAGE_COLORS = {
    "safe": "🟢",
    "warning": "🟡",
    "alert": "🟠",
    "critical": "🔴"
}

# Cache TTLs (seconds)
CONFIG_CACHE_TTL = 300
TOKEN_COUNT_CACHE_TTL = 60
SYSTEM_PROMPT_CACHE_TTL = 300


# Documentation Content
EXPERT_BEHAVIOR_DOCS = """
### 🎯 Why This Field Matters Most

The behavior instructions define your expert's entire approach:
- **Tone**: Friendly, professional, casual, formal?
- **Expertise**: General overview or deep technical details?
- **Format**: Code examples, step-by-step, conversational?
- **Constraints**: What should the expert NOT do?
- **Guidelines**: Specific requirements for responses

### 📝 Example: Python Expert

```
You are a Python expert with 15 years of experience.
- Provide clean, PEP 8-compliant code with type hints and docstrings
- Explain concepts clearly with practical examples
- Warn about common pitfalls and best practices
- Suggest helpful libraries when appropriate
```

### 📝 Example: Legal Advisor

```
You are a legal assistant providing general legal information.
- Always include a disclaimer: "I am not a lawyer, this is not legal advice"
- Be thorough but cautious in recommendations
- Suggest consulting a qualified attorney for specific legal matters
- Provide general legal concepts and frameworks
```

### 📝 Example: Writing Coach

```
You are an encouraging writing coach.
- Ask questions to understand the writer's goals
- Provide specific, actionable feedback
- Balance praise with constructive criticism
- Suggest resources for improvement
- Be patient and supportive
```
"""

EXPERT_BEHAVIOR_DOCS_EDIT = """
### 🎯 Why This Field Matters Most

The behavior instructions define your expert's entire approach:
- **Tone**: Friendly, professional, casual, formal?
- **Expertise**: General overview or deep technical details?
- **Format**: Code examples, step-by-step, conversational?
- **Constraints**: What should the expert NOT do?
- **Guidelines**: Specific requirements for responses

### 💡 Tip
Leaving this empty will keep the expert's current behavior. Only edit if you want to change how they respond!
"""


# LLM Provider Helper Functions

def get_provider_config(provider: str) -> dict:
    """Get configuration for a specific LLM provider.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")

    Returns:
        dict: Provider configuration dictionary

    Raises:
        ValueError: If provider is not found
    """
    if provider not in LLM_PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(LLM_PROVIDERS.keys())}")
    return LLM_PROVIDERS[provider]


def get_model_config(provider: str, model: str) -> dict:
    """Get configuration for a specific model within a provider.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")
        model: Model ID (e.g., "deepseek-chat", "gpt-5", "glm-4.7")

    Returns:
        dict: Model configuration with display_name, max_tokens, thinking_param

    Raises:
        ValueError: If provider or model is not found
    """
    provider_config = get_provider_config(provider)
    if model not in provider_config["models"]:
        available = list(provider_config["models"].keys())
        raise ValueError(f"Unknown model: {model} for provider {provider}. Available: {available}")
    return provider_config["models"][model]


def get_max_tokens(provider: str, model: str) -> int:
    """Get maximum context tokens for a specific model.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")
        model: Model ID (e.g., "deepseek-chat", "gpt-5", "glm-4.7")

    Returns:
        int: Maximum context length for the model

    Raises:
        ValueError: If provider or model is not found
    """
    return get_model_config(provider, model)["max_tokens"]


def get_provider_display_name(provider: str) -> str:
    """Get display name for a provider.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")

    Returns:
        str: Display name (e.g., "DeepSeek", "OpenAI", "Z.AI")
    """
    return get_provider_config(provider)["name"]


def get_model_display_name(provider: str, model: str) -> str:
    """Get display name for a model.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")
        model: Model ID (e.g., "deepseek-chat", "gpt-5", "glm-4.7")

    Returns:
        str: Display name (e.g., "DeepSeek Chat", "GPT-5", "GLM-4.7")
    """
    return get_model_config(provider, model)["display_name"]


def get_provider_base_url(provider: str) -> str:
    """Get base URL for a provider.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")

    Returns:
        str: Base URL for the provider's API
    """
    return get_provider_config(provider)["base_url"]


def get_provider_api_key_env(provider: str) -> str:
    """Get environment variable name for a provider's API key.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")

    Returns:
        str: Environment variable name (e.g., "DEEPSEEK_API_KEY")
    """
    return get_provider_config(provider)["api_key_env"]


def get_default_model_for_provider(provider: str) -> str:
    """Get default model for a provider.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")

    Returns:
        str: Default model ID for the provider
    """
    return get_provider_config(provider)["default_model"]
