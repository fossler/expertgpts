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
- **:material/help:** Help - In-app documentation

### Home Page

The Home page is your central hub for:

- **Viewing all experts** - See all created experts at a glance
- **Adding new experts** - Use the "➕ Add Chat" button in the sidebar Toolbox (also available as "➕ Add new Chat" in Settings → Expert Management)

Editing and deleting experts is done in **Settings** → **Expert Management**.

### Expert Pages

Each expert has a dedicated page with:

- **Chat interface** - Conversate with the expert
- **Chat toolbox** below the chat input - attachments, voice input, clear chat history, context usage
- **Model selection** - Choose the model (and with it the provider) per expert, in the toolbox
- **Temperature control** - Adjust response creativity (where the model allows it)
- **Thinking level** - Choose the reasoning level (for supported models)

The sidebar of an expert page only contains the navigation and the git branch footer.

### Settings Page

Access configuration options:
- **General** - Theme and language
- **API Key** - Manage API keys for all providers
- **Default LLM** - Default provider, model and thinking mode for new experts
- **Expert Management** - Add, edit and delete experts
- **Danger Zone** - Download all configurations, reset the application
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

### Attaching Files

Below the chat input are two rows: the toolbox row and, below it, the [model selection](#switching-providers). The toolbox row has, from left to right, **📎 Attach file**, **🖼️ Attach image**, **🎤 Voice input**, status notes about your attachments and, on the right, **🗑️ Clear Chat History** and the [context usage](#context-usage). Use **📎 Attach file** to add text files to your next message:

1. Click **Attach file** and choose one or more files in the popover
2. The toolbox lists the attached files ("📎 Attached: ...")
3. Type your prompt and send it; the files are sent together with the message

**Supported files:**
- Text files only (UTF-8), up to **200 KB** each
- Common text and code formats such as `.txt`, `.md`, `.csv`, `.json`, `.yaml`, `.xml`, `.log`, `.html`, `.py`, `.js`, `.sql` and more
- Files that are too large or not UTF-8 text are reported in the toolbox and skipped

**Good to know:**
- Each attachment appears in your message as a collapsible "📎 <filename>" section, also after reloading the page
- The file content becomes part of your message, so it counts toward the model's context and the chat history size limit
- Attachments are cleared after the message is sent; attach them again for later messages if needed (the expert still sees earlier attachments as part of the conversation)

### Attaching Images

Use **🖼️ Attach image** to send screenshots, photos or diagrams with your next message:

1. Click **Attach image** and choose one or more images in the popover
2. The toolbox lists the attached images ("🖼️ Images: ...")
3. Type your prompt and send it; the images are sent to the model together with the message

**Supported images:**
- PNG, JPEG, WebP and GIF, up to **5 MB** each
- Files that are too large or not valid images are reported in the toolbox and skipped

**Which models support images:**
- **DeepSeek**: `deepseek-flash` (not `deepseek-v4-pro`)
- **OpenAI**: all models
- **KIMI**: all models
- **Z.AI**: none (the GLM models are text-only)

For models without image support the button is disabled; hover over it to see "<model> does not support images". Switch the expert to a model that supports images to use it.

**Good to know:**
- Images appear as thumbnails in your message, also after reloading the page
- Images are stored locally in `chat_attachments/{expert_id}/` (not committed to git); the chat history only keeps a reference to them
- Images are not included in the context usage shown in the toolbox, although they do use part of the model's context
- If you later switch the expert to a model without image support, earlier images in the conversation are replaced by a short note ("[Image <name> omitted: the selected model does not support images]") when the conversation is sent; switching back sends them again
- If an image file was deleted, the message shows "no longer available" and the model receives a note instead of the image
- **🗑️ Clear Chat History** in the toolbox also deletes the expert's images

### Voice Input

**🎤 Voice input** in the toolbox records a voice message with your microphone (your browser asks for permission the first time):

1. Open **Voice input** and start the recording
2. Stop the recording: it is converted to text and **sent automatically** like a typed message, together with any attached files and images

**Which speech-to-text model is used** depends on the expert's provider:

| Expert provider | Transcription model | API key needed | Limit |
|---|---|---|---|
| OpenAI | `gpt-transcribe` (OpenAI) | OpenAI | 25 MB |
| DeepSeek, Z.AI, KIMI | `glm-asr-2512` (Z.AI GLM-ASR) | Z.AI | 30 seconds, 25 MB |

The popover shows the model in use. If the required API key is missing, the recorder is disabled and a notice tells you which key to add in Settings.

**Language**: Speak in the app's interface language for best results. OpenAI receives the interface language as a hint; for GLM-ASR, which has no language setting, a short sentence in the interface language is sent as context — without it, GLM-ASR often returned German speech in Chinese or translated it to English.

### Context Usage

The right side of the toolbox shows how much of the model's context window the conversation uses, as a compact button with a severity emoji and the percentage (e.g. "🟢 3.2%"; 🟢 below 50%, 🟡 below 75%, 🟠 below 90%, 🔴 from 90%). Click it for details: usage percentage, total and maximum tokens, and the tokens used by the system prompt and by the chat messages. Text attachments are counted; images are not.

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
| **DeepSeek** | api.deepseek.com | deepseek-flash | Cost-effective, 1M context, dual thinking modes |
| **OpenAI** | api.openai.com/v1 | gpt-6.1-sol | Advanced reasoning |
| **Z.AI** | api.z.ai/api/paas/v4 | glm-5.3 | GLM models |
| **KIMI** | api.moonshot.ai/v1 | kimi-k3 | 1M context, always-on reasoning |

### Selecting a Provider

Each expert can use a different provider and model. Switch directly below the chat input:

1. Go to the expert's page
2. Open the **model dropdown** in the second row below the chat input. It lists all models of every provider that has an API key, in this order: DeepSeek, OpenAI, Z.AI, KIMI
3. Select a model — the change is saved for this expert immediately (no save button)

Next to the model, only the settings the model actually supports are shown:

- **🧠 Thinking mode**: the model's reasoning levels (e.g. Low/Medium/High), or On/Off for GLM-5, GLM-4.7-Flash and KIMI K2.6. Nothing is shown for KIMI K2.7 Code, which always thinks. If the previous level isn't available for the new model, its default is used
- **🌡️ Temperature**: only for DeepSeek and Z.AI models. OpenAI and KIMI models use a fixed temperature, so the field is hidden. Z.AI accepts at most 1.0; for DeepSeek the field is disabled while thinking is enabled (DeepSeek ignores the temperature then; set thinking to "None" to use it)

Switching models mid-conversation keeps the history. Each answer keeps the logo of the provider that wrote it (answers saved before this feature show the current provider's logo).

**Use case examples**:
- Use **DeepSeek** for cost-effective daily tasks
- Use **OpenAI** for complex reasoning tasks
- Use **Z.AI** for Chinese language optimization

### Selecting a Model

Each provider offers multiple models:

**DeepSeek**:
- `deepseek-flash` - Cost-effective, 1M context, dual thinking modes (default)
- `deepseek-v4-pro` - Premium flagship, 1M context, dual thinking modes

**OpenAI**:
- `gpt-6.1-sol` - GPT-6.1 Sol, 1.05M context, always reasons (default)
- `gpt-6-astra` - GPT-6 Astra, top tier, 1.05M context, always reasons
- `gpt-6-luna` - GPT-6 Luna, cost-effective, 1.05M context
- `gpt-5.6-sol` - Frontier flagship, 1.05M context
- `gpt-5.6-terra` - Balanced performance/price, 1.05M context
- `gpt-5.6-luna` - Efficient, high-volume, 1.05M context
- `gpt-5.4-mini` - Cost-effective option, 400K context
- `gpt-5.4-nano` - High-throughput option, 400K context

**Z.AI**:
- `glm-5.3` - Flagship model (default), 1M context, always reasons, adjustable reasoning effort (low/high/max)
- `glm-5.2` - 1M context, adjustable reasoning effort (high/max)
- `glm-5` - 200K context
- `glm-4.7-flash` - Free model, 200K context

**KIMI**:
- `kimi-k3` - Flagship model (default), 1M context, always reasons, adjustable reasoning effort (low/high/max)
- `kimi-k2.7-code` - Coding-focused, 256K context, thinking always on
- `kimi-k2.7-code-highspeed` - Faster variant of K2.7 Code, 256K context, thinking always on
- `kimi-k2.6` - 256K context, thinking can be enabled/disabled

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

- **None** - Standard generation
- **Low** - Light reasoning
- **Medium** - Balanced reasoning
- **High** - Deep reasoning
- **Xhigh** - Extended reasoning (OpenAI only)
- **Max** - Maximum reasoning (DeepSeek, Z.AI GLM-5.3/5.2 and KIMI K3)

**Availability** (the options shown depend on the selected model):
- **OpenAI**: `gpt-6.1-sol` / `gpt-6-astra` always reason: `low`/`medium`/`high`/`xhigh` (default `medium`); other models: `none`/`low`/`medium`/`high`/`xhigh` (default `none`)
- **DeepSeek**: `none`/`high`/`max` (default `high`)
- **Z.AI**: GLM-5.3: `low`/`high`/`max` (default `max`); GLM-5.2: `high`/`max`; GLM-5 / GLM-4.7-Flash: enabled/disabled
- **KIMI**: K3: `low`/`high`/`max` (default `max`); K2.7 Code: always enabled; K2.6: enabled/disabled

If an expert's saved level isn't supported by the newly selected model, the model's default level is preselected.

> **Note**: Some models use a fixed temperature, so the temperature control is hidden in the toolbox (and disabled in the expert dialogs) for them: all OpenAI models (1.0), KIMI K3 and K2.7 Code (1.0), and KIMI K2.6 (1.0 with thinking, 0.6 without).

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

**Option 1: In-App**
Use **🗑️ Clear Chat History** in the toolbox below the chat input (left of the context usage). It opens a confirmation; **Delete permanently** removes the whole conversation of this expert, including attached images. The button is disabled while the history is empty.

**Option 2: Via File System**
```bash
rm chat_history/{expert_id}.json
rm -r chat_attachments/{expert_id}/   # attached images, if any
```

## Session State Management

ExpertGPTs uses multi-layered state management:

### Shared Session State
- Initialized once per session
- API keys for all providers
- Default LLM settings (provider, model, thinking level)
- Language preference
- Navigation state

### Per-Expert Session State
- **Messages history**: `st.session_state[f"messages_{expert_id}"]`
- **Config cache version**: `st.session_state[f"cache_version_{expert_id}"]` (incremented when the config changes)
- **Provider, model, temperature and thinking level** are not kept in session state: the toolbox saves them directly to the expert's config (`configs/{expert_id}.yaml`)

### Persistent Storage
- **Chat history**: `chat_history/{expert_id}.json`
- **Image attachments**: `chat_attachments/{expert_id}/` (local only, gitignored)
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
- Rename experts with prefixes (e.g., "0 Python Expert"; names allow only letters, numbers, spaces, `_`, `-` and `.`)
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

- Monitor the context usage on the right of the toolbox below the chat input
- Lower temperature for shorter, focused responses
- Switch to cost-effective providers (DeepSeek) for simple tasks

## Troubleshooting

### Expert Not Responding

**Problem**: No response after sending message

**Solutions**:
1. Check API key is configured (Settings → API Key)
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
