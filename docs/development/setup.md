# Development Setup Guide

This guide covers setting up a development environment for ExpertGPTs.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)
- Code editor or IDE (VSCode, PyCharm, etc.)

## Initial Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd expertgpts
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

**Development dependencies include**:
- All production dependencies
- pytest (testing framework)
- pytest-cov (coverage reporting)
- watchdog (faster file watching)

### 4. Initial Application Setup

```bash
python3 scripts/setup.py
```

This creates 7 example experts.

## Development Workflow

### Running the Application

**Standard**:
```bash
streamlit run app.py
```

**With Enhanced File Watching** (recommended for development):
```bash
streamlit run app.py --server.fileWatcherType=watchdog
```

**Benefits of watchdog**:
- Instant reload when Python files change
- Faster development iteration
- Requires `watchdog` package (included in requirements-dev.txt)

### Project Structure

```
expertgpts/
├── app.py                      # Entry point
├── pages/                      # Streamlit pages
│   ├── 1000_Home.py           # Home (permanent)
│   ├── 9998_Settings.py       # Settings (permanent)
│   ├── 9999_Help.py           # Help (permanent)
│   └── 1XXX_*.py             # Expert pages (generated)
├── templates/
│   └── template.py            # Expert page template
├── utils/                     # Business logic
├── configs/                   # Expert configurations
├── locales/                   # UI translations
├── tests/                     # Test suite
└── scripts/                   # Administrative scripts
```

### Running Tests

```bash
# Run all tests
./scripts/run_tests.sh

# Or directly with pytest
pytest

# With coverage
pytest --cov=utils --cov-report=html
```

## IDE Setup

### VSCode

**Recommended Extensions**:
- Python (Microsoft)
- Pylance (Microsoft)
- Python Test Explorer (LittleFoxTeam)

**Workspace Settings** (.vscode/settings.json):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["-v"],
  "files.watcherExclude": {
    "**/.streamlit/**": true
  }
}
```

### PyCharm

**Configuration**:
1. Open project
2. Settings → Project → Python Interpreter
3. Add existing interpreter: `.venv/bin/python`
4. Settings → Tools → Python Integrated Tools
5. Set default test runner to pytest

## Code Quality

### Formatting with Black

```bash
# Format code
black .

# Check formatting without making changes
black --check .
```

### Type Checking (Optional)

```bash
pip install mypy
mypy utils/
```

## Development Scripts

### `scripts/setup.py`

Create example experts.

```bash
python3 scripts/setup.py
```

### `scripts/reset_application.py`

Reset to factory defaults (regenerate expert pages from template).

```bash
echo "yes" | python3 scripts/reset_application.py
```

**Warning**: Deletes all custom experts and regenerates from template.

### `scripts/update_translations.py`

Sync all locale files with English (source of truth).

```bash
python3 scripts/update_translations.py
```

### `scripts/run_tests.sh`

Run the test suite.

```bash
./scripts/run_tests.sh
```

## Debugging

### Streamlit Debugger

```bash
streamlit run app.py --logger.level=debug
```

### Python Debugger

Add breakpoint in code:
```python
import pdb; pdb.set_trace()
```

Or use VSCode/PyCharm debugger.

## Development Best Practices

### 1. Follow DRY Principle

Before writing code:
- Search for existing implementations
- Extract shared functionality to utils
- Update all locations using the code

### 2. Template-First Development

When modifying expert pages:
1. Edit `templates/template.py`
2. Test with one expert
3. Run `reset_application.py` to regenerate all
4. Test multiple experts

### 3. Test Before Committing

```bash
# Run tests
./scripts/run_tests.sh

# Check formatting
black --check .

# If both pass, commit
git add .
git commit -m "Description"
```

### 4. Incremental Development

- Make small, testable changes
- Commit frequently
- Test after each change
- Document complex logic

## Common Development Tasks

### Adding a New Utility

1. Create file in `lib/`
2. Add functionality
3. Write tests in `tests/`
4. Run tests to verify
5. Update CLAUDE.md if needed

### Modifying Expert Template

1. Edit `templates/template.py`
2. Test with one expert
3. Run `reset_application.py`
4. Verify all experts work
5. Commit changes

### Adding New Translations

1. Add key to `locales/ui/en.json`
2. Run `update_translations.py`
3. Translate in all locale files
4. Test in app

## Next Steps

- **[Project Structure](project-structure.md)** - File organization
- **[Adding Features](adding-features.md)** - Feature development
- **[Testing Guide](testing.md)** - Testing documentation

---

**Back to**: [Documentation Home](../README.md)
