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
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐ │
│  │ DeepSeek  │  │  OpenAI   │  │   Z.AI    │  │   KIMI    │ │
│  │    API    │  │    API    │  │    API    │  │    API    │ │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## LLM Client Implementation

### Core Class: `LLMClient`

**Location**: `lib/llm/llm_client.py`

**Purpose**: Unified interface for all LLM providers

**Constructor**: `LLMClient(provider, api_key)` (wraps an `OpenAI` client with the provider's `base_url`)

**Key Methods**:
- `chat(messages, temperature=1.0, model=None, system_prompt=None, thinking_level=None)` - non-streaming request, returns the response text
- `chat_stream(messages, temperature=1.0, model=None, system_prompt=None, thinking_level=None)` - streaming request, yields text chunks (used by `StreamingCache`)
- `generate_system_prompt(expert_name, description, temperature=1.0, model=None)` - AI-generated system prompt for new experts
- `_prepare_thinking_param(model, thinking_level)` / `_effective_temperature(model, temperature, thinking_level)` - provider/model-specific parameters

### Provider Configuration

**Location**: `lib/shared/constants.py`

**Structure**:
```python
LLM_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-flash",
        "icon_path": "icons/deepseek_icon_blue.png",
        # Thinking mode silently ignores temperature
        "temperature_ignored_with_thinking": True,
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
                "vision": True,  # accepts image input
                "display_name": "KIMI K2.7 Code",
                "max_tokens": 262144,
                "thinking_param": {"thinking": {"type": "enabled"}},
                "thinking_always_on": True,   # thinking cannot be disabled
                "fixed_temperature": 1.0,
            },
            "kimi-k2.6": {
                "vision": True,  # accepts image input
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

Generated automatically from `LLM_PROVIDERS` in `lib/shared/constants.py`:

```python
MODEL_LOOKUP[provider][model]     # -> model config
PROVIDER_NAMES[provider]          # -> display name ("DeepSeek", "OpenAI", "Z.AI", "KIMI")
DEFAULT_MODELS[provider]          # -> default model ID
BASE_URLS[provider]               # -> base URL
API_KEY_ENVS[provider]            # -> secrets key name (e.g. "MOONSHOT_API_KEY")
MAX_TOKENS[(provider, model)]     # -> context window
```

Access them via the helpers (`get_model_config()`, `get_provider_display_name()`, `get_default_model_for_provider()`, `get_provider_base_url()`, `get_provider_api_key_env()`, `get_max_tokens()`).

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
def _prepare_thinking_param(self, model, thinking_level=None):
    if self.provider == "deepseek":
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
def _prepare_thinking_param(self, model, thinking_level=None):
    if self.provider == "zai":
        model_config = get_model_config(self.provider, model) or {}
        if "reasoning_efforts" in model_config:  # glm-5.3 / glm-5.2
            effort = resolve_reasoning_effort(self.provider, model, thinking_level)
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
- `kimi-k2.7-code`, `kimi-k2.7-code-highspeed` — coding-focused (HighSpeed = faster serving), 262,144-token context. They **always think**: thinking cannot be disabled (the API rejects `thinking.type=disabled`) and `reasoning_effort` is ignored. Config flag `thinking_always_on: True`; the expert dialogs show a fixed, disabled "Enabled" thinking selector (the toolbox model row shows no thinking control). Fixed `temperature = 1.0`.
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
> such models (the toolbox model row hides it). Adjustable temperatures are clamped to the provider's
> `max_temperature` (Z.AI `1.0`), and `render_temperature_input()` uses the same
> bound for its control. DeepSeek (`temperature_ignored_with_thinking`) still
> sends the value, but the UI disables the control while thinking is on because
> the API ignores it.

### Unified Implementation

**Location**: `lib/llm/llm_client.py`

```python
def _prepare_thinking_param(self, model: str, thinking_level: str = None) -> dict:
    """Prepare provider-specific thinking/reasoning parameter.

    Returns:
        tuple: (extra_body_dict, direct_params_dict)
    """
    # DeepSeek first: API defaults to thinking-enabled, so "none" must explicitly disable.
    if self.provider == "deepseek":
        if thinking_level in ("high", "max"):
            return {}, {"reasoning_effort": thinking_level}
        return {"thinking": {"type": "disabled"}}, {}

    # Z.AI / KIMI: per-model handling (reasoning_effort vs. thinking.type
    # toggle) — see the Z.AI and KIMI sections above.
    if self.provider == "zai":
        ...
    if self.provider == "kimi":
        ...

    # OpenAI: reasoning_effort always sent explicitly (including "none");
    # unsupported levels fall back to the model's default effort.
    if self.provider == "openai":
        effort = resolve_reasoning_effort(self.provider, model, thinking_level)
        return {}, {"reasoning_effort": effort}

    # Other providers: no thinking parameter
    return {}, {}
```

## Connection Pooling

### Client Pool Implementation

**Location**: `lib/llm/client_pool.py`

**Purpose**: Cache and reuse LLM client instances

**Key Function**: `get_cached_client(provider, api_key)`

**Cache Key**: the function arguments `(provider, api_key)` (Streamlit `@st.cache_resource`)

**Benefits**:
- ~50% reduction in client creation overhead
- Faster API calls (no re-authentication)
- Reduced resource usage

### Implementation

```python
import streamlit as st
from lib.llm.llm_client import LLMClient


@st.cache_resource
def get_cached_client(provider: str, api_key: str) -> LLMClient:
    """Streamlit-cached client getter with resource-level caching."""
    return LLMClient(provider=provider, api_key=api_key)
```

The underlying `OpenAI` client is available as `LLMClient.client` (used e.g. by `lib/audio/transcription.py` for `audio.transcriptions.create`).

**Cache Invalidation**:
- Automatic when API key changes
- Manual: Restart application

## Using Different Providers

### Per-Expert Provider Selection

Provider, model, thinking level and temperature are stored per expert in `configs/{expert_id}.yaml` (`metadata.provider`, `metadata.model`, `metadata.thinking_level`, `temperature`) and read with `get_llm_metadata(config)`.

**UI Controls** (model row of the chat toolbox, `_render_model_settings()` in `lib/ui/chat_toolbox.py`):
- One dropdown with `"provider/model"` options for every provider that has an API key (`_model_options()`); choosing a model of another provider switches the expert's provider
- Thinking control (`_render_thinking_select()`) and temperature input only where the model supports them
- Changes are saved immediately via `update_config()` + `invalidate_expert_cache()`

The expert dialogs (create/edit, `lib/ui/dialogs.py`) offer the same settings via `render_provider_selection()`, `render_thinking_mode_ui()` and `render_temperature_input()`.

### Generating Responses

**Unified interface regardless of provider** (simplified from `handle_user_input()` in `templates/template.py`):
```python
from lib.config.config_manager import get_llm_metadata
from lib.llm.client_pool import get_cached_client
from lib.storage import StreamingCache

provider, model, thinking_level = get_llm_metadata(config)
api_key = st.session_state["api_keys"][provider]

# Get cached client
client = get_cached_client(provider=provider, api_key=api_key)

# Stream the response in a background thread (calls client.chat_stream())
cache = StreamingCache(EXPERT_ID)
cache.start_streaming_to_file(
    client=client,
    messages=api_messages,
    temperature=config.get("temperature", 1.0),
    model=model,
    system_prompt=system_prompt_with_lang,
    thinking_level=thinking_level,
)

# Non-streaming alternative
response = client.chat(
    messages=api_messages,
    temperature=temperature,
    model=model,
    system_prompt=system_prompt,
    thinking_level=thinking_level,
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
        "api_key_env": "NEWPROVIDER_API_KEY",
        "base_url": "https://api.newprovider.com/v1",
        "default_model": "new-model",
        "icon_path": "icons/newprovider_logo.png",
        "models": {
            "new-model": {
                "display_name": "New Model",
                "max_tokens": 128000,
                "thinking_param": {"thinking": {"type": "enabled"}},
                # optional: "vision": True, "reasoning_efforts": [...],
                # "fixed_temperature": 1.0, ...
            }
        }
    }
}
```

Also add the provider to `PROVIDER_LINKS` and `PROVIDER_AVATARS` (same file) and to the `Provider` enum / `ProviderKey` in `lib/shared/types.py`.

### Step 2: Update Thinking Parameter Handling

**File**: `lib/llm/llm_client.py`

**Add to `_prepare_thinking_param()`**:
```python
def _prepare_thinking_param(self, model: str, thinking_level: str = None) -> dict:
    # ... existing logic ...

    # New provider thinking parameter
    if self.provider == "newprovider":
        if not thinking_level or thinking_level == "none":
            return {"thinking": {"type": "disabled"}}, {}
        return {"thinking": {"type": "enabled"}}, {}

    return {}, {}
