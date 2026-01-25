# First Use Guide

This guide walks you through your first time using ExpertGPTs, covering all the essential setup and features you'll need to get started.

## Running the Application

Start the application with:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

**First Run?** The app will automatically create 9 example expert agents on first launch.

## Initial Setup

### 1. Language Selection

ExpertGPTs supports **13 languages** with automatic detection.

**What happens on first run**:
1. The app detects your system language automatically
2. Saves it to `.streamlit/app_defaults.toml`
3. Starts the app in your detected language

**Supported languages**:
- 🇺🇸 English (en)
- 🇩🇪 German (Deutsch) (de)
- 🇪🇸 Spanish (Español) (es)
- 🇫🇷 French (Français) (fr)
- 🇮🇹 Italian (Italiano) (it)
- 🇮🇩 Indonesian (Bahasa Indonesia) (id)
- 🇲🇾 Malay (Bahasa Melayu) (ms)
- 🇵🇹 Portuguese (Português) (pt)
- 🇷🇺 Russian (Русский) (ru)
- 🇹🇷 Turkish (Türkçe) (tr)
- 🇨🇳 Simplified Chinese (简体中文) (zh-CN)
- 🇹🇼 Traditional Chinese (繁體中文) (zh-TW)
- 🇭🇰 Cantonese (粵語) (yue)
- 🗣️ Wu Chinese (文言文) (wyw)

**To change language manually**:
1. Navigate to **Settings** → **General** tab
2. Select your preferred language from the dropdown
3. Click outside the selector to save
4. The app restarts in the selected language

### 2. API Key Configuration

ExpertGPTs requires an API key to function. You can set it up in two ways:

#### Option 1: Via Settings Page (Recommended)

1. Navigate to **Settings** in the app
2. Go to the **API Keys** tab
3. Enter your DeepSeek API key
4. Click **"Save API Key"**
5. The key will be automatically saved to `.streamlit/secrets.toml`

#### Option 2: Manual Configuration

