# Troubleshooting Guide

This guide covers common issues and solutions for ExpertGPTs.

## Installation Issues

### "Python version too old"

**Problem**: `Python version < 3.8 required`

**Solution**:
```bash
# Check version
python3 --version

# Install newer Python
# macOS: brew install python3
# Ubuntu: sudo apt-get install python3.11
```

---

### "Module not found" errors

**Problem**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
# Ensure virtual environment activated
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Permission errors during installation

**Problem**: `Permission denied when installing packages`

**Solution**:
```bash
# Ensure virtual environment activated
source .venv/bin/activate

# Reinstall
pip install -r requirements.txt --user
```

---

## Configuration Issues

### "Configuration not found" error

**Problem**: Expert configuration missing

**Solution**:
```bash
python3 scripts/setup.py
```

---

### API key errors

**Problem**: `Invalid API key` or `Authentication failed`

**Solutions**:
1. Verify API key in Settings → API Keys
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

**Problem**: `streamlit run app.py` fails

**Possible causes**:
1. Dependencies not installed
2. Port 8501 already in use
3. Python version incompatibility

**Solutions**:
```bash
# Check dependencies
pip install -r requirements.txt

# Use different port
streamlit run app.py --server.port 8502

# Check Python version
python3 --version  # Must be 3.8+
```

---

### Slow responses

**Problem**: Expert takes too long to respond

**Solutions**:
1. Disable thinking level (set to "None")
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
1. App restarts automatically - wait for reload
2. Clear browser cache
3. Check `.streamlit/app_defaults.toml` for correct language code

### Translation missing

**Problem**: Some UI elements still in English after language change

**Solution**:
```bash
python3 scripts/update_translations.py
```

## Development Issues

### Template changes not appearing

**Problem**: Modified template but expert pages unchanged

**Solution**:
```bash
echo "yes" | python3 scripts/reset_application.py
```

### Tests failing

**Problem**: Test suite fails after changes

**Solutions**:
```bash
# Run tests in verbose mode
pytest -v

# Run specific test
pytest tests/test_agent_generation.py::TestAgentGeneration::test_create_config

# Check for import errors
pytest --tb=long
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
2. Verify file permissions
3. Check disk space
4. Ensure `save_chat_history()` is being called

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
