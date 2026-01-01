# ExpertGPTs

A multi-expert AI chat application built with Streamlit and powered by the DeepSeek API. ExpertGPTs provides access to multiple domain-specific expert AI agents, each specialized in different fields.

## Features

- **Multiple Expert Agents**: Chat with domain-specific AI experts, each specialized in different areas
- **Custom Expert Creation**: Easily create your own expert agents with custom domains and descriptions
- **Streamlit-Powered**: Built with Streamlit for a clean, responsive interface
- **File-Based Configuration**: Each expert has its own configuration file for easy management
- **Template-Based Pages**: New experts are generated from a consistent template
- **Chat History**: Maintain conversation context throughout your session
- **Adjustable Temperature**: Control response creativity and focus for each expert

## Architecture

```
expertgpts/
├── Home.py                   # Main landing page
├── pages/
│   ├── 1_Python_Expert.py    # Auto-generated expert pages
│   └── ...
├── templates/
│   └── template.py           # Template for all expert pages
├── configs/
│   └── {expert_id}.yaml      # Config files for each expert
├── utils/
│   ├── config_manager.py     # Config file operations
│   ├── page_generator.py     # Page generation logic
│   └── deepseek_client.py    # DeepSeek API wrapper
├── requirements.txt
├── setup_examples.py         # Script to create example experts
└── README.md
```

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
   python3 setup_examples.py
   ```

This will create 5 example experts:
- Python Expert
- Data Scientist
- Writing Assistant
- Linux System Admin
- Career Coach

## Usage

### Running the Application

Start the application with:
```bash
streamlit run Home.py
```

The app will open in your browser at `http://localhost:8501`

### Setting Your API Key

You can set your DeepSeek API key in two ways:

**Option 1: Using .env file (Recommended)**
1. Copy `.env.example` to `.env`
2. Add your API key: `DEEPSEEK_API_KEY=your_key_here`
3. The app will automatically load it on startup

**Option 2: Manual Input**
1. Get a DeepSeek API key from [https://platform.deepseek.com/](https://platform.deepseek.com/)
2. Enter your API key in the sidebar under "Configuration"

> **Note**: The .env file method is more secure and convenient. The .env file is already excluded from version control.

### Chatting with Experts

1. **Select an Expert**: Choose an expert from the navigation menu in the sidebar
2. **Start Chatting**: Type your question or prompt in the chat input
3. **Continue Conversation**: The expert maintains context throughout your session

### Creating New Expert Agents

1. Click the **"Add Chat"** button in the sidebar
2. Fill in the form:
   - **Chat Name**: A descriptive name for the expert (e.g., "Legal Advisor")
   - **Agent Description**: Describe the expert's domain and capabilities
   - **Temperature**: Set response creativity (0.0 = focused, 2.0 = creative)
   - **Custom System Prompt** (optional): Provide a custom system prompt
3. Click **"Create Expert"**
4. You'll be automatically navigated to your new expert page and can start chatting immediately!

## Configuration

Each expert agent is configured via a YAML file in the `configs/` directory. Example configuration:

```yaml
expert_id: "20251230_221325_python_expert"
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
- **Environment Variables**: Consider using `DEEPSEEK_API_KEY` environment variable
- **File Permissions**: Ensure config files have appropriate permissions

## Troubleshooting

### Common Issues

**Issue**: "Configuration not found" error
- **Solution**: Run `python3 setup_examples.py` to create example experts

**Issue**: API key errors
- **Solution**: Verify your DeepSeek API key is valid and has sufficient credits

**Issue**: New expert not appearing in navigation
- **Solution**: The app should auto-navigate to newly created experts. If it doesn't, wait a moment for the page to be discovered.

**Issue**: Import errors
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

## Development

### Project Structure

- **app.py**: Main application entry point, landing page, and "Add Chat" functionality
- **pages/template.py**: Template used to generate all expert pages
- **utils/**: Shared utilities and business logic
- **configs/**: YAML configuration files for each expert

### Adding New Features

1. **New Utility**: Add to `utils/` directory
2. **UI Changes**: Modify `pages/template.py` for all experts, or specific expert pages
3. **New Pages**: Create in `pages/` directory with numeric prefix for ordering

### Testing

The project includes automated tests using pytest. For detailed testing instructions, see [Testing Guide](docs/testing.md).

Quick test run:
```bash
./run_tests.sh
```

### Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [DeepSeek API](https://www.deepseek.com/)
- Inspired by OpenAI's GPTs explore functionality

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/yourusername/expertgpts).
