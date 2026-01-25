# User Guide - Basics

This guide covers the fundamentals of using ExpertGPTs for chatting with experts, navigation, and understanding the basic workflow.

## Overview

ExpertGPTs provides access to multiple domain-specific AI experts, each specialized in different fields. Each expert maintains its own conversation history and can be customized independently.

## Navigation

### Sidebar Navigation

The sidebar displays all available experts as navigation items:

- **:material/home:** Home Page - Expert list and management
- **:material/psychology: {Expert Name}** - Individual expert pages
- **:material/settings:** Settings - Configuration

### Home Page

The Home page is your central hub for:

- **Viewing all experts** - See all created experts at a glance
- **Adding new experts** - Use the "➕ Add Chat" button (only available here)
- **Managing experts** - Edit or delete existing experts

### Expert Pages

Each expert has a dedicated page with:

- **Chat interface** - Conversate with the expert
- **Provider selection** - Choose LLM provider per expert
- **Model selection** - Choose specific model within provider
- **Temperature control** - Adjust response creativity
- **Thinking level** - Enable/disable reasoning (for supported models)

### Settings Page

Access configuration options:
- **General** - Theme, language, defaults
- **API Keys** - Manage API keys for all providers
- **About** - Version information and acknowledgments

## Chatting with Experts

### Selecting an Expert

Click on any expert in the sidebar to load their page. You'll see:
- Expert name and description
- Chat history (if any)
- Input field at the bottom

### Sending Messages

1. Type your question or prompt in the chat input
2. Press **Enter** or click the send button
3. The expert responds, maintaining conversation context

### Conversation Context

**What is context?**
- The expert "remembers" previous messages in the current session
- Enables multi-turn conversations
- Each expert has independent context

**Context persistence:**
- **Session-based**: Context persists while the app is running
- **Chat history**: Conversations saved to `chat_history/{expert_id}.json`
- **Auto-loaded**: History loads automatically when you revisit an expert

### Multi-Turn Conversations

Example conversation with Python Expert:

```
User: How do I read a file in Python?
Expert: You can use the `open()` function...
User: Can you show me an example?
Expert: Here's an example... [shows code]
User: What about error handling?
Expert: You should use try-except blocks...
```

Each response builds on the previous context.

## Provider and Model Selection

### Understanding Providers

ExpertGPTs supports multiple LLM providers through OpenAI-compatible APIs:

| Provider | Base URL | Default Model | Characteristics |
|----------|----------|---------------|-----------------|
| **DeepSeek** | api.deepseek.com | deepseek-chat | Cost-effective, high quality |
| **OpenAI** | api.openai.com/v1 | o3-mini | Advanced reasoning |
| **Z.AI** | api.z.ai/v1 | glm-4.7 | GLM models |

### Selecting a Provider

Each expert can use a different provider:

1. Go to the expert's page
2. Use the "Provider" dropdown in the sidebar
3. Select your preferred provider

**Use case examples**:
- Use **DeepSeek** for cost-effective daily tasks
- Use **OpenAI** for complex reasoning tasks
- Use **Z.AI** for Chinese language optimization

### Selecting a Model

Each provider offers multiple models:

**DeepSeek**:
- `deepseek-chat` - Standard model (default)
- `deepseek-reasoner` - Reasoning-optimized model

**OpenAI**:
- `o3-mini` - Mini reasoning model (default)
- `gpt-4o` - Flagship model
- `gpt-4o-mini` - Cost-effective option

**Z.AI**:
- `glm-4.7` - Standard model (default)
- `glm-4.7-thinking` - Reasoning-enabled model

## Temperature and Thinking Level

### Temperature

Controls response creativity and randomness:

| Range | Style | Best For |
|-------|-------|----------|
| **0.0 - 0.3** | Focused, deterministic | Coding, math, facts |
| **0.4 - 0.7** | Balanced (recommended) | General advice, explanations |
| **0.8 - 1.2** | Creative | Brainstorming, analysis |
| **1.3 - 2.0** | Highly creative | Creative writing, ideation |

**See also**: [Temperature Guide](temperature-guide.md) for detailed explanations

### Thinking Level

Enables/disables reasoning capabilities (provider-specific):

- **None** - Standard generation (default)
- **Low** - Light reasoning
- **Medium** - Balanced reasoning
- **High** - Deep reasoning

**Availability**:
- **OpenAI**: Supports all levels (reasoning_effort parameter)
- **DeepSeek**: Enabled/disabled based on model selection
- **Z.AI**: Enabled/disabled via extra_body parameter

> **Note**: Reasoning increases response time and cost. Use when needed for complex tasks.

## Understanding Chat History

### Where History is Stored

Chat history is saved in `chat_history/{expert_id}.json` files.

**Example**:
```
chat_history/
├── 1001_python_expert.json
├── 1002_data_scientist.json
└── 1003_writing_assistant.json
```

### History Limits

- **File size limit**: 1MB per expert
- **Auto-trimming**: Oldest messages removed when limit exceeded
- **Seamless**: No user action needed

### Viewing History

When you revisit an expert:
1. Previous conversation loads automatically
2. Context is restored
3. You can continue from where you left off

### Clearing History

