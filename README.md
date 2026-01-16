# ExpertGPTs

A multi-expert AI chat application built with Streamlit and powered by the DeepSeek API. ExpertGPTs provides access to multiple domain-specific expert AI agents, each specialized in different fields.

## Features

- **Multiple Expert Agents**: Chat with domain-specific AI experts, each specialized in different areas
- **Custom Expert Creation**: Easily create your own expert agents with custom domains and descriptions
- **Modern Navigation**: Material Design icons in navigation using Streamlit's `st.navigation()` API
- **Wide Mode**: Expansive content layout enabled by default
- **Theme Customization**: Customize colors through the Settings page with preset themes
- **Secure Secrets Management**: API keys stored securely in `.streamlit/secrets.toml`
- **File-Based Configuration**: Each expert has its own configuration file for easy management
- **Template-Based Pages**: Expert pages are generated from a master template
- **Chat History**: Maintain conversation context throughout your session
- **Adjustable Temperature**: Control response creativity and focus for each expert

## Architecture

```
expertgpts/
├── app.py                         # Main entry point with st.navigation()
├── pages/
│   ├── 1000_Home.py              # Home page (permanent, committed to git)
│   ├── 1001_Python_Expert.py     # Expert pages (generated from template)
│   ├── 1002_Data_Scientist.py
│   └── ...
│   └── 9999_Settings.py          # Settings page (permanent, committed to git)
├── templates/
│   └── template.py               # Template for expert pages only
├── configs/
│   └── {expert_id}.yaml          # Config files for each expert
├── utils/
│   ├── config_manager.py         # Config file operations
│   ├── page_generator.py         # Page generation logic
│   ├── deepseek_client.py        # DeepSeek API wrapper
│   ├── secrets_manager.py        # Streamlit secrets management
│   ├── config_toml_manager.py    # Theme configuration management
│   └── app_defaults_manager.py   # User preferences management (LLM defaults, language)
├── .streamlit/
│   ├── secrets.toml              # API keys and secrets (gitignored)
│   ├── secrets.toml.example      # Template for secrets file
│   ├── config.toml               # Theme settings (gitignored)
│   ├── config.toml.example       # Template for theme settings
│   ├── app_defaults.toml         # User preferences (gitignored)
│   └── app_defaults.toml.example # Template for app defaults
├── requirements.txt
├── scripts/                      # Administrative scripts
│   ├── setup.py                 # Script to set up the application
│   └── reset_application.py     # Script to reset application
└── README.md
```

## Internationalization (i18n)

ExpertGPTs supports **13 languages** with automatic language detection and runtime language injection.

### Supported Languages

- 🇺🇸 **English** (en)
- 🇩🇪 **German** (Deutsch) (de)
- 🇪🇸 **Spanish** (Español) (es)
- 🇫🇷 **French** (Français) (fr)
- 🇮🇹 **Italian** (Italiano) (it)
- 🇮🇩 **Indonesian** (Bahasa Indonesia) (id)
- 🇲🇾 **Malay** (Bahasa Melayu) (ms)
- 🇵🇹 **Portuguese** (Português) (pt)
- 🇷🇺 **Russian** (Русский) (ru)
- 🇹🇷 **Turkish** (Türkçe) (tr)
- 🇨🇳 **Simplified Chinese** (简体中文) (zh-CN)
- 🇹🇼 **Traditional Chinese** (繁體中文) (zh-TW)
- 🇭🇰 **Cantonese** (粵語) (yue)
- 🗣️ **Wu Chinese** (文言文) (wyw)

### How It Works

ExpertGPTs uses a **clean three-layer architecture** for internationalization:

```
┌─────────────────────────────────────────────────────────┐
│  1. STORAGE LAYER (configs/*.yaml)                      │
│  Expert content in English - Single Source of Truth     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  2. TRANSLATION LAYER (locales/ui/*.json)               │
│  UI translations ONLY - Buttons, labels, messages       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  3. RUNTIME LAYER (template.py, i18n.py)                │
│  Language prefix injection: "Respond in German (Deutsch)"│
└─────────────────────────────────────────────────────────┘
```

**Key Features:**

1. **Auto-Detection**: First run detects system language automatically
2. **Manual Selection**: Users can change language in Settings
3. **Persistent Preference**: Language choice saved to `.streamlit/app_defaults.toml`
4. **AI Language Respect**: Experts automatically respond in user's language
5. **No Duplication**: Expert content exists ONLY in YAML configs (not in locales)

### Language Preference

The app stores your language preference in `.streamlit/app_defaults.toml`:

```toml
[llm]
provider = "deepseek"
model = "deepseek-chat"
thinking_level = "none"

[language]
code = "de"  # German
```

**First Run:**
- App auto-detects system language
- Saves detected language to `app_defaults.toml`
- Starts app in detected language

**Manual Change:**
- Go to Settings → Language
- Select your preferred language
- Preference saved to `app_defaults.toml`
- App restarts in selected language

