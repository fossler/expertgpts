# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ExpertGPTs is a multi-expert AI chat application built with Streamlit, powered by the DeepSeek API. It uses a **template-based architecture** where each domain-specific expert agent is generated from a single template, with behavior controlled by YAML configuration files.

## Key Architecture Concepts

### Template-Based Page Generation
- **All expert pages** inherit from `templates/template.py`
- **PageGenerator** creates numbered Python files (e.g., `1_Python_Expert.py`) from the template
- Placeholders `{{EXPERT_ID}}` and `{{EXPERT_NAME}}` are replaced during generation
- **Never manually edit expert pages** - changes will be lost when regenerated
- To modify all experts, edit `templates/template.py` instead

### Expert Configuration System
Each expert has a corresponding YAML config file in `configs/`:
- **Format**: `{timestamp}_{safe_name}.yaml`
- **Contains**: expert_id, expert_name, description, temperature, system_prompt, metadata
- **System prompts** are auto-generated from description if not provided
- Config is loaded at runtime via `ConfigManager.load_config()`

### Session State Architecture
Critical pattern for expert isolation:
- **Chat history per expert**: `st.session_state[f"messages_{EXPERT_ID}"]` - prevents cross-contamination
- **Shared API key**: `st.session_state.deepseek_api_key` - available across all experts
- **Navigation state**: `st.session_state.pending_expert_page` - for auto-navigation after creation

### Streamlit Multi-Page Pattern
- Streamlit automatically discovers Python files in `pages/` directory
- Pages are ordered by filename prefix (`1_`, `2_`, `3_`, etc.)
- New pages require `st.rerun()` to be discovered
- Navigation happens via `st.switch_page("pages/filename.py")`

### DeepSeek API Integration
- Uses OpenAI-compatible client with custom `base_url="https://api.deepseek.com"`
- System prompts automatically prepended to message history
- Streaming responses via `client.chat.completions.create(stream=True)`
- Temperature and system prompt come from expert's YAML config

## Essential Commands

### Development Setup
```bash
# Always use .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt  # Development (includes watchdog, pytest, black)
pip install -r requirements.txt        # Production only

# Create example experts
python3 setup_examples.py

# Run the app
streamlit run Home.py
```

### Application Reset
```bash
# Reset application to factory default state
# WARNING: This deletes all configs and pages, then recreates example experts
python3 reset_application.py

# Or make executable and run directly
chmod +x reset_application.py
./reset_application.py
```

**Use reset_application.py when:**
- After modifying `templates/template.py` and need to regenerate all expert pages
- Configs and pages become out of sync or corrupted
- Starting fresh for development/testing
- Restoring application to initial example state

The script will:
1. Ask for confirmation (type "yes" to proceed)
2. Delete all YAML configs from `configs/`
3. Delete all expert pages from `pages/` (keeps Home.py)
4. Run `setup_examples.py` to recreate 7 default experts

### Testing
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_agent_generation.py

# Run specific test
pytest tests/test_agent_generation.py::TestAgentGeneration::test_create_config

# Run with coverage
pytest --cov=utils --cov-report=html

# Quick test run
./run_tests.sh
```

### Code Quality
```bash
# Format code (if black is installed)
black .

# Check import issues
python -m pytest --collect-only  # Verifies imports without running tests
```

## Important Workflows

### Creating a New Expert Agent
When users create an expert through the UI:
1. Form submission → `ConfigManager.create_config()` generates YAML config with unique ID
2. `PageGenerator.generate_page()` creates numbered page file from template
3. `st.rerun()` triggers Streamlit to discover the new page
4. `st.switch_page()` automatically navigates to the new expert

**Manual expert creation** (for testing):
```python
from utils.config_manager import ConfigManager
from utils.page_generator import PageGenerator

config_manager = ConfigManager()
page_generator = PageGenerator()

expert_id = config_manager.create_config(
    expert_name="Test Expert",
    description="An expert in testing...",
    temperature=0.7,
)

page_path = page_generator.generate_page(
    expert_id=expert_id,
    expert_name="Test Expert",
)
```

### Understanding Chat Flow
1. User input → stored in `st.session_state[f"messages_{EXPERT_ID}"]`
2. DeepSeekClient initialized with shared API key
3. `client.chat_stream()` sends messages with system prompt to DeepSeek API
4. Streaming response accumulated character by character
5. Complete response added to session state for context

### Modifying Expert Behavior
- **Temperature**: Edit YAML config file or use UI when creating
- **System Prompt**: Provide custom prompt via "Advanced: Custom System Prompt" field
- **All Experts**: Edit `templates/template.py` (changes require regenerating pages)
  - After modifying template, run `python3 reset_application.py` to regenerate all experts
- **Single Expert**: Edit specific page file directly (but loses template consistency)

## File Structure Notes

- **`templates/template.py`**: Master template - edit this to change all expert pages
- **`pages/`**: Auto-generated expert pages - **gitignored** (regenerated from template)
- **`configs/`**: YAML configs - **gitignored** (regenerated by setup scripts)
- **`utils/`**: Shared business logic - modular, testable components
- **`tests/`**: Test suite using pytest with temporary directories for isolation
- **`setup_examples.py`**: Creates the 7 default example experts
- **`reset_application.py`**: Resets app to factory state (deletes all, then runs setup_examples.py)

**Important**: Both `configs/` and `pages/` are in `.gitignore` since they're auto-generated. To recreate them, run `setup_examples.py` or `reset_application.py`.

## Key Implementation Details

### Session State Isolation Pattern
```python
# WRONG - shared across all experts
if "messages" not in st.session_state:
    st.session_state.messages = []

# RIGHT - isolated per expert
messages_key = f"messages_{EXPERT_ID}"
if messages_key not in st.session_state:
    st.session_state[messages_key] = []
```

### Page Discovery Timing
After creating a new page file, Streamlit won't see it until rerun:
```python
# Create page
page_path = page_generator.generate_page(...)

# Store for navigation after rerun
st.session_state.pending_expert_page = page_path

# Trigger rerun (Streamlit discovers new page)
st.rerun()

# Next run: check for pending navigation and switch
if st.session_state.get("pending_expert_page"):
    st.switch_page(st.session_state.pending_expert_page)
```

### Environment Variable Loading
API keys loaded from `.env` in multiple files:
- `utils/deepseek_client.py` - loads on module import
- `Home.py` - loads at startup
- Both use: `load_dotenv(Path(__file__).parent.parent / ".env")`

## Common Pitfalls

1. **Editing expert pages directly** - Changes lost on regeneration
2. **Not using .venv** - Dependencies or versions may be incorrect
3. **Forgetting `st.rerun()`** after page creation - New page won't be discoverable
4. **Shared session state keys** - Chat history contaminates between experts
5. **Hardcoding paths** - Use `Path(__file__).parent` for relative paths
6. **Not regenerating pages** after template changes - Old pages use outdated code
   - Solution: Run `python3 reset_application.py` after modifying template

## Testing Approach

Tests use **temporary directories** via `tmp_path` fixture to avoid polluting the project:
- Temporary configs directory
- Temporary pages directory
- Copy of actual template
- Automatic cleanup after tests

Always use **fictitious test data**, never real user information.
