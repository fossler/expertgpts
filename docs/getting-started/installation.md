# Installation Guide

This guide provides detailed installation instructions for ExpertGPTs.

## Prerequisites

Before installing ExpertGPTs, ensure you have:

- **Python 3.11 or higher** installed
- **uv** (Python package manager) - [Installation instructions](#installing-uv)
- **A DeepSeek API key** - Get one free at [https://platform.deepseek.com/](https://platform.deepseek.com/)
- Git (for cloning the repository)

## Installing uv

[uv](https://docs.astral.sh/uv/) is a fast Python package installer and resolver. We recommend using it for managing dependencies.

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# With pip (any platform)
pip install uv
```

**Why uv?**
- 10-100x faster than pip
- Automatic dependency resolution
- Built-in virtual environment management
- No need to manually create/activate venv
- Reproducible builds with `uv.lock`

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd expertgpts
```

### 2. Run the Application

With uv, you don't need to manually create a virtual environment or install dependencies. Just run:

```bash
uv run streamlit run app.py
```

uv automatically:
- Creates a virtual environment (if needed)
- Installs all dependencies
- Runs the command in that environment

### 3. Create Example Expert Agents (Optional)

On first run, the application will automatically create 9 example experts. To create them manually:

```bash
uv run python scripts/setup.py
```

This creates the following experts:
- Helpful Assistant
- Email Assistant
- Translation Expert EN-DE
- Spell Checker
- Copywriter
- Text Summarizer
- Data Scientist
- Linux System Engineer
- Python Expert

## Verification

Verify your installation by running the application:

```bash
uv run streamlit run app.py
```

The application should open in your browser at `http://localhost:8501`

## Troubleshooting Installation Issues

### Python Version Errors

**Problem**: `Python version too old`

**Solution**:
```bash
# Check your Python version
python3 --version

# If < 3.11, install a newer version
# macOS: brew install python3
# Ubuntu: sudo apt-get install python3.12
```

### uv Not Found

**Problem**: `uv: command not found`

**Solution**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your shell or add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Dependency Issues

**Problem**: Package version conflicts or missing dependencies

**Solution**:
```bash
# Clear uv cache and reinstall
uv cache clean
uv sync --reinstall
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
# Make sure you're using uv run
uv run streamlit run app.py

# Or sync dependencies explicitly
uv sync
```

## Next Steps

After successful installation:

1. **[Quick Start Guide](quickstart.md)** - Get up and running in 5 minutes
2. **[First Use Guide](first-use.md)** - Learn the basics of using the app
3. **[User Guide](../user-guide/basics.md)** - Comprehensive user documentation

## Development Setup

If you're planning to contribute or modify the codebase, see the **[Development Setup Guide](../development/setup.md)** for additional configuration.

## Advanced Installation Options

### Using watchdog for Faster Development

For faster file reloading during development:

```bash
uv run streamlit run app.py --server.fileWatcherType=watchdog
```

This provides instant reload when Python files change. The `watchdog` package is included in the development dependencies.

### Traditional pip Installation (Alternative)

If you prefer using pip directly with a virtual environment:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt  # Development
# OR
pip install -r requirements.txt       # Production only

# Run the app
streamlit run app.py
```

**Note**: uv is recommended for better performance and simpler workflow.

## Uninstallation

To completely remove ExpertGPTs:

```bash
# Remove the project directory
rm -rf expertgpts

# uv's virtual environment is stored in .venv in the project directory
# so it's removed automatically when you delete the project
```

Configuration files in `.streamlit/` and `chat_history/` will also need to be manually deleted if desired.

## Support

If you encounter issues not covered here:

- Check the **[Troubleshooting Guide](../reference/troubleshooting.md)**
- Visit the [GitHub repository](https://github.com/fossler/expertgpts)
- Open an issue with your error message and environment details

---

**Back to**: [Documentation Home](../README.md) | [Quick Start](quickstart.md)
