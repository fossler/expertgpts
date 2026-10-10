# Quick Start Guide

Get ExpertGPTs up and running in 5 minutes!

## Prerequisites

- Python 3.14+ installed
- uv (Python package manager) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- An API key for at least one provider: DeepSeek ([Get one here](https://platform.deepseek.com/)), OpenAI, Z.AI or KIMI

## Installation

**1. Install uv (if not already installed):**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2. Clone the repository and run the application:**

```bash
git clone <repository-url>
cd expertgpts
uv run streamlit run app.py
```

The app will open at `http://localhost:8501`

> **Note**: uv automatically manages dependencies - no need to manually install packages!

## First Run Setup

### Step 1: Choose Your Language

On first run, the app auto-detects your system language.

- **To change**: Go to **Settings** → **General** tab
- **Supported**: 14 languages including English, German, Spanish, French, Chinese, and more
- Your preference is saved and persists across app restarts

### Step 2: Set Up Your API Key

Navigate to **Settings** → **API Key** tab:

1. Select the LLM provider (DeepSeek, OpenAI, Z.AI or KIMI)
2. Enter your API key and click **"Save API Key"**
3. The key is automatically saved to `.streamlit/secrets.toml` with secure permissions

**Get a DeepSeek API key**: [https://platform.deepseek.com/](https://platform.deepseek.com/) (the default provider for new experts)

### Step 3: Select an Expert

Click on any expert in the navigation menu:
- **Helpful Assistant** - Knowledgeable, reliable generalist assistant for accurate information
- **Email Assistant** - Email replies based on keywords and sender tone
- **Translation Expert EN-DE** - English-German translation specialist
- **Spell Checker** - Multilingual spell checking with change summaries
- **Copywriter** - Marketing, advertising, SEO, and branding content
- **Text Summarizer** - Text summarization in multiple formats
- **Data Scientist** - Data analysis and visualization
- **Linux System Engineer** - Linux system administration and engineering
- **Python Expert** - Python programming help

### Step 4: Start Chatting

Type your question in the chat input and get expert responses!

Below the chat input, the chat toolbox lets you attach files or images (vision models only), use voice input, clear the chat history, check the context usage, and switch the model, thinking mode and temperature.

**Features you'll love**:
- Multi-language support with 14 languages
- Automatic language detection
- Modern navigation with Material Design icons
- Wide mode enabled by default
- Expert pages generated from templates for consistency

## Creating Your Own Expert

Create custom experts for any domain in seconds:

1. Navigate to the **Home** page
2. Click **"➕ Add Chat"** in the sidebar
3. Fill in the details:
   - **LLM Provider & Model**: provider, model, thinking mode and temperature (default 1.0)
   - **Expert Name**: e.g., "Legal Advisor" (letters A-Z, numbers, spaces, `_`, `-`, `.`)
   - **Agent Description**: What this expert specializes in
4. Click **"Create Expert"**
5. You'll automatically navigate to your new expert and can start chatting immediately!

**Multilingual Experts**: You can describe experts in any language! The expert will automatically respond in the user's selected language. For example, create a "Datenexperte" (Data Expert) in German, and it will respond in German when the user has German selected.

> **Note**: The "Add Chat" button is available in the Home page sidebar; you can also use **"➕ Add new Chat"** in **Settings** → **Expert Management**

## Temperature Guide

Choose the right temperature for your use case:

| Temperature | Style | Best For |
|-------------|-------|----------|
| **0.0 - 0.3** | Highly focused, deterministic | Coding, mathematics, factual answers |
| **0.4 - 0.7** | Balanced, informative | General advice, explanations (default) |
| **0.8 - 1.2** | Creative, exploratory | Brainstorming, analysis |
| **1.3 - 2.0** | Highly creative | Creative writing, ideation |

> **Provider limits**: Z.AI accepts at most 1.0, DeepSeek ignores the temperature while thinking is enabled, OpenAI models are fixed at 1.0, and some KIMI models use a fixed temperature.

## Quick Troubleshooting

**App won't start?**
```bash
# Make sure you're using uv run
uv run streamlit run app.py
```

**uv not found?**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**API errors?**
- Verify the API key of the expert's provider is valid
- Check that you have sufficient API credits

**Import errors?**
```bash
# Sync dependencies
uv sync
```

## Next Steps

- **[Detailed Installation Guide](installation.md)** - Complete installation instructions
- **[First Use Guide](first-use.md)** - Learn all the basics
- **[User Guide](../user-guide/basics.md)** - Comprehensive usage documentation
- **[Creating Experts Guide](../user-guide/creating-experts.md)** - Advanced expert creation

## Support

For issues or questions, visit the [GitHub repository](https://github.com/fossler/expertgpts).

---

**Back to**: [Documentation Home](../README.md) | [Installation](installation.md)