1. Copy the example file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` and add your API key:
   ```toml
   DEEPSEEK_API_KEY = "your_actual_api_key_here"
   ```

**Get your API key from**: [https://platform.deepseek.com/](https://platform.deepseek.com/)

> **Security Note**: The `.streamlit/secrets.toml` file is gitignored and will never be committed to version control. The file is automatically set to 600 permissions (read/write for owner only) when created or modified.

## Understanding the Interface

### Navigation

ExpertGPTs uses Streamlit's modern navigation with Material Design icons:

- **:material/home:** Home - Expert list and Add Chat button
- **:material/psychology:** Expert Pages - Your custom expert agents
- **:material/settings:** Settings - Configure API keys, themes, language, and defaults

### Default Experts

On first run, 9 example experts are created:

| Expert | Specialization |
|--------|---------------|
| **Helpful Assistant** | Knowledgeable, reliable, and supportive generalist assistant for accurate and practical information |
| **Email Assistant** | Email replies based on keywords and sender tone |
| **Translation Expert EN-DE** | English-German translation specialist |
| **Spell Checker** | Multilingual spell checking with change summaries |
| **Copywriter** | Marketing, advertising, SEO, and branding content creation |
| **Text Summarizer** | Text summarization in multiple formats |
| **Data Scientist** | Data analysis, visualization, statistics |
| **Linux System Engineer** | Linux system administration and engineering |
| **Python Expert** | Python programming, software development, debugging |

### Layout

- **Sidebar**: Navigation menu with expert list
- **Main Content**: Chat interface with expert
- **Settings Panel**: Configuration options (when on Settings page)

## Your First Chat

### Selecting an Expert

1. Click on any expert in the sidebar navigation
2. The expert's page loads with a welcome message
3. You'll see the chat interface with a text input at the bottom

### Sending Your First Message

1. Type your question or prompt in the chat input
2. Press **Enter** or click the send button
3. The expert responds maintaining conversation context

### Conversation Features

- **Context Awareness**: The expert maintains context throughout your session
- **Persistent History**: Conversations are saved automatically
- **Per-Expert History**: Each expert has its own chat history
- **Multi-Language Responses**: Experts respond in your selected language

## Customizing Your Experience

### Provider Selection

ExpertGPTs supports multiple LLM providers:

- **DeepSeek** (default) - Cost-effective, high-quality
- **OpenAI** - GPT models with reasoning
- **Z.AI** - GLM models

Switch providers per expert using the dropdown in the sidebar.

### Model Selection

Each provider offers multiple models:

- **DeepSeek**: `deepseek-chat`, `deepseek-reasoner`
- **OpenAI**: `o3-mini`, `gpt-4o`, `gpt-4o-mini`
- **Z.AI**: `glm-4.7`, `glm-4.7-thinking`

### Temperature Adjustment

Control response creativity:
- **Lower (0.0-0.3)**: Focused, factual responses
- **Medium (0.4-0.7)**: Balanced (recommended for most use cases)
- **Higher (0.8-2.0)**: Creative, exploratory responses

### Theme Customization

Personalize the app's appearance:

1. Go to **Settings** → **General** tab
2. Use color pickers to adjust:
   - **Buttons and Interactive Elements**
   - **Background Color**
   - **Secondary Background** (sidebar)
   - **Text Color**
3. Click **"Apply Changes"** to save

**Preset Themes**: Quick access to Light (Red, Blue, Green, Purple) and Dark (Dark Blue, Dark Gray) themes.

## Creating Your First Expert

1. Navigate to the **Home** page (the "Add Chat" button is only available there)
2. Click the **"➕ Add Chat"** button in the sidebar
3. Fill in the form:
   - **Expert Name**: A descriptive name (e.g., "Legal Advisor")
   - **Agent Description**: Describe the expert's domain and capabilities
   - **Temperature**: Set response creativity (default: 0.7)
   - **Custom System Prompt** (optional): Provide a custom system prompt
4. Click **"Create Expert"**
5. You'll be automatically navigated to your new expert page

**Example Expert Creation**:
- **Name**: "SQL Expert"
- **Description**: "Expert in SQL database design, query optimization, and database administration"
- **Temperature**: 0.5 (balanced focus and creativity)

### Multilingual Experts

You can create experts in any language! For example:

- **German Expert**: Name "Datenexperte" with German description
- **Chinese Expert**: Name "数据专家" with Chinese description
- **French Expert**: Name "Expert Français" with French description

The expert will automatically respond in the user's selected language, regardless of the language used to create it.

## Common First-Time Tasks

### Test Different Experts

Try asking the same question to different experts to see their specialized responses:

- Ask **Python Expert** about a coding problem
- Ask **Copywriter** to improve your marketing content
- Ask **Translation Expert EN-DE** to translate text

### Adjust Temperature

Experiment with temperature settings to understand how it affects responses:

1. Ask a creative question with low temperature (0.2)
2. Ask the same question with high temperature (1.5)
3. Compare the responses

### Create a Custom Expert

Create an expert for your specific use case:

- **Work-related**: Project Management, HR, Finance
- **Hobby**: Cooking, Gardening, Music
- **Learning**: History, Science, Philosophy

## Understanding Chat History

### Where History is Stored

Chat history is stored in `chat_history/{expert_id}.json` files.

### History Limits

- **File size limit**: 1MB per expert
- **Auto-trimming**: Old messages are removed when limit is exceeded
- **Per-expert**: Each expert has independent history

### Clearing History

To clear chat history:
1. Delete the corresponding `chat_history/{expert_id}.json` file
2. Or restart the conversation using the chat interface

## Getting Help

### Troubleshooting

If you encounter issues:

- **"Configuration not found"**: Run `python3 scripts/setup.py` to create example experts
- **API key errors**: Verify your API key is valid and has sufficient credits
- **Expert not appearing**: Check that the expert page exists in `pages/` directory
- **Import errors**: Ensure dependencies are installed: `pip install -r requirements.txt`

### Documentation

- **[Quick Start Guide](quickstart.md)** - Fast setup reference
- **[Installation Guide](installation.md)** - Detailed installation instructions
- **[User Guide](../user-guide/basics.md)** - Comprehensive usage documentation
- **[Troubleshooting Guide](../reference/troubleshooting.md)** - Common issues and solutions

### Community Support

- Visit the [GitHub repository](https://github.com/fossler/expertgpts)
- Open an issue with your error message and environment details

## Next Steps

Now that you're familiar with the basics:

1. **[Learn expert creation](../user-guide/creating-experts.md)** - Create advanced custom experts
2. **[Explore customization](../user-guide/customization.md)** - Customize themes and settings
3. **[Understand architecture](../architecture/overview.md)** - Learn how the system works
4. **[Development setup](../development/setup.md)** - Start contributing

---

**Back to**: [Documentation Home](../README.md) | [Quick Start](quickstart.md)
