# Multi-Provider LLM Architecture

This guide explains ExpertGPTs' multi-provider LLM integration, including provider support, parameter handling, and connection pooling.

## Overview

ExpertGPTs supports **multiple LLM providers** through OpenAI-compatible APIs, providing:
- Provider flexibility (choose per expert)
- Cost optimization (use cost-effective providers)
- Feature diversity (different provider capabilities)
- Unified client interface (single API)

## Supported Providers

| Provider | Base URL | Default Model | Characteristics |
|----------|----------|---------------|-----------------|
| **DeepSeek** | `https://api.deepseek.com` | `deepseek-chat` | Cost-effective, high quality |
| **OpenAI** | `https://api.openai.com/v1` | `o3-mini` | Advanced reasoning, o3-series |
| **Z.AI** | `https://api.z.ai/v1` | `glm-4.7` | GLM models, Chinese optimization |

## Architecture

### Unified Client Interface

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│              (Expert pages, Settings, etc.)                 │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                  LLMClient Interface                        │
│           (lib/llm/llm_client.py - Unified API)              │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                 Connection Pool                             │
│          (lib/llm/client_pool.py - Caching)                  │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│              OpenAI Python Client                          │
│         (openai library with custom base_url)              │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                  Provider APIs                              │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐ │
│  │  DeepSeek    │  │    OpenAI     │  │      Z.AI        │ │
│  │     API      │  │      API      │  │       API        │ │
│  └──────────────┘  └───────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## LLM Client Implementation

### Core Class: `LLMClient`

**Location**: `lib/llm/llm_client.py`

**Purpose**: Unified interface for all LLM providers

**Key Method**: `generate_response(messages, provider, model, temperature, thinking_level)`

### Provider Configuration

**Location**: `lib/shared/constants.py`

**Structure**:
```python
LLM_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "models": {
            "deepseek-chat": {
                "display_name": "DeepSeek Chat",
                "max_tokens": 4096,
                "thinking_param": None
            },
            "deepseek-reasoner": {
                "display_name": "DeepSeek Reasoner",
                "max_tokens": 8192,
                "thinking_param": "enabled"
            }
        }
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "default_model": "o3-mini",
        "models": {
            "o3-mini": {
                "display_name": "o3-mini",
                "max_tokens": 65536,
                "thinking_param": "reasoning_effort"
            },
            # ... more models
        }
    },
    # ... zai configuration
}
```

### O(1) Lookup Tables

**Pre-computed for performance**:

```python
# Provider names to IDs
PROVIDER_NAME_TO_ID = {
    "DeepSeek": "deepseek",
    "OpenAI": "openai",
    "Z.AI": "zai"
}

# Model availability
MODELS_BY_PROVIDER = {
    "deepseek": ["deepseek-chat", "deepseek-reasoner"],
    "openai": ["o3-mini", "gpt-4o", "gpt-4o-mini"],
    "zai": ["glm-4.7", "glm-4.7-thinking"]
}

# Thinking parameters
THINKING_PARAMS_BY_MODEL = {
    "deepseek-reasoner": "enabled",
    "o3-mini": "reasoning_effort",
    # ...
}
```

**Benefit**: Eliminates nested dictionary access overhead

## Provider-Specific Parameters

### Thinking Parameters

**Challenge**: Each provider handles "thinking" (reasoning) differently

**Solution**: `_prepare_thinking_param()` method handles provider differences

#### OpenAI: `reasoning_effort`

**Parameter**: Direct parameter in API call

**Values**: `"low"`, `"medium"`, `"high"`

**Implementation**:
```python
def _prepare_thinking_param(provider, model, thinking_level):
    if provider == "openai" and thinking_level != "none":
        return {}, {"reasoning_effort": thinking_level}
```

**Example**:
```python
client.chat.completions.create(
    model="o3-mini",
    reasoning_effort="medium",  # Direct parameter
    messages=messages
)
```

#### DeepSeek: `thinking.type`

**Parameter**: In `extra_body` dictionary

**Values**: `"enabled"`, `"disabled"` (model-dependent)

**Model Behavior**:
- `deepseek-chat`: No thinking parameter
- `deepseek-reasoner`: `thinking.type` = "enabled"

**Implementation**:
```python
def _prepare_thinking_param(provider, model, thinking_level):
    if provider == "deepseek" and model == "deepseek-reasoner":
        extra_body = {"thinking": {"type": "enabled"}}
        return extra_body, {}
```

**Example**:
```python
client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages,
    extra_body={"thinking": {"type": "enabled"}}
)
```

#### Z.AI: `thinking.type` via extra_body

**Parameter**: In `extra_body` dictionary

**Values**: `"enabled"`, `"disabled"`

**Similar to DeepSeek** but different model availability

