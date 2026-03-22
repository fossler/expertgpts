# Development Setup Guide

This guide covers setting up a development environment for ExpertGPTs.

## Prerequisites

- Python 3.11 or higher
- uv (Python package manager)
- Git (for version control)
- Code editor or IDE (VSCode, PyCharm, etc.)

## Installing uv

[uv](https://docs.astral.sh/uv/) is a fast Python package installer and resolver:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# With pip (any platform)
pip install uv
```

## Initial Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd expertgpts
```

### 2. Sync Dependencies

```bash
uv sync
```

This creates a virtual environment and installs all dependencies.

**Development dependencies include**:
- All production dependencies
- pytest (testing framework)
- pytest-cov (coverage reporting)
- watchdog (faster file watching)
- black (code formatter)

### 3. Initial Application Setup

```bash
uv run python scripts/setup.py
```

This creates 9 example experts.

## Development Workflow

### Running the Application

**Standard** (recommended):
```bash
uv run streamlit run app.py
```

**With Enhanced File Watching** (recommended for development):
```bash
uv run streamlit run app.py --server.fileWatcherType=watchdog
```

**Benefits of watchdog**:
- Instant reload when Python files change
- Faster development iteration
- Requires `watchdog` package (included in development dependencies)

**Benefits of uv**:
- No need to manually activate virtual environment
- Automatic dependency management
- 10-100x faster than pip

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
├── lib/                       # Core library (domain-driven)
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
uv run pytest

# With coverage
uv run pytest --cov=lib --cov-report=html
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

> **Note**: uv creates the virtual environment at `.venv` when you run `uv sync` or `uv run`.

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
uv run black .

# Check formatting without making changes
uv run black --check .
```

### Type Checking (Optional)

```bash
uv add --dev mypy
uv run mypy lib/
```

## Development Scripts

### `scripts/setup.py`

Create example experts.

```bash
uv run python scripts/setup.py
```

### `scripts/reset_application.py`

Reset to factory defaults (regenerate expert pages from template).

```bash
echo "yes" | uv run python scripts/reset_application.py
```

**Warning**: Deletes all custom experts and regenerates from template.

### `scripts/update_translations.py`

Sync all locale files with English (source of truth).

```bash
uv run python scripts/update_translations.py
```

### `scripts/run_tests.sh`

Run the test suite.

```bash
./scripts/run_tests.sh
```

## Debugging

### Streamlit Debugger

```bash
uv run streamlit run app.py --logger.level=debug
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
uv run black --check .

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
4. Run `uv run pytest` to verify
5. Update CLAUDE.md if needed

### Modifying Expert Template

1. Edit `templates/template.py`
2. Test with one expert
3. Run `uv run python scripts/reset_application.py`
4. Verify all experts work
5. Commit changes

### Adding New Translations

1. Add key to `locales/ui/en.json`
2. Run `uv run python scripts/update_translations.py`
3. Translate in all locale files
4. Test in app

### Adding New Dependencies

```bash
# Add a runtime dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

## Next Steps

- **[Project Structure](project-structure.md)** - File organization
- **[Adding Features](adding-features.md)** - Feature development
- **[Testing Guide](testing.md)** - Testing documentation

---

**Back to**: [Documentation Home](../README.md)
