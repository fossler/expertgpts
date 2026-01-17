# ExpertGPTs

A multi-expert AI chat application built with Streamlit, providing access to domain-specific AI experts with support for multiple LLM providers, full internationalization, and persistent chat history.

## Overview

ExpertGPTs is a powerful AI chat interface that lets you create and interact with specialized AI experts. Each expert has deep knowledge in specific domains—from Python programming to career coaching—and maintains independent conversation history. Switch between LLM providers (DeepSeek, OpenAI, Z.AI) per expert, customize responses with temperature controls, and enjoy a fully internationalized interface supporting 13 languages.

## Key Features

- **🤖 Multiple Expert Agents** - Chat with domain-specific AI experts, each specialized in different areas
- **🔄 Multi-Provider Support** - Choose between DeepSeek, OpenAI, and Z.AI per expert
- **🌍 Full Internationalization** - 13 languages with automatic detection and AI language response
- **📝 Template-Based Architecture** - Consistent UI/UX across all experts with easy customization
- **🎨 Theme Customization** - Personalize colors and appearance with preset themes
- **🔒 Secure API Key Management** - API keys stored securely with automatic file permissions
- **💾 Persistent Chat History** - Conversations saved automatically per expert
- **⚙️ Adjustable Temperature** - Control response creativity (0.0-2.0) for each expert
- **🚀 Modern Navigation** - Material Design icons using Streamlit's st.navigation() API
- **📂 File-Based Configuration** - Each expert has its own YAML config for easy management

## Quick Start

Get ExpertGPTs up and running in 5 minutes:

```bash
# Clone and navigate
git clone <repository-url>
cd expertgpts

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt  # Development (includes watchdog)
# OR
pip install -r requirements.txt       # Production only

# Run the app
streamlit run app.py
```

**First run?** The app automatically creates 7 example experts and detects your system language.

**Get your API key**: [https://platform.deepseek.com/](https://platform.deepseek.com/)

Set it via **Settings → API Keys** in the app.

**That's it!** Start chatting with experts.

**Detailed setup**: [Installation Guide](docs/getting-started/installation.md)

## Architecture Overview

```
expertgpts/
├── app.py                         # Main entry point with st.navigation()
├── pages/
│   ├── 1000_Home.py              # Home page (permanent)
│   ├── 1001_*.py                 # Expert pages (generated from template)
│   ├── 9998_Settings.py          # Settings page (permanent)
│   └── 9999_Help.py              # Help page (permanent)
├── templates/template.py          # Template for expert pages
├── configs/{expert_id}.yaml       # Expert configurations
├── utils/                         # Business logic modules
│   ├── llm_client.py             # Multi-provider LLM client
│   ├── client_pool.py            # Connection pooling
│   ├── config_manager.py         # Config operations
│   ├── page_generator.py         # Page generation
│   └── ...
└── locales/ui/*.json             # UI translations (13 languages)
```

**Key Architecture Principles**:
- **Template-Based**: Single template generates all expert pages
- **Multi-Provider Abstraction**: Unified client interface for DeepSeek, OpenAI, Z.AI
- **DRY Configuration**: Expert content in YAML (English only), UI in locale files
- **State Management**: Multi-layered session state with persistent storage

**Detailed architecture**: [Architecture Documentation](docs/architecture/overview.md)

## Internationalization

ExpertGPTs supports **13 languages** with automatic detection:

🇺🇸 English | 🇩🇪 German | 🇪🇸 Spanish | 🇫🇷 French | 🇮🇹 Italian | 🇮🇩 Indonesian | 🇲🇾 Malay | 🇵🇹 Portuguese | 🇷🇺 Russian | 🇹🇷 Turkish | 🇨🇳 Simplified Chinese | 🇹🇼 Traditional Chinese | 🇭🇰 Cantonese | 🗣️ Wu Chinese

**How it works**: Language prefix injected at runtime ensures AI responds in your selected language, while expert content remains in English (single source of truth).

**Full guide**: [Internationalization Documentation](docs/internationalization/I18N_GUIDE.md)

## Documentation

### For Users

- **[Quick Start Guide](docs/getting-started/quickstart.md)** - 5-minute setup
- **[Installation Guide](docs/getting-started/installation.md)** - Detailed installation
- **[User Guide](docs/user-guide/basics.md)** - Using experts, navigation, provider selection
- **[Creating Experts](docs/user-guide/creating-experts.md)** - Custom expert creation
- **[Customization](docs/user-guide/customization.md)** - Themes, language, settings
- **[Troubleshooting](docs/reference/troubleshooting.md)** - Common issues

### For Developers

- **[Development Setup](docs/development/setup.md)** - Development environment
- **[Architecture Overview](docs/architecture/overview.md)** - System architecture
- **[Project Structure](docs/development/project-structure.md)** - File organization
- **[Adding Features](docs/development/adding-features.md)** - Feature development guidelines
- **[Testing Guide](docs/development/testing.md)** - Testing documentation

### Technical Reference

- **[Configuration](docs/configuration/overview.md)** - Configuration system
- **[API Providers](docs/api/providers.md)** - LLM provider integration
- **[Template System](docs/architecture/template-system.md)** - Page generation
- **[Scripts Reference](docs/reference/scripts.md)** - Administrative scripts

**Full documentation**: [docs/](docs/)

## Multi-Provider LLM Support

ExpertGPTs integrates with multiple LLM providers through OpenAI-compatible APIs:

| Provider | Default Model | Characteristics |
|----------|---------------|-----------------|
| **DeepSeek** | `deepseek-chat` | Cost-effective, high quality |
| **OpenAI** | `o3-mini` | Advanced reasoning capabilities |
| **Z.AI** | `glm-4.7` | GLM models, Chinese optimization |

**Per-Expert Selection**: Each expert can use a different provider/model. Switch via the sidebar dropdown.

**Connection Pooling**: Client instances cached for ~50% performance improvement.

**API Documentation**: [Provider Reference](docs/api/providers.md)

## Development

### Running the App

```bash
# Standard
streamlit run app.py

# With enhanced file watching (faster during development)
streamlit run app.py --server.fileWatcherType=watchdog
```

### Running Tests

```bash
# Run all tests
./scripts/run_tests.sh

# Direct pytest
pytest -v

# With coverage
pytest --cov=utils --cov-report=html
```

### Adding Features

**Modify Expert Pages**: Edit `templates/template.py`, then run `echo "yes" | python3 scripts/reset_application.py`

**Modify Home/Settings/Help**: Edit `pages/1000_Home.py`, `pages/9998_Settings.py`, or `pages/9999_Help.py` directly

**Development Guide**: [Adding Features Documentation](docs/development/adding-features.md)

## License

This project is open source and available under the Apache License 2.0.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [DeepSeek API](https://www.deepseek.com/), [OpenAI API](https://openai.com/), and [Z.AI](https://z.ai/)
- Inspired by OpenAI's GPTs explore functionality
- Developed with [Z.AI](https://z.ai/subscribe?ic=JGTYCX7ZO7) - Advanced AI platform

## Support

For issues, questions, or contributions, visit the [GitHub repository](https://github.com/fossler/expertgpts).

---

## ☕ Buy Me a Coffee

If you find this project helpful and would like to support its development, consider buying me a coffee!

<a href="https://www.buymeacoffee.com/MirzetKadic" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
