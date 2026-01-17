# Scripts Reference

This guide documents all administrative scripts in ExpertGPTs.

## Available Scripts

### Maintenance Scripts

#### `update_translations.py`

**Purpose**: Sync all locale files with English (source of truth)

**What it does**:
- Reads `locales/ui/en.json` as source
- Adds missing keys to all other language files
- Preserves existing translations
- Recursively merges nested dictionaries

**When to use**:
- After adding new translation keys to `en.json`
- During development of new features
- Before releases

**Usage**:
```bash
python3 scripts/update_translations.py
```

**Note**: This is the primary tool for maintaining translation consistency across all 13 supported languages.

---

### Application Setup Scripts

#### `setup.py`

**Purpose**: Initial application setup

**What it does**:
- Creates 7 default example experts
- Sets up initial configuration
- Creates expert pages from templates

**When to use**:
- First time running the application
- After deleting all experts

**Usage**:
```bash
python3 scripts/setup.py
```

**Creates Experts**:
- Python Expert
- Data Scientist
- Writing Assistant
- Linux System Admin
- Career Coach
- Translation Expert
- Spell Checker

---

#### `reset_application.py`

**Purpose**: Reset application to factory default state

**What it does**:
- Deletes all expert configurations
- Deletes all expert pages
- Runs `setup.py` to recreate example experts
- **Warning**: Irreversible, deletes all custom experts

**When to use**:
- After modifying `templates/template.py` to regenerate pages
- When configs/pages become corrupted
- Starting fresh for development/testing

**Usage**:
```bash
echo "yes" | python3 scripts/reset_application.py
```

**⚠️ Warning**: Always use `echo "yes" |` prefix to auto-confirm in non-interactive environments.

---

### Testing Scripts

#### `run_tests.sh`

**Purpose**: Run the test suite

**What it does**:
- Activates virtual environment
- Executes all pytest tests
- Provides verbose output

**When to use**:
- After making code changes
- Before committing changes
- Continuous integration

**Usage**:
```bash
./scripts/run_tests.sh
```

**Direct pytest alternatives**:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agent_generation.py

# Run with coverage
pytest --cov=utils --cov-report=html
```

---

## Script Development Guidelines

When creating new scripts:

1. **Add shebang**: `#!/usr/bin/env python3`
2. **Include docstring**: Explain purpose and usage
3. **Make idempotent** when possible: Safe to run multiple times
4. **Add error handling**: Check for file existence, permissions
5. **Provide feedback**: Print clear messages about progress
6. **Use Pathlib**: For cross-platform path handling

**Example**:
```python
#!/usr/bin/env python3
"""Script description here."""

import sys
from pathlib import Path

def main():
    """Main function."""
    # Script logic here
    print("Operation complete")

if __name__ == "__main__":
    main()
```

---

## Related Documentation

- **[Development Setup](../development/setup.md)** - Development environment
- **[Testing Guide](../development/testing.md)** - Testing documentation
- **[CLAUDE.md](../../CLAUDE.md)** - Project overview

---

**Back to**: [Documentation Home](../README.md)
