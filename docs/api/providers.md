# LLM Providers API Reference

This guide provides details about supported LLM providers and their APIs.

## Supported Providers

ExpertGPTs integrates with multiple LLM providers through OpenAI-compatible APIs.

For the input modalities (text, image, audio, video) of each model, see [Model Capabilities](model-capabilities.md).

### DeepSeek

**Base URL**: `https://api.deepseek.com`

**Default Model**: `deepseek-flash`

**Models**:
- `deepseek-flash` - DeepSeek V4.1 Flash, cost-effective (1M context). Replaces `deepseek-v4-flash`, which DeepSeek retired as an alias
- `deepseek-v4-pro` - Premium flagship (1M context, 1.6T/49B active params)

**Thinking Parameter**: Two knobs, both models support both modes
- `reasoning_effort` (top-level): `"high"` (default on API) or `"max"`
- `thinking.type = "disabled"` (via `extra_body`) — used only to turn thinking off; the API defaults to enabled

**UI effort values**: `none`, `high`, `max`

**Temperature**: adjustable (`0.0`–`2.0`), but **only with thinking disabled** (`none`). In thinking mode the API ignores `temperature` without an error, so the app disables the temperature control and shows a hint while a thinking level is selected (provider flag `temperature_ignored_with_thinking`). See [Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode).

