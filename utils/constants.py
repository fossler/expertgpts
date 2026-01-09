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

# Performance Optimization: Pre-computed lookup tables for O(1) access
# These eliminate nested dictionary lookups and provide direct access paths

# Nested model lookup: MODEL_LOOKUP[provider][model] -> model_config
MODEL_LOOKUP = {
    provider: {model_id: config for model_id, config in models.items()}
    for provider, models in {
        provider: provider_config["models"]
        for provider, provider_config in LLM_PROVIDERS.items()
    }.items()
}

# Provider display names: PROVIDER_NAMES[provider] -> display_name
PROVIDER_NAMES = {provider: config["name"] for provider, config in LLM_PROVIDERS.items()}

# Default models: DEFAULT_MODELS[provider] -> default_model_id
DEFAULT_MODELS = {provider: config["default_model"] for provider, config in LLM_PROVIDERS.items()}

# Base URLs: BASE_URLS[provider] -> base_url
BASE_URLS = {provider: config["base_url"] for provider, config in LLM_PROVIDERS.items()}

# API key environment variables: API_KEY_ENVS[provider] -> env_var_name
API_KEY_ENVS = {provider: config["api_key_env"] for provider, config in LLM_PROVIDERS.items()}

# Max tokens: MAX_TOKENS[(provider, model)] -> max_tokens
MAX_TOKENS = {
    (provider, model): config["max_tokens"]
    for provider, provider_config in LLM_PROVIDERS.items()
    for model, config in provider_config["models"].items()
}

# Thinking parameters: THINKING_PARAMS[(provider, model)] -> thinking_param
THINKING_PARAMS = {
    (provider, model): config["thinking_param"]
    for provider, provider_config in LLM_PROVIDERS.items()
    for model, config in provider_config["models"].items()
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
    # Optimized: Use pre-computed lookup table
    if provider not in MODEL_LOOKUP:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(MODEL_LOOKUP.keys())}")
    if model not in MODEL_LOOKUP[provider]:
        available = list(MODEL_LOOKUP[provider].keys())
        raise ValueError(f"Unknown model: {model} for provider {provider}. Available: {available}")
    return MODEL_LOOKUP[provider][model]


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
    # Optimized: Direct tuple key lookup
    key = (provider, model)
    if key not in MAX_TOKENS:
        raise ValueError(f"Unknown provider/model combination: {provider}/{model}")
    return MAX_TOKENS[key]


def get_provider_display_name(provider: str) -> str:
    """Get display name for a provider.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")

    Returns:
        str: Display name (e.g., "DeepSeek", "OpenAI", "Z.AI")

    Raises:
        ValueError: If provider is not found
    """
    # Optimized: Direct dict lookup
    if provider not in PROVIDER_NAMES:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDER_NAMES.keys())}")
    return PROVIDER_NAMES[provider]


def get_model_display_name(provider: str, model: str) -> str:
    """Get display name for a model.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")
        model: Model ID (e.g., "deepseek-chat", "gpt-5", "glm-4.7")

    Returns:
        str: Display name (e.g., "DeepSeek Chat", "GPT-5", "GLM-4.7")

    Raises:
        ValueError: If provider or model is not found
    """
    # Optimized: Use pre-computed lookup
    config = get_model_config(provider, model)
    return config["display_name"]


def get_provider_base_url(provider: str) -> str:
    """Get base URL for a provider.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")

    Returns:
        str: Base URL for the provider's API

    Raises:
        ValueError: If provider is not found
    """
    # Optimized: Direct dict lookup
    if provider not in BASE_URLS:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(BASE_URLS.keys())}")
    return BASE_URLS[provider]


def get_provider_api_key_env(provider: str) -> str:
    """Get environment variable name for a provider's API key.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")

    Returns:
        str: Environment variable name (e.g., "DEEPSEEK_API_KEY")

    Raises:
        ValueError: If provider is not found
    """
    # Optimized: Direct dict lookup
    if provider not in API_KEY_ENVS:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(API_KEY_ENVS.keys())}")
    return API_KEY_ENVS[provider]


def get_default_model_for_provider(provider: str) -> str:
    """Get default model for a provider.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")

    Returns:
        str: Default model ID for the provider

    Raises:
        ValueError: If provider is not found
    """
    # Optimized: Direct dict lookup
    if provider not in DEFAULT_MODELS:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(DEFAULT_MODELS.keys())}")
    return DEFAULT_MODELS[provider]
