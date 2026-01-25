# Quick Start Guide

Get ExpertGPTs up and running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- pip (Python package installer)
- A DeepSeek API key ([Get one here](https://platform.deepseek.com/))

## Installation

**1. Install dependencies:**

```bash
# For development (includes watchdog for faster reloading)
pip install -r requirements-dev.txt

# For production only
pip install -r requirements.txt
```

**2. Run the application:**

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## First Run Setup

### Step 1: Choose Your Language

On first run, the app auto-detects your system language.

- **To change**: Go to **Settings** → **General** tab
- **Supported**: 13 languages including English, German, Spanish, French, Chinese, and more
- Your preference is saved and persists across app restarts

### Step 2: Set Up Your API Key

Navigate to **Settings** → **API Key** tab:

1. Enter your DeepSeek API key
2. Click **"Save API Key"**
3. The key is automatically saved to `.streamlit/secrets.toml` with secure permissions

**Get your API key**: [https://platform.deepseek.com/](https://platform.deepseek.com/)

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

**Features you'll love**:
- Multi-language support with 13 languages
- Automatic language detection
- Modern navigation with Material Design icons
- Wide mode enabled by default
- Expert pages generated from templates for consistency

## Creating Your Own Expert

Create custom experts for any domain in seconds:

1. Navigate to the **Home** page
2. Click **"➕ Add Chat"** in the sidebar
3. Fill in the details:
   - **Name**: e.g., "Legal Advisor" (can be in any language!)
   - **Description**: What this expert specializes in
   - **Temperature**: 0.7 (balanced) or customize
4. Click **"Create Expert"**
5. You'll automatically navigate to your new expert and can start chatting immediately!

**Multilingual Experts**: You can create experts in any language! The expert will automatically respond in the user's selected language. For example, create a "Datenexperte" (Data Expert) in German, and it will respond in German when the user has German selected.

> **Note**: The "Add Chat" button is only available on the Home page sidebar

## Temperature Guide

Choose the right temperature for your use case:

| Temperature | Style | Best For |
|-------------|-------|----------|
| **0.0 - 0.3** | Highly focused, deterministic | Coding, mathematics, factual answers |
| **0.4 - 0.7** | Balanced, informative | General advice, explanations (default) |
| **0.8 - 1.2** | Creative, exploratory | Brainstorming, analysis |
| **1.3 - 2.0** | Highly creative | Creative writing, ideation |

## Quick Troubleshooting

**App won't start?**
```bash
# Ensure dependencies are installed
pip install -r requirements.txt
```

**API errors?**
- Verify your DeepSeek API key is valid
- Check that you have sufficient API credits

**Import errors?**
- Make sure you're running from the project root directory
- Check that virtual environment is activated: `source .venv/bin/activate`

## Next Steps

- **[Detailed Installation Guide](installation.md)** - Complete installation instructions
- **[First Use Guide](first-use.md)** - Learn all the basics
- **[User Guide](../user-guide/basics.md)** - Comprehensive usage documentation
- **[Creating Experts Guide](../user-guide/creating-experts.md)** - Advanced expert creation

## Support

For issues or questions, visit the [GitHub repository](https://github.com/fossler/expertgpts).

---

**Back to**: [Documentation Home](../README.md) | [Installation](installation.md)
