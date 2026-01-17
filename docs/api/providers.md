# LLM Providers API Reference

This guide provides details about supported LLM providers and their APIs.

## Supported Providers

ExpertGPTs integrates with multiple LLM providers through OpenAI-compatible APIs.

### DeepSeek

**Base URL**: `https://api.deepseek.com`

**Default Model**: `deepseek-chat`

**Models**:
- `deepseek-chat` - Standard model (4096 max tokens)
- `deepseek-reasoner` - Reasoning-optimized (8192 max tokens)

**Thinking Parameter**: Model-dependent
- `deepseek-chat`: No thinking parameter
- `deepseek-reasoner`: `thinking.type = "enabled"` (via extra_body)

**API Documentation**: [https://api-docs.deepseek.com/](https://api-docs.deepseek.com/)

**Characteristics**:
- Most cost-effective
- High quality responses
- Good for daily use

**Get API Key**: [https://platform.deepseek.com/](https://platform.deepseek.com/)

---

### OpenAI

**Base URL**: `https://api.openai.com/v1`

**Default Model**: `o3-mini`

**Models**:
- `o3-mini` - Mini reasoning model (65536 max tokens)
- `gpt-4o` - Flagship model
- `gpt-4o-mini` - Cost-effective option

**Thinking Parameter**: `reasoning_effort`
- Values: `"low"`, `"medium"`, `"high"`
- Passed as direct parameter in API call

**API Documentation**: [https://platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference)

**Characteristics**:
- Advanced reasoning capabilities
- o3-series optimized for complex tasks
- Higher cost but premium quality

**Get API Key**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

---

### Z.AI

**Base URL**: `https://api.z.ai/v1`

**Default Model**: `glm-4.7`

**Models**:
- `glm-4.7` - Standard model
- `glm-4.7-thinking` - Reasoning-enabled model

**Thinking Parameter**: `thinking.type`
- Values: `"enabled"`, `"disabled"`
- Passed via extra_body

**API Documentation**: [https://z.ai/](https://z.ai/)

**Characteristics**:
- GLM models optimized for Chinese
- Competitive pricing
- Good for multilingual applications

**Get API Key**: [https://z.ai/](https://z.ai/)

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
    model="deepseek-chat",
    messages=[...]
)
```

### Connection Pooling

ExpertGPTs caches client instances per provider/api_key combination.

**Implementation**: `utils/client_pool.py`

**Benefit**: ~50% reduction in client creation overhead

---

## Provider-Specific Features

### Reasoning/Thinking

**DeepSeek**: Enabled via model selection
- Use `deepseek-reasoner` for reasoning
- No separate parameter needed

**OpenAI**: `reasoning_effort` parameter
- Values: low, medium, high
- Direct parameter in API call

**Z.AI**: `thinking.type` via extra_body
- Set in `extra_body` dictionary
- Values: enabled, disabled

### Model Selection

Each provider offers multiple models with different capabilities:

**Cost-Effective**: DeepSeek, OpenAI mini models
**High Quality**: OpenAI o3-series, GPT-4o
**Chinese Optimization**: Z.AI GLM models
**Reasoning**: DeepSeek Reasoner, OpenAI o3-mini

---

## Rate Limits and Pricing

Check provider dashboards for current rates and limits:

- **DeepSeek**: [https://platform.deepseek.com/](https://platform.deepseek.com/)
- **OpenAI**: [https://platform.openai.com/usage](https://platform.openai.com/usage)
- **Z.AI**: [https://z.ai/](https://z.ai/)

---

## Related Documentation

- **[Multi-Provider LLM Architecture](../architecture/multi-provider-llm.md)** - Integration details
- **[API Keys Guide](../configuration/api-keys.md)** - Key management
- **[Configuration Overview](../configuration/overview.md)** - Configuration system

---

**Back to**: [Documentation Home](../README.md)