**Implementation**:
```python
def _prepare_thinking_param(provider, model, thinking_level):
    if provider == "zai" and "thinking" in model:
        extra_body = {"thinking": {"type": "enabled"}}
        return extra_body, {}
```

### Unified Implementation

**Location**: `lib/llm/llm_client.py`

```python
def _prepare_thinking_param(self, provider: str, model: str, thinking_level: str):
    """
    Prepare provider-specific thinking parameters.

    Returns:
        tuple: (extra_body_dict, direct_params_dict)
    """
    extra_body = {}
    direct_params = {}

    if thinking_level == "none":
        return extra_body, direct_params

    # OpenAI: reasoning_effort as direct parameter
    if provider == "openai":
        direct_params["reasoning_effort"] = thinking_level

    # DeepSeek: thinking.type in extra_body
    elif provider == "deepseek" and model == "deepseek-reasoner":
        extra_body["thinking"] = {"type": "enabled"}

    # Z.AI: thinking.type in extra_body
    elif provider == "zai" and "thinking" in model:
        extra_body["thinking"] = {"type": "enabled"}

    return extra_body, direct_params
```

## Connection Pooling

### Client Pool Implementation

**Location**: `lib/llm/client_pool.py`

**Purpose**: Cache and reuse LLM client instances

**Key Function**: `get_cached_client(provider, api_key)`

**Cache Key**: `{provider}_{api_key_hash}`

**Benefits**:
- ~50% reduction in client creation overhead
- Faster API calls (no re-authentication)
- Reduced resource usage

### Implementation

```python
from functools import lru_cache
from openai import OpenAI

@lru_cache(maxsize=32)
def get_cached_client(provider: str, api_key: str) -> OpenAI:
    """
    Get cached LLM client instance.

    Args:
        provider: Provider name (deepseek, openai, zai)
        api_key: API key for the provider

    Returns:
        Cached OpenAI client instance
    """
    base_url = get_provider_config(provider)["base_url"]
    return OpenAI(api_key=api_key, base_url=base_url)
```

**Cache Invalidation**:
- Automatic when API key changes
- Manual: Restart application

## Using Different Providers

### Per-Expert Provider Selection

**UI Controls** (in expert page sidebar):
```python
provider = st.selectbox(
    "Provider",
    ["deepseek", "openai", "zai"],
    index=["deepseek", "openai", "zai"].index(
        st.session_state[f"provider_{EXPERT_ID}"]
    )
)
st.session_state[f"provider_{EXPERT_ID}"] = provider
```

### Model Selection

**Dynamic model list based on provider**:
```python
provider = st.session_state[f"provider_{EXPERT_ID}"]
available_models = get_models_for_provider(provider)

model = st.selectbox(
    "Model",
    available_models,
    index=available_models.index(
        st.session_state[f"model_{EXPERT_ID}"]
    )
)
st.session_state[f"model_{EXPERT_ID}"] = model
```

### Generating Responses

**Unified interface regardless of provider**:
```python
from utils.llm_client import LLMClient
from utils.client_pool import get_cached_client
from utils.secrets_manager import SecretsManager

# Get API key for provider
secrets_manager = SecretsManager()
api_key = secrets_manager.get_api_key(provider)

# Get cached client
client = get_cached_client(provider, api_key)

# Generate response
llm_client = LLMClient(client)
response = llm_client.generate_response(
    messages=messages,
    provider=provider,
    model=model,
    temperature=temperature,
    thinking_level=thinking_level
)
```

## Adding a New Provider

### Step 1: Add Provider Configuration

**File**: `lib/shared/constants.py`

```python
LLM_PROVIDERS = {
    # ... existing providers ...

    "newprovider": {
        "name": "New Provider",
        "base_url": "https://api.newprovider.com/v1",
        "default_model": "new-model",
        "models": {
            "new-model": {
                "display_name": "New Model",
                "max_tokens": 4096,
                "thinking_param": None  # or specific parameter
            }
        }
    }
}
```

### Step 2: Update Thinking Parameter Handling

**File**: `lib/llm/llm_client.py`

**Add to `_prepare_thinking_param()`**:
```python
def _prepare_thinking_param(self, provider: str, model: str, thinking_level: str):
    # ... existing logic ...

    # New provider thinking parameter
    elif provider == "newprovider" and thinking_level != "none":
        # Add provider-specific thinking logic
        if model == "thinking-model":
            extra_body["thinking"] = {"enabled": True}

    return extra_body, direct_params
```

### Step 3: Add API Key UI

**File**: `pages/9998_Settings.py`