**API Documentation**: [https://api-docs.deepseek.com/](https://api-docs.deepseek.com/)

**Characteristics**:
- Most cost-effective
- 1M context window
- Dual thinking modes per model
- Good for daily use

**Get API Key**: [https://platform.deepseek.com/](https://platform.deepseek.com/)

---

### OpenAI

**Base URL**: `https://api.openai.com/v1`

**Default Model**: `gpt-6.1-sol`

**Models**:
- `gpt-6.1-sol` - GPT-6.1 Sol, default (1.05M context window), always reasons
- `gpt-6-astra` - GPT-6 Astra, top tier (1.05M context), always reasons
- `gpt-6-luna` - GPT-6 Luna, cost-effective (1.05M context)
- `gpt-5.6-sol` - Frontier flagship (1.05M context window)
- `gpt-5.6-terra` - Balanced performance/price (1.05M context)
- `gpt-5.6-luna` - Efficient, high-volume option (1.05M context)
- `gpt-5.4-mini` - Cost-effective option (400K context)
- `gpt-5.4-nano` - High-throughput option (400K context)

**Thinking Parameter**: `reasoning_effort`
- `gpt-6.1-sol`, `gpt-6-astra`: `"low"`, `"medium"`, `"high"`, `"xhigh"` — default `"medium"` (no `"none"`; these models always reason)
- `gpt-6-luna`, GPT-5.6 and GPT-5.4 models: `"none"`, `"low"`, `"medium"`, `"high"`, `"xhigh"` — default `"none"`
- `"max"` exists only in the Responses API, not in Chat Completions (which the app uses), so it is not offered
- Passed as direct parameter in API call and **always sent explicitly, including `"none"`** (if omitted, the API applies its own default and GPT-6 would reason anyway). Unsupported levels fall back to the model's default effort

**Temperature**: fixed at `1.0` for all OpenAI models (OpenAI rejects `temperature != 1` whenever reasoning is active); the app enforces this automatically via the provider-level `fixed_temperature`.

**API Documentation**: [https://platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference)

**Characteristics**:
- Advanced reasoning, coding, agentic tasks
- 1.05M token context window (GPT-6 and GPT-5.6 families)
- `xhigh` reasoning effort for deep reasoning
- GPT-6 family optimized for complex tasks
- Higher cost but premium quality

**Get API Key**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

---

### Z.AI

**Base URL**: `https://api.z.ai/api/paas/v4`

**Default Model**: `glm-5.3`

**Models**:
- `glm-5.3` - Flagship model (default), 1M context, 128K output, always reasons, adjustable reasoning effort (`low`/`high`/`max`, default `max`)
- `glm-5.2` - 1M context, always reasons, adjustable reasoning effort (`high`/`max`)
- `glm-5` - 200K context, enabled/disabled thinking toggle
- `glm-4.7-flash` - Free model, 200K context, enabled/disabled thinking toggle

**Thinking Parameter**: `thinking.type`
- Values: `"enabled"`, `"disabled"`
- Passed via extra_body
- `glm-5.3` and `glm-5.2` always send `thinking.type = "enabled"` plus `reasoning_effort` as a direct parameter (`low`/`high`/`max` for GLM-5.3, `high`/`max` for GLM-5.2)

**Temperature**: adjustable within `0.0`–`1.0` (API default `1.0`), with or without thinking. The provider config sets `max_temperature: 1.0`: the UI caps the control at `1.0`, and the client clamps higher stored values (e.g. an expert created with `1.5` under another provider) to `1.0`. See the [Chat Completion API reference](https://docs.z.ai/api-reference/llm/chat-completion).

**API Documentation**: [https://z.ai/](https://z.ai/)

**Characteristics**:
- GLM models optimized for Chinese
- Competitive pricing
- Good for multilingual applications

**Get API Key**: [https://z.ai/](https://z.ai/)

---

### KIMI

**Base URL**: `https://api.moonshot.ai/v1`

**Default Model**: `kimi-k3`

**Models**:
- `kimi-k3` - Flagship model (1M context window), always-on reasoning
- `kimi-k2.7-code` - Coding-focused model (256K context window), always thinks
- `kimi-k2.7-code-highspeed` - Faster-serving variant of K2.7 Code (256K context window), always thinks
- `kimi-k2.6` - Previous flagship (256K context window)

**Thinking Parameter**: differs by model generation
- `kimi-k3` — `reasoning_effort` as a **top-level** parameter: `"low"`, `"high"` or `"max"` (default `"max"`; always reasons). Do **not** send the K2.x `thinking` parameter.
- `kimi-k2.7-code`, `kimi-k2.7-code-highspeed` — always think: thinking cannot be disabled and `reasoning_effort` is ignored by the API. The UI shows a fixed, disabled "Enabled" thinking selector.
- `kimi-k2.6` — `thinking.type` (`"enabled"` / `"disabled"`) via `extra_body`. The API thinks by default, so "Disabled" sends `thinking.type = "disabled"` explicitly.

**Temperature**: fixed by the API (the app enforces this automatically) — `kimi-k3` and `kimi-k2.7-code*` use `1.0`; `kimi-k2.6` uses `1.0` with thinking and `0.6` without.

**API Documentation**: [https://platform.kimi.ai/docs](https://platform.kimi.ai/docs)

**Characteristics**:
- `kimi-k3`: 1M context window (1,048,576 tokens), always-on reasoning (`low`/`high`/`max`)
- `kimi-k2.7-code`, `kimi-k2.7-code-highspeed`, `kimi-k2.6`: 256K context window (262,144 tokens)
- Native multimodal support (images, videos), see [Model Capabilities](model-capabilities.md); the app sends images only
- Strong reasoning capabilities

**Get API Key**: [https://platform.kimi.ai/console](https://platform.kimi.ai/console)

---

## API Integration

### Client Implementation

**Technology**: OpenAI Python SDK with custom `base_url`

**Example**:
```python
from openai import OpenAI

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"  # Provider-specific
)

response = client.chat.completions.create(
    model="deepseek-flash",
    messages=[...]
)
```

### Connection Pooling

ExpertGPTs caches client instances per provider/api_key combination.

**Implementation**: `lib/llm/client_pool.py`

**Benefit**: ~50% reduction in client creation overhead

---

## Provider-Specific Features

### Reasoning/Thinking

**DeepSeek**: `reasoning_effort` (top-level) + `thinking.type` (extra_body)
- Both V4 models support dual thinking modes
- `reasoning_effort` values: `high`, `max`
- API defaults to thinking-enabled; pass `extra_body={"thinking": {"type": "disabled"}}` to turn off

**OpenAI**: `reasoning_effort` parameter
- Values: none (not for gpt-6.1-sol / gpt-6-astra), low, medium, high, xhigh
- Direct parameter in API call, always sent explicitly; temperature fixed at 1.0

**Z.AI**: `thinking.type` via extra_body
- Set in `extra_body` dictionary
- Values: enabled, disabled
- GLM-5.3 / GLM-5.2: thinking always enabled, plus `reasoning_effort` (GLM-5.3: low/high/max; GLM-5.2: high/max)

**KIMI**:
- `kimi-k3`: `reasoning_effort` as a top-level parameter (`low`/`high`/`max`; always reasons)
- `kimi-k2.7-code*`: always thinks; no adjustable thinking parameter
- `kimi-k2.6`: `thinking.type` (`enabled`/`disabled`) via extra_body; `disabled` is sent explicitly since the API thinks by default

### Image Input

Models that accept images declare `"vision": True` in their `LLM_PROVIDERS` config; `supports_images(provider, model)` in `lib/shared/constants.py` reads the flag. Only for these models is "Attach image" enabled in the chat toolbox, and images are sent as OpenAI-style `image_url` content parts with base64 data URLs (Chat Completions).

| Provider | Image input | Notes |
|----------|-------------|-------|
| **DeepSeek** | `deepseek-flash` | `deepseek-v4-pro` silently ignores images, so it has no flag |
| **OpenAI** | All 8 models | |
| **Z.AI** | None | GLM models are text-only per the Z.AI docs (not live-tested) |
| **KIMI** | All 4 models | Including `kimi-k2.7-code-highspeed` |

Verified live via Chat Completions on 2026-10-10 (except Z.AI). For models without the flag, earlier images in a conversation are replaced by a text note when the request is sent (see `to_api_content()` in `lib/shared/attachments.py`).

### Model Selection

Each provider offers multiple models with different capabilities:

**Cost-Effective**: DeepSeek, OpenAI mini models
**High Quality**: OpenAI GPT-6 series
**Chinese Optimization**: Z.AI GLM models, KIMI
**Large Context**: KIMI K3, DeepSeek, Z.AI GLM-5.3, OpenAI GPT-6 / GPT-5.6 (1M+ tokens)
**Reasoning**: DeepSeek V4 (thinking mode), OpenAI GPT-6, Z.AI GLM-5.3, KIMI K3 (always-on)
**Coding**: KIMI K2.7 Code / K2.7 Code HighSpeed
**Image Input**: DeepSeek Flash, all OpenAI models, all KIMI models

---

## Rate Limits and Pricing

Check provider dashboards for current rates and limits:

- **DeepSeek**: [https://platform.deepseek.com/](https://platform.deepseek.com/)
- **OpenAI**: [https://platform.openai.com/usage](https://platform.openai.com/usage)
- **Z.AI**: [https://z.ai/](https://z.ai/)
- **KIMI**: [https://platform.kimi.ai/console](https://platform.kimi.ai/console)

---

## Related Documentation

- **[Multi-Provider LLM Architecture](../architecture/multi-provider-llm.md)** - Integration details
- **[API Keys Guide](../configuration/api-keys.md)** - Key management
- **[Configuration Overview](../configuration/overview.md)** - Configuration system

---

**Back to**: [Documentation Home](../README.md)
