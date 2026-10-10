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
| **DeepSeek** | `https://api.deepseek.com` | `deepseek-flash` | Cost-effective, 1M context, dual thinking modes |
| **OpenAI** | `https://api.openai.com/v1` | `gpt-6.1-sol` | Advanced reasoning, GPT-6 / GPT-5.6 / GPT-5.4 series |
| **Z.AI** | `https://api.z.ai/api/paas/v4` | `glm-5.3` | GLM models, Chinese optimization |
| **KIMI** | `https://api.moonshot.ai/v1` | `kimi-k3` | 1M context, always-on reasoning (`low`/`high`/`max`), multimodal |

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
        "default_model": "deepseek-flash",
        "models": {
            "deepseek-flash": {
                "vision": True,  # accepts image input
                "display_name": "DeepSeek V4.1 Flash",
                "max_tokens": 1000000,
                "reasoning_efforts": ["none", "high", "max"],
                "reasoning_effort_default": "high",
            },
            "deepseek-v4-pro": {
                "display_name": "DeepSeek V4 Pro",
                "max_tokens": 1000000,
                "reasoning_efforts": ["none", "high", "max"],
                "reasoning_effort_default": "high",
            }
        }
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-6.1-sol",
        # Provider-wide: OpenAI rejects temperature != 1 while reasoning
        "fixed_temperature": 1.0,
        "models": {
            "gpt-6.1-sol": {
                "vision": True,  # accepts image input
                "display_name": "GPT-6.1 Sol",
                "max_tokens": 1050000,
                "reasoning_efforts": ["low", "medium", "high", "xhigh"],  # always reasons
                "reasoning_effort_default": "medium",
                "thinking_param": {"reasoning": {"effort": "medium"}}
            },
            # ... more models
        }
    },
    "kimi": {
        # ...
        "models": {
            "kimi-k2.7-code": {
                "display_name": "KIMI K2.7 Code",
                "max_tokens": 262144,
                "thinking_param": {"thinking": {"type": "enabled"}},
                "thinking_always_on": True,   # thinking cannot be disabled
                "fixed_temperature": 1.0,
            },
            "kimi-k2.6": {
                "display_name": "KIMI K2.6",
                "max_tokens": 262144,
                "thinking_param": {"thinking": {"type": "enabled"}},
                "fixed_temperature": 1.0,                   # with thinking
                "fixed_temperature_without_thinking": 0.6,  # thinking disabled
            },
            # ... kimi-k3, kimi-k2.7-code-highspeed
        }
    },
    # ... zai configuration
}
```

**Optional config keys**:
- `reasoning_efforts` / `reasoning_effort_default` (model) — effort levels shown in the UI and the fallback used when a requested level isn't supported
- `fixed_temperature` (provider or model) — the only temperature the API accepts; a model-level value overrides the provider-level one
- `fixed_temperature_without_thinking` (model) — fixed temperature used when thinking is disabled (kimi-k2.6)
- `max_temperature` (provider) — highest temperature the API accepts (Z.AI `1.0`); defaults to `DEFAULT_MAX_TEMPERATURE` (`2.0`)
- `temperature_ignored_with_thinking` (provider) — the API silently ignores temperature while thinking (DeepSeek); the UI disables the control for thinking levels other than `none`
- `thinking_always_on` (model) — the model always thinks and the thinking toggle is shown fixed/disabled (kimi-k2.7-code, kimi-k2.7-code-highspeed)
- `vision` (model) — the model accepts image input; enables "Attach image" in the chat toolbox and sends images as `image_url` parts. Set for deepseek-flash, all OpenAI models and all KIMI models; not for deepseek-v4-pro (ignores images) or the Z.AI models (text-only). See [Image Input](../api/providers.md#image-input)

**Helpers** (`lib/shared/constants.py`):
- `get_default_reasoning_effort(provider, model)` — the model's `reasoning_effort_default` (or first effort), `None` if the model has no efforts
- `resolve_reasoning_effort(provider, model, thinking_level)` — returns `thinking_level` if supported, otherwise the model's default effort
- `get_fixed_temperature(provider, model=None, thinking=True)` — the enforced temperature, or `None` if adjustable
- `supports_images(provider, model)` — `True` if the model config declares `"vision": True`
- `get_max_temperature(provider)` — the provider's `max_temperature`, or `DEFAULT_MAX_TEMPERATURE`
- `is_temperature_ignored(provider, thinking_level)` — `True` if the API ignores temperature for this thinking level
- `is_thinking_enabled(thinking_level)` — `True` for any level other than empty/`"none"`

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
    "deepseek": ["deepseek-flash", "deepseek-v4-pro"],
    "openai": ["gpt-6.1-sol", "gpt-6-astra", "gpt-6-luna", "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna", "gpt-5.4-mini", "gpt-5.4-nano"],
    "zai": ["glm-5.3", "glm-5.2", "glm-5", "glm-4.7-flash"]
}

# Thinking parameters
THINKING_PARAMS_BY_MODEL = {
    "deepseek-flash": "reasoning_effort",
    "deepseek-v4-pro": "reasoning_effort",
    "gpt-6.1-sol": "reasoning_effort",
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

**Values** (per model, from `reasoning_efforts`):
- `gpt-6.1-sol`, `gpt-6-astra` — always reason: `"low"`, `"medium"`, `"high"`, `"xhigh"` (default `"medium"`, no `"none"`)
- `gpt-6-luna`, GPT-5.6 and GPT-5.4 models — `"none"`, `"low"`, `"medium"`, `"high"`, `"xhigh"` (default `"none"`)

`"max"` exists only in OpenAI's Responses API, not in Chat Completions (which the app uses), so it is not offered.

**Always explicit**: `reasoning_effort` is sent on every OpenAI request, **including `"none"`**. If the parameter is omitted the API applies its own default, and GPT-6 models would reason even with "none" selected. A level the model doesn't support (e.g. `"none"` for `gpt-6.1-sol`) falls back to the model's `reasoning_effort_default` via `resolve_reasoning_effort()`.

**Temperature**: OpenAI rejects `temperature != 1` whenever reasoning is active, so the provider config sets `fixed_temperature: 1.0` and every OpenAI request is sent with `temperature=1.0`.

**Implementation**:
```python
def _prepare_thinking_param(self, model, thinking_level):
    if self.provider == "openai":
        effort = resolve_reasoning_effort(self.provider, model, thinking_level)
        return {}, {"reasoning_effort": effort}