**Add tab in API Keys section**:
```python
# In Settings page, API Keys tab
with st.tabs(["DeepSeek", "OpenAI", "Z.AI", "New Provider"]):
    # ... existing tabs ...

    with tab_new_provider:
        st.subheader("New Provider API Key")
        new_provider_key = st.text_input(
            "New Provider API Key",
            type="password",
            help="Enter your New Provider API key"
        )
        if st.button("Save New Provider Key"):
            secrets_manager.save_api_key("NEW_PROVIDER", new_provider_key)
```

### Step 4: Update Secrets Template

**File**: `.streamlit/secrets.toml.example`

```toml
# ... existing keys ...

NEW_PROVIDER_API_KEY = ""
```

### Step 5: Update Lookup Tables

**File**: `lib/shared/constants.py`

```python
# Provider names to IDs
PROVIDER_NAME_TO_ID = {
    # ... existing ...
    "New Provider": "newprovider"
}

# Models by provider
MODELS_BY_PROVIDER = {
    # ... existing ...
    "newprovider": ["new-model", "thinking-model"]
}

# Thinking parameters
THINKING_PARAMS_BY_MODEL = {
    # ... existing ...
    "thinking-model": "enabled"  # if applicable
}
```

## Provider Comparison

### Cost

| Provider | Relative Cost | Best For |
|----------|--------------|----------|
| **DeepSeek** | $ | Cost-effective daily use |
| **OpenAI** | $$$ | Complex reasoning tasks |
| **Z.AI** | $$ | Chinese language optimization |

### Features

| Feature | DeepSeek | OpenAI | Z.AI |
|---------|----------|--------|------|
| **Reasoning** | Model-dependent | Yes (o3 series) | Model-dependent |
| **Thinking Levels** | 2 (on/off) | 4 (none/low/med/high) | 2 (on/off) |
| **Max Tokens** | 4K-8K | Up to 65K | Varies |
| **Language Strength** | English | Multilingual | Chinese |

### Use Case Recommendations

**Daily Development**:
- Provider: DeepSeek
- Model: `deepseek-chat`
- Reasoning: Disabled

**Complex Problem Solving**:
- Provider: OpenAI
- Model: `o3-mini`
- Reasoning: Medium/High

**Chinese Language**:
- Provider: Z.AI
- Model: `glm-4.7`
- Reasoning: Disabled

**Balanced Quality/Cost**:
- Provider: DeepSeek (most tasks)
- Provider: OpenAI (selective complex tasks)
- Model: Defaults
- Reasoning: As needed

## Performance Considerations

### Response Time

| Provider | Typical Response Time | Reasoning Impact |
|----------|---------------------|------------------|
| **DeepSeek** | Fast | +50% with reasoner |
| **OpenAI** | Medium | +100-200% with reasoning |
| **Z.AI** | Fast | +50% with thinking |

**Optimization**: Disable reasoning for faster responses

### Cost Optimization

**Strategies**:
1. Use DeepSeek for most tasks (most cost-effective)
2. Use OpenAI selectively for complex reasoning
3. Disable reasoning when not needed
4. Use appropriate temperature (lower = fewer tokens)

### Connection Pooling Benefits

**Performance Improvement**:
- First call: ~500ms (client creation + API call)
- Cached calls: ~300ms (API call only)
- **Improvement**: ~40% faster

## Best Practices

### 1. Use Connection Pooling

**Good**:
```python
from utils.client_pool import get_cached_client

client = get_cached_client(provider, api_key)
```

**Bad**:
```python
from openai import OpenAI

client = OpenAI(api_key=api_key, base_url=base_url)
# ❌ Creates new client every time
```

### 2. Handle Provider Failures

**Implementation**:
```python
try:
    response = llm_client.generate_response(...)
except APIError as e:
    st.error(f"Provider error: {e}")
    # Fallback to different provider
```

### 3. Validate Provider/Model Combinations

**Check availability**:
```python
if model not in get_models_for_provider(provider):
    st.error(f"Model {model} not available for provider {provider}")
    return
```

## Troubleshooting

### Provider API Errors

**Problem**: API call fails

**Possible Causes**:
1. Invalid API key
2. Insufficient credits/quota
3. Wrong provider/model combination
4. Network issues

**Solutions**:
1. Verify API key in Settings → API Keys
2. Check provider dashboard for credits
3. Validate provider/model combination
4. Test network connectivity

### Model Not Available

**Problem**: Model not showing in dropdown

**Possible Cause**: Model not configured for provider

**Solution**: Check `lib/shared/constants.py` for model configuration

### Connection Pool Issues

**Problem**: Client not cached properly

**Solution**: Restart application to clear cache

## Related Documentation

- **[Architecture Overview](overview.md)** - System architecture
- **[API Keys Guide](../configuration/api-keys.md)** - API key management
- **[API Providers Reference](../api/providers.md)** - Provider-specific details

---

**Back to**: [Documentation Home](../README.md) | [Architecture Overview](overview.md)
