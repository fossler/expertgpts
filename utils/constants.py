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
EXPERT_BEHAVIOR_DOCS = """### Why is the Expert Behavior field important?

The **system prompt** is the heart of your expert. It defines everything about how your expert will behave:
- **Tone and personality**: Friendly, professional, humorous, serious?
- **Expertise level**: Beginner-friendly explanations vs. technical deep-dives?
- **Communication style**: Concise answers vs. detailed explanations with examples?
- **Domain focus**: Specific areas of expertise to focus on
- **Constraints**: What the expert should NOT do (e.g., "Don't provide legal advice")

#### Examples

**Beginner-Friendly Expert:**
```
You are a Python Expert who specializes in teaching programming to beginners.

Your communication style:
- Use simple, clear language
- Provide code examples with detailed comments
- Explain concepts step-by-step
- Avoid jargon unless necessary, and explain it when used
- Encourage questions and learning
```

**Technical Expert:**
```
You are a Python Expert specializing in advanced Python programming and software architecture.

Your expertise includes:
- Design patterns and best practices
- Performance optimization
- Testing strategies (pytest, unittest)
- Code review and refactoring
- Enterprise Python applications

Provide concise, technical answers with code examples.
```

**Creative Writing Assistant:**
```
You are a creative writing expert who helps authors improve their craft.

Your approach:
- Provide constructive, specific feedback
- Suggest creative alternatives and improvements
- Explain storytelling techniques and narrative devices
- Encourage experimentation with different styles
- Balance critique with encouragement
```

#### Tips for Great Results
1. **Be specific** about the expert's role and expertise
2. **Define the communication style** clearly (tone, detail level)
3. **Set expectations** for what the expert should focus on
4. **Include constraints** if needed (what NOT to do)
5. **Keep it concise** but comprehensive enough to guide behavior

Remember: The more specific and clear your system prompt, the better your expert will perform!
"""


EXPERT_BEHAVIOR_DOCS_EDIT = """### Why is this important?

The **system prompt** defines your expert's behavior, expertise, and communication style. Editing it allows you to:
- **Refine behavior**: Improve how your expert responds based on experience
- **Add expertise**: Expand the domain knowledge or specialize further
- **Adjust tone**: Make responses more formal, casual, technical, or friendly
- **Set boundaries**: Define what the expert should NOT do

#### Quick Guidelines

✅ **Good edits:**
- Add new areas of expertise
- Refine communication style
- Add constraints or guidelines
- Clarify the expert's role

❌ **Avoid:**
- Making it too vague or generic
- Removing key role definitions
- Making it overly long (experts should stay focused)

#### Example Edit

**Original:**
```
You are a Python Expert who helps with Python programming questions.
```

**Improved:**
```
You are a Python Expert specializing in data science and machine learning.

Your expertise includes:
- Data analysis with pandas and numpy
- Machine learning with scikit-learn
- Data visualization with matplotlib and seaborn
- Jupyter notebooks and best practices

Provide clear explanations with code examples, and suggest best practices
for data science projects.
```

**Pro tip**: Test your expert after editing to ensure it behaves as expected!
"""


def get_expert_behavior_docs():
    """Get translated expert behavior documentation for add chat dialog.

    Returns:
        str: Markdown-formatted documentation about expert behavior field
    """
    from utils.i18n import i18n
    return i18n.t("dialogs.add_chat.expert_behavior_docs")


def get_expert_behavior_docs_edit():
    """Get translated expert behavior documentation for edit expert dialog.

    Returns:
        str: Markdown-formatted documentation about expert behavior field (shorter version)
    """
    from utils.i18n import i18n
    return i18n.t("dialogs.edit_expert.expert_behavior_docs_edit")


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