### Creating Multilingual Experts

You can create experts in ANY language:

1. **Expert Name**: Use name in your language (e.g., "Datenexperte")
2. **Description**: Write description in your language
3. **System Prompt**: Write prompt in your language
4. **AI Response**: Expert will respond in the user's selected language

**Example (German):**
```yaml
expert_name: Datenexperte
description: Experte für Datenanalyse und Visualisierung
system_prompt: |
  Sie sind Datenexperte, spezialisiert auf Datenanalyse...
```

### Language Prefix Injection

When you chat with an expert, the app automatically adds a language prefix to the system prompt:

```
You must respond in German (Deutsch).

You are Python Expert, a domain-specific expert AI assistant.
Expert in Python programming, software development...
```

This ensures AI responds in the user's preferred language while maintaining expert context.

### File Structure

```
locales/ui/
├── en.json         # English UI translations (buttons, labels, messages)
├── de.json         # German UI translations
├── es.json         # Spanish UI translations
├── fr.json         # French UI translations
└── ... (10 more language files)
```

**Important:** Locale files contain ONLY UI translations, not expert content.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd expertgpts
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:

   **For development (includes watchdog for faster file watching):**
   ```bash
   pip install -r requirements-dev.txt
   ```

   **For production only:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create example expert agents** (optional):
   ```bash
   python3 scripts/setup.py
   ```

This will create 7 example experts:
- Python Expert
- Data Scientist
- Writing Assistant
- Linux System Admin
- Career Coach
- Translation Expert
- Spell Checker

## Usage

### Running the Application

Start the application with:
```bash
streamlit run app.py
```

**First run?** The app will automatically create 7 example expert agents on first launch.

The app will open in your browser at `http://localhost:8501`

**Note**: ExpertGPTs uses Streamlit's modern `st.navigation()` API with Material Design icons for a polished user experience. Wide mode is enabled by default for maximum content visibility.

### Setting Your API Key

ExpertGPTs uses Streamlit's secure secrets management system. You can set your DeepSeek API key in two ways:

**Option 1: Via Settings Page (Recommended)**
1. Navigate to **Settings** in the app
2. Go to the **API Key** tab
3. Enter your DeepSeek API key
4. Click **"Save API Key"**
5. The key will be automatically saved to `.streamlit/secrets.toml`

**Option 2: Manual Configuration**
1. Copy the example file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
2. Edit `.streamlit/secrets.toml` and add your API key:
   ```toml
   DEEPSEEK_API_KEY = "your_actual_api_key_here"
   ```

