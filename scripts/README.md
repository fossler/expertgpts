# ExpertGPTs Scripts

This directory contains utility scripts for maintaining and testing the ExpertGPTs application.

## 📁 Available Scripts

### 🔄 Maintenance Scripts

#### `update_translations.py`
**Purpose**: Sync all locale files with English (source of truth)

**What it does**:
- Reads `locales/ui/en.json` as the source of truth
- Adds missing keys to all other language files
- Preserves existing translations
- Recursively merges nested dictionaries

**When to use**:
- After adding new translation keys to `en.json`
- During development of new features
- Before releases to ensure all locales have same structure

**Example**:
```bash
python3 scripts/update_translations.py
```

**Notes**: This is the primary tool for maintaining translation consistency across all 13 supported languages.

---

#### `test_i18n_refactoring.py`
**Purpose**: Test/verification suite for i18n implementation

**What it tests**:
- Language prefix generation for all 13 languages
- System prompt construction with language prefix
- Locale files are clean (no expert content)
- YAML configs still have expert content
- Integration test simulating full workflow

**When to use**:
- After making changes to i18n system
- Adding new languages
- Refactoring translation-related code
- Before releases

**Example**:
```bash
python3 scripts/test_i18n_refactoring.py
```

**Notes**: Essential for ensuring the i18n architecture doesn't break during development.

---

### 🛠️ Application Setup Scripts

#### `setup.py`
**Purpose**: Initial application setup

**What it does**:
- Creates 7 default example experts
- Sets up initial configuration
- Creates expert pages from templates

**When to use**:
- First time running the application
- After deleting all experts and wanting to restore defaults

**Example**:
```bash
python3 scripts/setup.py
```

---

#### `reset_application.py`
**Purpose**: Reset application to factory default state

**What it does**:
- Deletes all expert configurations
- Deletes all expert pages
- Runs `setup.py` to recreate example experts
- **Warning**: This is irreversible and deletes all custom experts

**When to use**:
- After modifying `templates/template.py` and need to regenerate all expert pages
- Configs and pages become corrupted or out of sync
- Starting fresh for development/testing

**Example**:
```bash
echo "yes" | python3 scripts/reset_application.py
```

**⚠️ Warning**: Always use `echo "yes" |` prefix to auto-confirm in non-interactive environments.

---

### 🧪 Testing Scripts

#### `run_tests.sh`
**Purpose**: Run the test suite

**What it does**:
- Executes all pytest tests
- Provides quick test execution

**When to use**:
- After making code changes
- Before committing changes
- Continuous integration

**Example**:
```bash
./scripts/run_tests.sh
```

---

## 🗂️ File Structure

```
scripts/
├── README.md                           # This file
├── update_translations.py              # Sync locales with en.json
├── test_i18n_refactoring.py            # Test i18n implementation
├── setup.py                            # Initial app setup
├── reset_application.py                # Reset to factory defaults
└── run_tests.sh                        # Run test suite
```

## 📝 Script Development Guidelines

When creating new scripts:

1. **Add shebang**: `#!/usr/bin/env python3`
2. **Include docstring**: Explain purpose and usage
3. **Make idempotent** when possible: Scripts should be safe to run multiple times
4. **Add error handling**: Check for file existence, permissions, etc.
5. **Provide feedback**: Print clear messages about what's happening
6. **Use Pathlib**: For cross-platform path handling

## 🔄 Related Documentation

- **CLAUDE.md**: Project overview and development guidelines
- **QUICKSTART.md**: Getting started guide
- **i18n Documentation**: See main documentation directory for internationalization details

## ⚠️ Important Notes

- Always backup your work before running reset scripts
- Test scripts in a development environment first
- Check Python version compatibility (requires Python 3.8+)
- Ensure virtual environment is activated: `source .venv/bin/activate`
