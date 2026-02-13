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
- **💾 Persistent Chat History** - Conversations saved automatically per expert
- **⚙️ Adjustable Temperature** - Control response creativity (0.0-2.0) for each expert
- **🚀 Modern Navigation** - Material Design icons using Streamlit's st.navigation() API
- **📂 File-Based Configuration** - Each expert has its own YAML config for easy management

## Code Hosting

- **GitHub**: [https://github.com/fossler/expertgpts](https://github.com/fossler/expertgpts) (primary)
- **Gitee**: [https://gitee.com/mirzet/expertgpts](https://gitee.com/mirzet/expertgpts) (mirror)

## Pay Only for What You Use: The Economic and Strategic Advantages of API-Based AI Chats

API-based AI chats operate on a **pay-as-you-go (PAYG)** model—meaning you pay **only for actual usage**, not for access. There are no fixed monthly fees, no long-term commitments, and no costs when the service isn't used. This makes PAYG inherently more transparent, flexible, and cost-efficient than traditional subscription models.

### Why PAYG Is Often Significantly Cheaper Than Flat-Rate Subscriptions

**Full Cost Transparency & Control**
Spending scales directly with usage. You decide how much you pay simply by how much you use the system.

**Perfect for Variable Demand**
Whether usage is sporadic or comes in bursts, PAYG adapts instantly. You never overpay during low-usage periods.

**Concrete Cost Example**
Around **180 requests to DeepSeek can cost as little as ~$0.06**. Even with higher-priced APIs like OpenAI—often several times more expensive—PAYG remains economical because **you are billed only when requests are made**.

In contrast, subscription-based AI chats charge the same monthly fee regardless of whether the service is used heavily, lightly, or not at all.

### Combine Providers, Optimize Performance, Reduce Costs

An application that **supports multiple AI providers** unlocks even greater advantages:

- Select the **most cost-effective model** for routine tasks
- Switch to **more powerful models** only when complexity truly requires it
- Avoid vendor lock-in and dynamically balance cost, quality, and speed

This strategy ensures optimal results without unnecessary expense.

### What Can Smaller, Cost-Efficient Models Handle?

For many everyday use cases, lightweight models are more than sufficient, including:

- **Text summarization**
- **Email and short-text drafting**
- **Standard programming questions** (e.g., "How do I write an if-clause in language X?")
- **Concept explanations** (e.g., "What are the advantages of microservices?")

Reserving large, expensive models only for genuinely complex tasks leads to **dramatic cost savings without sacrificing quality**.

### Conclusion

Why pay for an expensive flat-rate AI subscription when an **API-based, multi-provider chat solution** gives you:

- Precise cost control
- Maximum flexibility
- No unused capacity
- Optimal performance per task

With PAYG, **you stay in control—financially and technically—at all times**.


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

**First run?** The app automatically creates 9 example experts and detects your system language.

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
├── lib/                           # Core library (domain-driven structure)
│   ├── llm/                      # LLM client, connection pooling, token management
│   ├── config/                   # Expert config, secrets, app defaults, theme config
│   ├── i18n/                     # Internationalization
│   ├── storage/                  # Chat history, streaming cache
│   ├── ui/                       # Dialogs and UI components
│   └── shared/                   # Constants, helpers, file ops, types, session state
└── locales/ui/*.json             # UI translations (13 languages)
```

**Key Architecture Principles**:
- **Template-Based**: Single template generates all expert pages
- **Multi-Provider Abstraction**: Unified client interface for DeepSeek, OpenAI, Z.AI
- **Clean Architecture**: Expert content in YAML (English), UI in locale files
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

## Why Streamlit and Its Limitations

I chose Streamlit because it makes creating beautiful interfaces remarkably easy, and Streamlit itself actively promotes it for AI and LLM applications ([chat tutorials](https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps), [30 Days of AI Challenge](https://discuss.streamlit.io/t/the-30-days-of-ai-challenge-starts-today/120455)). Since the framework is Python-based, it also gave me an opportunity to delve deeper into Python development. However, I wasn't aware of Streamlit's architectural limitations before starting this project, and they significantly shaped the implementation.

The three biggest challenges are:

1. **No Asynchronicity**: Streamlit doesn't support `async/await`, meaning all LLM streaming requests are blocking. I had to implement a file-based background streaming system with daemon threads just to allow responses to complete when users navigate away—a 250-line solution for what should be a simple async operation.

2. **Execution Model**: Streamlit reruns your entire script from top to bottom on every interaction. This means changing session state doesn't update the UI until you explicitly call `st.rerun()`. ExpertGPTs has 36 such calls—for everything from toggling dialogs to reloading API keys—because the script can't re-evaluate conditionals mid-execution.

3. **State Management Complexity**: Session state doesn't persist across app restarts, and external file changes (configs, API keys) aren't detected automatically. I built a multi-layered state system with manual cache invalidation to work around this.

Would I choose Streamlit again? For data dashboards and simple prototypes, absolutely—it's perfect for those. But for an AI chatbot with real-time streaming, complex state management, and background processing? I'd rather do a rewrite with a modern stack like **React and Bun**, which handle these requirements natively with better performance and developer experience.

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