Get your API key from [https://platform.deepseek.com/](https://platform.deepseek.com/)

> **Security Note**: The `.streamlit/secrets.toml` file is gitignored and will never be committed to version control. The file is automatically set to 600 permissions (read/write for owner only) when created or modified.

### Customizing the Theme

ExpertGPTs allows you to customize the app's appearance through the Settings page:

1. Go to **Settings** → **General** tab
2. Use the color pickers to adjust:
   - **Buttons and interactive Elements**: Color for buttons and interactive elements
   - **Background Color**: Main background color
   - **Secondary Background**: Sidebar and secondary areas
   - **Text Color**: Main text color
3. Click **"Apply Changes"** to save your theme

**Preset Themes:**
- 🎨 **Light Themes**: Red, Blue, Green, Purple
- 🌙 **Dark Themes**: Dark Blue, Dark Gray
- Click any preset to instantly apply the theme

**Default Theme:**
The app comes with a modern Indigo theme by default:
- Buttons: Indigo (#6366F1)
- Background: White (#FFFFFF)
- Sidebar: Light Gray (#F3F4F6)
- Text: Dark Gray (#1F2937)

The theme settings are automatically saved to `.streamlit/config.toml` with secure permissions.

### Chatting with Experts

1. **Select an Expert**: Choose an expert from the navigation menu in the sidebar
2. **Start Chatting**: Type your question or prompt in the chat input
3. **Continue Conversation**: The expert maintains context throughout your session

### Creating New Expert Agents

1. Navigate to the **Home** page (the "Add Chat" button is only available there)
2. Click the **"➕ Add Chat"** button in the sidebar
3. Fill in the form:
   - **Expert Name**: A descriptive name for the expert (e.g., "Legal Advisor")
   - **Agent Description**: Describe the expert's domain and capabilities
   - **Temperature**: Set response creativity (0.0 = focused, 2.0 = creative)
   - **Custom System Prompt** (optional): Provide a custom system prompt
4. Click **"Create Expert"**
5. You'll be automatically navigated to your new expert page and can start chatting immediately!

## Configuration

Each expert agent is configured via a YAML file in the `configs/` directory. Example configuration:

```yaml
expert_id: "1001_python_expert"
expert_name: "Python Expert"
description: "Expert in Python programming, software development..."
temperature: 0.7
system_prompt: |
  You are Python Expert, a domain-specific expert AI assistant.

  ## Your Expertise
  Expert in Python programming, software development, debugging, and best practices...

  ## Guidelines
  - Provide accurate, expert-level information in your domain
  - If you're unsure about something, acknowledge it honestly
  - Use clear, professional language appropriate for your domain
created_at: "2025-12-30T22:13:25.123456"
metadata:
  version: "1.0"
  model: "deepseek-chat"
```

## Customization

### Modifying the Page Template

The `templates/template.py` file defines the structure of all expert pages. You can modify this template to change the UI/UX for all experts.

### Changing System Prompts

You can customize system prompts in two ways:

1. **Auto-generated**: The system automatically generates prompts from the description
2. **Custom**: Use the "Advanced: Custom System Prompt" field when creating an expert

### Adding New Features

The modular structure makes it easy to add new features:

- **ConfigManager** (`utils/config_manager.py`): Manage expert configurations
- **PageGenerator** (`utils/page_generator.py`): Generate new expert pages
- **DeepSeekClient** (`utils/deepseek_client.py`): Handle API interactions
- **SecretsManager** (`utils/secrets_manager.py`): Manage Streamlit secrets file
- **ConfigTomlManager** (`utils/config_toml_manager.py`): Manage theme configuration

## API Integration

ExpertGPTs uses the DeepSeek API, which is compatible with the OpenAI API format. The app uses the official OpenAI Python client with a custom base URL.

**API Endpoint**: `https://api.deepseek.com`
**Model**: `deepseek-chat`

For more information on the DeepSeek API, see the [official documentation](https://api-docs.deepseek.com/).

## Best Practices

### Creating Effective Experts

1. **Clear Descriptions**: Provide detailed, specific descriptions of the expert's domain
2. **Appropriate Temperature**:
   - 0.0-0.7: For technical, factual topics (e.g., coding, mathematics)
   - 0.7-1.3: For general advice and explanations (default)
   - 1.3-2.0: For creative tasks (e.g., brainstorming, creative writing)
3. **Custom System Prompts**: For advanced use cases, craft custom prompts that define the expert's behavior precisely

### Security Considerations

- **API Keys**: Never commit API keys to version control
- **Streamlit Secrets**: API keys are stored in `.streamlit/secrets.toml` which is gitignored
- **UI Management**: Use the Settings page to manage API keys securely
- **Automatic File Permissions**: The app automatically sets 600 permissions (owner read/write only) on `secrets.toml` when created or modified
- **Manual Verification**: You can verify permissions with `ls -la .streamlit/secrets.toml` (should show `-rw-------`)

## Troubleshooting

### Common Issues

**Issue**: "Configuration not found" error
- **Solution**: Run `python3 scripts/setup.py` to create example experts

**Issue**: API key errors
- **Solution**: Verify your DeepSeek API key is valid and has sufficient credits

**Issue**: New expert not appearing in navigation
- **Solution**: The app should auto-navigate to newly created experts. If it doesn't, wait a moment for the page to be discovered.

**Issue**: Import errors
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

## Development

### Project Structure

- **app.py**: Main application entry point using `st.navigation()` for modern navigation
- **templates/**: Template file for expert pages only
- **pages/**: Home (1000) and Settings (9999) are permanent; expert pages (1001+) are auto-generated
- **utils/**: Shared utilities and business logic
- **configs/**: YAML configuration files for each expert

### Adding New Features

1. **New Utility**: Add to `utils/` directory
2. **UI Changes for Experts**: Modify `templates/template.py`, then run `echo "yes" | python3 scripts/reset_application.py` to regenerate expert pages
3. **UI Changes for Home/Settings**: Edit directly in `pages/1000_Home.py` or `pages/9999_Settings.py` (permanent files)
4. **New Expert Pages**: Generate via Settings UI or programmatically using `PageGenerator`

### Template-Based Architecture

ExpertGPTs uses a template-based architecture for expert pages:

- **Home & Settings**: Permanent files in `pages/` (committed to git)
- **Expert Pages**: Generated from `templates/template.py` with placeholders replaced
- **Numbering**: Home (1000) → Experts (1001+) → Settings (9999)

When modifying the expert template:
1. Edit `templates/template.py`
2. Run `echo "yes" | python3 scripts/reset_application.py` to regenerate all expert pages
3. Changes will be reflected across all generated expert pages

### Testing

The project includes automated tests using pytest. For detailed testing instructions, see [Testing Guide](docs/testing.md).

Quick test run:
```bash
./scripts/run_tests.sh
```

### Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is open source and available under the Apache License 2.0.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [DeepSeek API](https://www.deepseek.com/)
- Inspired by OpenAI's GPTs explore functionality
- Developed with [Z.AI](https://z.ai/subscribe?ic=JGTYCX7ZO7) - Advanced AI platform for intelligent context engineering

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/fossler/expertgpts).