```

### Step 3: API Key Validation

**File**: `lib/shared/helpers.py`

The Settings page (`pages/9998_Settings.py`) lists every provider in `LLM_PROVIDERS` in its provider selectbox automatically and saves the key under `api_key_env` via `save_provider_api_key()`. Add a format pattern for the new provider to `PROVIDER_KEY_PATTERNS` in `validate_api_key()`; without one, only the generic minimum length (20 characters) is checked.

### Step 4: Update Secrets Template

**File**: `.streamlit/secrets.toml.example`

```toml
# ... existing keys ...

NEWPROVIDER_API_KEY = ""
```

### Step 5: Lookup Tables

**File**: `lib/shared/constants.py`

No changes needed: `MODEL_LOOKUP`, `PROVIDER_NAMES`, `DEFAULT_MODELS`, `BASE_URLS`, `API_KEY_ENVS` and `MAX_TOKENS` are generated from `LLM_PROVIDERS`.

## Provider Comparison

### Cost

| Provider | Relative Cost | Best For |
|----------|--------------|----------|
| **DeepSeek** | $ | Cost-effective daily use |
| **OpenAI** | $$$ | Complex reasoning tasks |
| **Z.AI** | $$ | Chinese language optimization |

### Features

| Feature | DeepSeek | OpenAI | Z.AI | KIMI |
|---------|----------|--------|------|------|
| **Reasoning** | Both models, optional | All models (GPT-6.1 Sol / GPT-6 Astra always) | GLM-5.3 / GLM-5.2 always; others optional | K3 / K2.7 Code always; K2.6 optional |
| **Thinking Levels** | none/high/max | none/low/medium/high/xhigh (model-dependent) | low/high/max (GLM-5.3), high/max (GLM-5.2), on/off (others) | low/high/max (K3), on/off (K2.6) |
| **Context Window** | 1M | 400K–1.05M | 200K–1M | 262K–1M |
| **Image Input** | deepseek-flash | All models | No | All models |
| **Language Strength** | English | Multilingual | Chinese | — |

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
| **DeepSeek** | Fast | +50% with thinking |
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
from lib.llm.client_pool import get_cached_client

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
    response = client.chat(messages=messages, model=model)
except Exception as e:  # LLMClient re-raises API errors as Exception("Error calling <provider> API: ...")
    st.error(f"Provider error: {sanitize_error_message(str(e))}")
    # Fallback to different provider
```

### 3. Validate Provider/Model Combinations

**Check availability**:
```python
try:
    get_model_config(provider, model)  # raises ValueError for unknown combinations
except ValueError:
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