**Option 1: Via File System**
```bash
rm chat_history/{expert_id}.json
```

**Option 2: In-App** (if implemented)
Use the "Clear Chat" button in the chat interface.

## Session State Management

ExpertGPTs uses multi-layered state management:

### Shared Session State
- Initialized once per session
- API keys for all providers
- Default LLM settings (provider, model, temperature)
- Language preference
- Navigation state

### Per-Expert Session State
- **Messages history**: `st.session_state[f"messages_{expert_id}"]`
- **Provider selection**: `st.session_state[f"provider_{expert_id}"]`
- **Model selection**: `st.session_state[f"model_{expert_id}"]`
- **Temperature**: `st.session_state[f"temperature_{expert_id}"]`
- **Thinking level**: `st.session_state[f"thinking_{expert_id}"]`

### Persistent Storage
- **Chat history**: `chat_history/{expert_id}.json`
- **Expert configurations**: `configs/{expert_id}.yaml`
- **User preferences**: `.streamlit/app_defaults.toml`
- **Theme settings**: `.streamlit/config.toml`

**See also**: [Architecture - State Management](../architecture/state-management.md) for technical details

## Best Practices for Effective Chats

### 1. Choose the Right Expert

Select the expert that best matches your domain:
- **Python Expert** - For Python-specific questions
- **Data Scientist** - For data analysis questions
- **Copywriter** - For marketing and content creation

### 2. Provide Clear Context

Give the expert relevant background:
```
Instead of: "How do I do this?"
Try: "I'm building a web scraper with Python. How do I handle pagination?"
```

### 3. Use Appropriate Temperature

- **Low (0.2)** - For code and technical answers
- **Medium (0.7)** - For explanations and advice
- **High (1.5)** - For brainstorming and creative tasks

### 4. Leverage Conversation Context

Build on previous responses:
```
User: Explain recursion
Expert: [Explains recursion]
User: Can you show me an example?
Expert: [Shows example]
User: How does it differ from iteration?
Expert: [Compares recursion vs iteration]
```

### 5. Switch Providers When Needed

- Use **DeepSeek** for cost-effective daily tasks
- Use **OpenAI** with reasoning for complex problems
- Use **Z.AI** for Chinese language tasks

## Common Workflows

### Workflow 1: Get Coding Help

1. Navigate to **Python Expert**
2. Set temperature to **0.3** (focused)
3. Describe your coding problem with context
4. Ask follow-up questions to refine solution
5. Request code examples if needed

### Workflow 2: Improve Writing

1. Navigate to **Copywriter**
2. Set temperature to **0.7** (balanced)
3. Paste your text
4. Ask for specific improvements (grammar, clarity, tone)
5. Iterate based on suggestions

### Workflow 3: Brainstorm Ideas

1. Navigate to appropriate expert or create custom one
2. Set temperature to **1.2** (creative)
3. Provide context and constraints
4. Ask for multiple options
5. Explore variations with follow-ups

## Keyboard Shortcuts

While Streamlit doesn't support custom keyboard shortcuts, you can use:

- **Enter** - Send message (when in chat input)
- **Shift + Enter** - New line in chat input
- **Tab** - Navigate between fields

## Tips and Tricks

### 1. Pin Frequently Used Experts

Streamlit doesn't support pinning, but you can:
- Rename experts with prefixes (e.g., "★ Python Expert")
- Arrange experts by usage frequency in naming

### 2. Use Custom Experts for Specific Tasks

Create focused experts:
- "Code Reviewer" - Set low temperature, specific prompt
- "Creative Writer" - Set high temperature, creative prompt
- "Research Assistant" - Set medium temperature, analytical prompt

### 3. Leverage Multilingual Support

- Create experts in different languages
- Switch UI language without losing expert functionality
- Experts respond in your selected language automatically

### 4. Manage Token Usage

- Monitor token counts in chat interface
- Lower temperature for shorter, focused responses
- Switch to cost-effective providers (DeepSeek) for simple tasks

## Troubleshooting

### Expert Not Responding

**Problem**: No response after sending message

**Solutions**:
1. Check API key is configured (Settings → API Keys)
2. Verify API key has sufficient credits
3. Check internet connection
4. Try switching provider

### Context Lost

**Problem**: Expert doesn't remember previous conversation

**Solutions**:
1. Check if chat history file exists: `ls chat_history/`
2. Verify you're on the same expert page
3. Session context resets when app restarts (history persists)

### Slow Responses

**Problem**: Expert takes too long to respond

**Solutions**:
1. Disable thinking level (set to "None")
2. Switch to faster provider/model
3. Reduce message length
4. Check API provider status

### Messages Cut Off

**Problem**: Response ends abruptly

**Solutions**:
1. This can happen with long responses
2. Ask "Continue" to get the rest
3. Or rephrase question for shorter answer

## Next Steps

- **[Creating Experts Guide](creating-experts.md)** - Learn to create custom experts
- **[Customization Guide](customization.md)** - Personalize themes and settings
- **[Temperature Guide](temperature-guide.md)** - Master temperature settings
- **[Configuration Guide](../configuration/overview.md)** - Understand expert configuration

---

**Back to**: [Documentation Home](../README.md) | [First Use](../getting-started/first-use.md)
