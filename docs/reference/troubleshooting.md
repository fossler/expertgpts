# Troubleshooting Guide

This guide covers common issues and solutions for ExpertGPTs.

## Installation Issues

### "Python version too old"

**Problem**: uv finds no interpreter matching `requires-python = ">=3.14"` (from `pyproject.toml`)

**Solution**:
```bash
# Check version
python3 --version

# Let uv install a matching Python
uv python install 3.14

# Or install it system-wide
# macOS: brew install python@3.14
# Ubuntu: sudo apt-get install python3.14
```

---

### "Module not found" errors

**Problem**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
# Install the locked dependencies into .venv
uv sync
```

If this happens right after a Python upgrade (e.g. an OS upgrade from Python 3.12
to 3.14), the existing `.venv` was built for the old interpreter. `uv run` and
`uv sync` normally detect this and rebuild it; if not, recreate it:

```bash
rm -rf .venv
uv sync
```

---

### Permission errors during installation

**Problem**: `Permission denied when installing packages`

**Solution**:
uv installs into the project's `.venv`, so no root or `--user` installs are
needed. If `.venv` was created by another user, recreate it as yourself:

```bash
rm -rf .venv
uv sync
```

---

## Configuration Issues

### "Configuration not found" error

**Problem**: Expert configuration missing

**Solution**:
```bash
uv run python scripts/setup.py
```

---

### API key errors

**Problem**: `Invalid API key` or `Authentication failed`

**Solutions**:
1. Verify API key in Settings → API Key
2. Check key has sufficient credits
3. Ensure key copied correctly (no extra spaces)
4. Regenerate key if needed

---

### Expert not appearing in navigation

**Problem**: Created expert but not visible in sidebar

**Solutions**:
1. Wait a moment for page discovery
2. Refresh browser
3. Check if page file exists: `ls pages/`
4. Verify config exists: `ls configs/`

---

## Runtime Issues

### Application won't start

**Problem**: `uv run streamlit run app.py` fails

**Possible causes**:
1. Dependencies not installed
2. Port 8501 already in use
3. Python version incompatibility

**Solutions**:
```bash
# Check dependencies
uv sync

# Use different port
uv run streamlit run app.py --server.port 8502

# Check Python version
uv run python --version  # Must be 3.14+
```

---

### Slow responses

**Problem**: Expert takes too long to respond

**Solutions**:
1. Disable thinking in the model row below the chat input ("🧠 None" or "🧠 Disabled"; not available for models that always reason)
2. Switch to faster provider/model
3. Reduce message length
4. Check internet connection
5. Check provider API status

---

### Messages cut off

**Problem**: Response ends abruptly

**Solutions**:
1. Can happen with long responses
2. Ask "Continue" to get rest
3. Or rephrase question for shorter answer

---

## Internationalization Issues

### Language not changing

**Problem**: Selected different language but UI still in English

**Solutions**:
1. The app reruns automatically after selecting a language - wait for reload
2. Clear browser cache
3. Check `.streamlit/app_defaults.toml` for correct language code

### Translation missing

**Problem**: Some UI elements still in English after language change

**Solution**:
```bash
uv run python scripts/update_translations.py
```

## Development Issues

### Template changes not appearing

**Problem**: Modified template (or pulled a template change) but expert pages unchanged

**Solution**: Regenerate the expert pages (configs and chat history are kept):
```bash
uv run python scripts/regenerate_pages.py
```

### Tests failing

**Problem**: Test suite fails after changes

**Solutions**:
```bash
# Run tests in verbose mode
uv run pytest -v

# Run specific test
uv run pytest tests/test_agent_generation.py::TestAgentGeneration::test_create_config

# Check for import errors
uv run pytest --tb=long
```

---

## File Issues

### File permission errors

**Problem**: Can't save to `.streamlit/secrets.toml`

**Solution**:
```bash
# Check directory permissions
ls -la .streamlit/

# Fix if needed
chmod 755 .streamlit/
chmod 600 .streamlit/secrets.toml
```

---

### Chat history not persisting

**Problem**: Conversations not saved across sessions

**Solutions**:
1. Check `chat_history/` directory exists
2. Verify file size is under the 1 MB limit (see the App status tab of the [Debug Page](debug-page.md))
3. Verify file permissions
4. Check disk space
5. Ensure `save_chat_history()` is being called

---

## Getting Help

If issues persist:

1. **Check documentation**: [Documentation Home](../README.md)
2. **Search existing issues**: [GitHub Repository](https://github.com/fossler/expertgpts)
3. **Open new issue**: Include error message and environment details

**Environment Information to Provide**:
- Python version
- Operating system
- Streamlit version
- Full error message
- Steps to reproduce

---

**Back to**: [Documentation Home](../README.md)