```

**Example**:
```python
client.chat.completions.create(
    model="gpt-6.1-sol",
    reasoning_effort="medium",  # Direct parameter, always sent
    temperature=1.0,            # Fixed for OpenAI
    messages=messages
)
```

#### DeepSeek V4: `reasoning_effort` + `thinking.type`

**Two knobs**:
- `reasoning_effort` (top-level): `"high"` or `"max"` — controls how much the model reasons. Thinking is enabled on the DeepSeek API by default, so setting `reasoning_effort` is sufficient to keep it on.
- `thinking.type` (in `extra_body`): used only to **disable** thinking (`{"type": "disabled"}`) since the API defaults to enabled.

**Effort levels exposed in UI**: `none`, `high`, `max`

**Model Behavior**: Both `deepseek-flash` and `deepseek-v4-pro` support both modes — thinking is no longer determined by model choice (as it was for the deprecated `deepseek-chat`/`deepseek-reasoner` pair).

**Implementation**:
```python
def _prepare_thinking_param(provider, model, thinking_level):
    if provider == "deepseek":
        if thinking_level in ("high", "max"):
            return {}, {"reasoning_effort": thinking_level}
        # "none" must explicitly disable, since DeepSeek defaults to enabled
        return {"thinking": {"type": "disabled"}}, {}
```

**Examples**:
```python
# Thinking off
client.chat.completions.create(
    model="deepseek-flash",
    messages=messages,
    extra_body={"thinking": {"type": "disabled"}}
)

# Thinking on, high effort (default)
client.chat.completions.create(
    model="deepseek-flash",
    messages=messages,
    reasoning_effort="high",
)
```

#### Z.AI: `thinking.type` via extra_body (+ `reasoning_effort` for GLM-5.3 / GLM-5.2)

**Parameter**: `thinking.type` in `extra_body` dictionary; `reasoning_effort` as a direct parameter for GLM-5.3 and GLM-5.2

**Values**: `thinking.type` = `"enabled"` / `"disabled"`; `reasoning_effort` = `"low"` / `"high"` / `"max"` (GLM-5.3) or `"high"` / `"max"` (GLM-5.2)

**Model behavior**:
- `glm-5.3` (default) — 1M context, 128K output; thinking is **always enabled**; the user adjusts `reasoning_effort` (`low`/`high`/`max`, default `max`).
- `glm-5.2` — thinking is **always enabled**; the user only adjusts `reasoning_effort` (`high`/`max`). The Z.AI API collapses `low`/`medium` → `high` and `xhigh` → `max`, so only the two distinct levels are exposed.
- `glm-5`, `glm-4.7-flash` — enabled/disabled toggle only (no `reasoning_effort`).

Detection is by whether the model config defines `reasoning_efforts` (GLM-5.3 and GLM-5.2 do; the others don't).

**Implementation**:
```python
def _prepare_thinking_param(provider, model, thinking_level):
    if provider == "zai":
        model_config = get_model_config(provider, model) or {}
        if "reasoning_efforts" in model_config:  # glm-5.3 / glm-5.2
            effort = resolve_reasoning_effort(provider, model, thinking_level)
            return {"thinking": {"type": "enabled"}}, {"reasoning_effort": effort}
        # glm-5 / glm-4.7-flash: enabled/disabled toggle
        if not thinking_level or thinking_level == "none":
            return {"thinking": {"type": "disabled"}}, {}
        return {"thinking": {"type": "enabled"}}, {}
