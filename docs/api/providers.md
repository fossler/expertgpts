# LLM Providers API Reference

This guide provides details about supported LLM providers and their APIs.

## Supported Providers

ExpertGPTs integrates with multiple LLM providers through OpenAI-compatible APIs.

### DeepSeek

**Base URL**: `https://api.deepseek.com`

**Default Model**: `deepseek-v4-flash`

**Models**:
- `deepseek-v4-flash` - Cost-effective V4 model (1M context, 284B/13B active params)
- `deepseek-v4-pro` - Premium flagship (1M context, 1.6T/49B active params)

**Thinking Parameter**: Two knobs, both models support both modes
- `reasoning_effort` (top-level): `"high"` (default on API) or `"max"`
- `thinking.type = "disabled"` (via `extra_body`) — used only to turn thinking off; the API defaults to enabled

**UI effort values**: `none`, `high`, `max`

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

**Default Model**: `gpt-5.6-terra`

**Models**:
- `gpt-5.6-sol` - Frontier flagship (1.05M context window)
- `gpt-5.6-terra` - Balanced performance/price, default (1.05M context)
- `gpt-5.6-luna` - Efficient, high-volume option (1.05M context)
- `gpt-5.4-mini` - Cost-effective option (400K context)
- `gpt-5.4-nano` - High-throughput option (400K context)

**Thinking Parameter**: `reasoning_effort`
- Values: `"none"`, `"low"`, `"medium"`, `"high"`, `"xhigh"` (all current OpenAI models top out at `xhigh`)
- Default: `"none"`
- Passed as direct parameter in API call

**API Documentation**: [https://platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference)

**Characteristics**:
- Advanced reasoning, coding, agentic tasks
- 1.05M token context window (GPT-5.6 family)
- `xhigh` reasoning effort for deep reasoning
- GPT-5.6 family optimized for complex tasks
- Higher cost but premium quality

**Get API Key**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

---

### Z.AI

**Base URL**: `https://api.z.ai/api/paas/v4`

**Default Model**: `glm-5.2`

**Models**:
- `glm-5.2` - Flagship model (default), 1M context, adjustable reasoning effort (`high`/`max`)
- `glm-5` - 200K context, enabled/disabled thinking toggle
- `glm-4.7-flash` - Free model, 200K context, enabled/disabled thinking toggle

**Thinking Parameter**: `thinking.type`
- Values: `"enabled"`, `"disabled"`
- Passed via extra_body
- `glm-5.2` additionally supports `reasoning_effort` (`high`/`max`) as a direct parameter, applied while thinking is enabled

**API Documentation**: [https://z.ai/](https://z.ai/)

**Characteristics**:
- GLM models optimized for Chinese
- Competitive pricing
- Good for multilingual applications

**Get API Key**: [https://z.ai/](https://z.ai/)

---

### KIMI

**Base URL**: `https://api.moonshot.ai/v1`

**Default Model**: `kimi-k2.6`

**Models**:
- `kimi-k2.6` - Flagship model (256K context window)

**Thinking Parameter**: `thinking.type`
- Values: `"enabled"`, `"disabled"`
- Passed via extra_body
- Default: enabled for kimi-k2.6

**API Documentation**: [https://platform.kimi.ai/docs](https://platform.kimi.ai/docs)

**Characteristics**:
- 256K context window (262,144 tokens)
- Native multimodal support (images, videos)
- Strong reasoning capabilities
- Chinese optimization

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
    model="deepseek-v4-flash",
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
- Values: low, medium, high
- Direct parameter in API call

**Z.AI**: `thinking.type` via extra_body
- Set in `extra_body` dictionary
- Values: enabled, disabled

**KIMI**: `thinking.type` via extra_body
- Set in `extra_body` dictionary
- Values: enabled, disabled
- Default: enabled for kimi-k2.6

### Model Selection

Each provider offers multiple models with different capabilities:

**Cost-Effective**: DeepSeek, OpenAI mini models
**High Quality**: OpenAI GPT-5.6 series
**Chinese Optimization**: Z.AI GLM models, KIMI
**Large Context**: KIMI (256K tokens)
**Reasoning**: DeepSeek V4 (thinking mode), OpenAI GPT-5.6, KIMI K2.6

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
