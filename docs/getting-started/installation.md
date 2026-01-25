# Installation Guide

This guide provides detailed installation instructions for ExpertGPTs.

## Prerequisites

Before installing ExpertGPTs, ensure you have:

- **Python 3.8 or higher** installed
- **pip** (Python package installer)
- **A DeepSeek API key** - Get one free at [https://platform.deepseek.com/](https://platform.deepseek.com/)
- Git (for cloning the repository)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd expertgpts
```

### 2. Create a Virtual Environment (Recommended)

Using a virtual environment keeps your dependencies isolated and prevents conflicts with system packages.

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Why use a virtual environment?**
- Isolates project dependencies from system packages
- Prevents version conflicts
- Makes dependency management easier
- Standard Python development best practice

### 3. Install Dependencies

ExpertGPTs offers two dependency installation options depending on your use case.

**For Development** (includes testing tools and faster file watching):
```bash
pip install -r requirements-dev.txt
```

**For Production Only** (minimal dependencies):
```bash
pip install -r requirements.txt
```

**Difference**:
- `requirements-dev.txt` includes pytest, pytest-cov, and watchdog for development
- `requirements.txt` includes only runtime dependencies

### 4. Create Example Expert Agents (Optional)

On first run, the application will automatically create 9 example experts. To create them manually:

```bash
python3 scripts/setup.py
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
streamlit run app.py
```

The application should open in your browser at `http://localhost:8501`

## Troubleshooting Installation Issues

### Python Version Errors

**Problem**: `Python version too old`

**Solution**:
```bash
# Check your Python version
python3 --version

# If < 3.8, install a newer version
# macOS: brew install python3
# Ubuntu: sudo apt-get install python3.11
```

### Permission Errors

**Problem**: `Permission denied when installing packages`

**Solution**: Ensure your virtual environment is activated and you have write permissions:
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Install with user flag (if needed)
pip install --user -r requirements.txt
```

### Dependency Conflicts

**Problem**: Package version conflicts

**Solution**:
```bash
# Upgrade pip first
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Verify Streamlit is installed
pip list | grep streamlit

# Reinstall if missing
pip install streamlit
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
pip install -r requirements-dev.txt
streamlit run app.py --server.fileWatcherType=watchdog
```

This provides instant reload when Python files change.

### System-wide Installation (Not Recommended)

You can install globally without a virtual environment, but this is not recommended:

```bash
pip install -r requirements.txt
```

**Warning**: This can conflict with other Python projects and is considered bad practice.

## Uninstallation

To completely remove ExpertGPTs:

```bash
# Deactivate virtual environment
deactivate

# Remove the project directory
rm -rf expertgpts

# (Optional) Remove the virtual environment
rm -rf .venv
```

Configuration files in `.streamlit/` and `chat_history/` will also need to be manually deleted if desired.

## Support

If you encounter issues not covered here:

- Check the **[Troubleshooting Guide](../reference/troubleshooting.md)**
- Visit the [GitHub repository](https://github.com/fossler/expertgpts)
- Open an issue with your error message and environment details

---

**Back to**: [Documentation Home](../README.md) | [Quick Start](quickstart.md)