```

#### KIMI: `reasoning_effort` (K3) vs `thinking.type` (K2.x)

**Challenge**: The K3 and K2.x generations use *different* reasoning parameters.

**Model behavior**:
- `kimi-k3` — reasons via a **top-level** `reasoning_effort` field: `"low"`, `"high"` or `"max"` (default `"max"`; the model always reasons). It only accepts a fixed `temperature = 1.0`. Do **not** send the K2.x `thinking` parameter.
- `kimi-k2.7-code`, `kimi-k2.7-code-highspeed` — coding-focused (HighSpeed = faster serving), 262,144-token context. They **always think**: thinking cannot be disabled (the API rejects `thinking.type=disabled`) and `reasoning_effort` is ignored. Config flag `thinking_always_on: True`; the UI shows a fixed, disabled "Enabled" thinking selector. Fixed `temperature = 1.0`.
- `kimi-k2.6` — enabled/disabled toggle via `thinking.type` in `extra_body`. The API thinks by default, so "none" sends `thinking.type=disabled` **explicitly** (omitting it would leave thinking on). Temperature is fixed per mode: `1.0` with thinking, `0.6` without (`fixed_temperature` / `fixed_temperature_without_thinking`).

Detection is by whether the model config defines `reasoning_efforts` (kimi-k3 does; the K2.x models don't) — the same pattern used for Z.AI's GLM-5.3/5.2.

**Implementation**:
```python
def _prepare_thinking_param(self, model, thinking_level):
    if self.provider == "kimi":
        model_config = get_model_config(self.provider, model) or {}
        if "reasoning_efforts" in model_config:  # kimi-k3
            effort = resolve_reasoning_effort(self.provider, model, thinking_level)
            return {}, {"reasoning_effort": effort}
        # kimi-k2.x: enabled/disabled toggle
        if not thinking_level or thinking_level == "none":
            if model_config.get("thinking_always_on"):  # kimi-k2.7-code*
                return {}, {}
            return {"thinking": {"type": "disabled"}}, {}  # kimi-k2.6
        return {"thinking": {"type": "enabled"}}, {}
```

> **Fixed temperature**: providers or models may declare `fixed_temperature`
> (OpenAI provider-wide `1.0`; kimi-k3, kimi-k2.7-code* and kimi-k2.6 `1.0`), and
> models may add `fixed_temperature_without_thinking` (kimi-k2.6 `0.6`).
> `LLMClient._effective_temperature(model, temperature, thinking_level)` resolves
> the value via `get_fixed_temperature()` and overrides the user-selected
> temperature on every call path, so the UI disables the temperature control for
> such models. Adjustable temperatures are clamped to the provider's
> `max_temperature` (Z.AI `1.0`), and `render_temperature_input()` uses the same
> bound for its control. DeepSeek (`temperature_ignored_with_thinking`) still
> sends the value, but the UI disables the control while thinking is on because
> the API ignores it.

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

    # DeepSeek first: API defaults to thinking-enabled, so "none" must explicitly disable.
    if provider == "deepseek":
        if thinking_level in ("high", "max"):
            direct_params["reasoning_effort"] = thinking_level
        else:
            extra_body["thinking"] = {"type": "disabled"}
        return extra_body, direct_params

    # Z.AI / KIMI: per-model handling (reasoning_effort vs. thinking.type
    # toggle) — see the Z.AI and KIMI sections above.
    if provider in ("zai", "kimi"):
        ...

    # OpenAI: reasoning_effort always sent explicitly (including "none");
    # unsupported levels fall back to the model's default effort.
    if provider == "openai":
        direct_params["reasoning_effort"] = resolve_reasoning_effort(
            provider, model, thinking_level
        )

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
- Model: `deepseek-flash`
- Reasoning: Disabled

**Complex Problem Solving**:
- Provider: OpenAI
- Model: `gpt-6-astra` or `gpt-6.1-sol`
- Reasoning: Medium/High/Xhigh

**Chinese Language**:
- Provider: Z.AI
- Model: `glm-5.3`
- Reasoning: Low/High/Max

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
