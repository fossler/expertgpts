# Testing Guide for ExpertGPTs

This guide covers everything you need to know about testing the ExpertGPTs application.

## Table of Contents

- [Overview](#overview)
- [Running Tests](#running-tests)
- [Test Suite](#test-suite)
- [Writing Tests](#writing-tests)
- [Continuous Integration](#continuous-integration)
- [Best Practices](#best-practices)

## Overview

ExpertGPTs uses **pytest** as its testing framework. The test suite focuses on:

- ✅ Agent configuration management
- ✅ Page file generation
- ✅ Full agent creation workflow
- ✅ System prompt handling
- ✅ Expert listing and deletion

### Test Requirements

All testing dependencies are included in `requirements-dev.txt`:

```bash
pip install -r requirements-dev.txt
```

Or install individually:

```bash
pip install pytest pytest-cov
```

## Running Tests

### Quick Start

The easiest way to run all tests:

```bash
./run_tests.sh
```

This activates the virtual environment and runs tests with verbose output.

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

See detailed test results:

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_agent_generation.py
```

### Run Specific Test

```bash
# Run a specific test class
pytest tests/test_agent_generation.py::TestAgentGeneration

# Run a specific test method
pytest tests/test_agent_generation.py::TestAgentGeneration::test_create_config
```

### Run with Coverage Report

Generate a coverage report:

```bash
pytest --cov=utils --cov-report=html
```

This creates an `htmlcov/` directory. Open `htmlcov/index.html` in your browser to view the report.

### Run with Coverage for Specific Module

```bash
pytest --cov=utils.config_manager tests/test_agent_generation.py::TestAgentGeneration::test_create_config
```

### Run Marked Tests

Run tests with specific markers:

```bash
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run integration tests
pytest -m integration
```

## Test Suite

### Current Tests

The test suite is located in `tests/test_agent_generation.py`.

#### `TestAgentGeneration` Class

| Test | Description |
|------|-------------|
| `test_create_config` | Verifies configuration files are created correctly |
| `test_create_page` | Verifies page files are generated with correct content |
| `test_full_agent_generation` | Tests complete workflow (config + page) |
| `test_list_experts` | Tests listing multiple experts |
| `test_page_naming` | Verifies pages are named with proper ordering (1_, 2_, etc.) |
| `test_delete_expert` | Tests expert deletion functionality |
| `test_custom_system_prompt` | Verifies custom prompts are handled correctly |
| `test_auto_generated_system_prompt` | Tests automatic prompt generation |

### Test Data

All tests use **fictitious test data** (no real user data):

- **Test Wizard**: Testing and QA expert
- **Code Reviewer**: Code review specialist
- **Storyteller**: Creative writing assistant

### Test Results

Current status (8 tests):

```
============================== 8 passed in 1.24s ==============================
```

## Writing Tests

### Test Structure

Follow the **Arrange-Act-Assert** pattern:

```python
def test_my_feature():
    # Arrange: Set up test data
    test_data = {"key": "value"}

    # Act: Execute the function being tested
    result = my_function(test_data)

    # Assert: Verify the result
    assert result == expected_value
```

### Using Fixtures

Pytest fixtures help with setup and teardown:

```python
@pytest.fixture
def temp_dirs(tmp_path):
    """Create temporary directories for testing."""
    temp_dir = tmp_path / "test"
    temp_dir.mkdir()

    yield temp_dir  # This is what the test receives

    # Cleanup happens automatically via tmp_path
```

### Example: Adding a New Test

```python
def test_my_new_feature(temp_dirs):
    """Test description."""
    # Arrange
    config_manager = ConfigManager(config_dir=str(temp_dirs))

    # Act
    result = config_manager.do_something()

    # Assert
    assert result is not None
    assert result.status == "success"
```

### Test Naming Conventions

- Test files: `test_<feature>.py`
- Test classes: `Test<FeatureName>`
- Test functions: `test_<specific_behavior>`

### Example: Full Test File

```python
"""Tests for my new feature."""

import pytest
from utils.my_module import MyClass


class TestMyNewFeature:
    """Test suite for MyNewFeature."""

    def test_basic_functionality(self):
        """Test that basic functionality works."""
        instance = MyClass()
        result = instance.do_work()
        assert result == "expected"

    def test_edge_case(self):
        """Test edge case handling."""
        instance = MyClass()
        result = instance.handle_edge_case(None)
        assert result is None
```

## Continuous Integration

### GitHub Actions (Future)

To add CI with GitHub Actions, create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'

    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        pytest --cov=utils --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Best Practices

### 1. Use Fictitious Data

Always use fake/test data, never real user data:

```python
# ✅ Good
test_data = {"name": "Test Expert", "description": "A test expert"}

# ❌ Bad
test_data = {"name": "John Doe", "email": "john@example.com"}
```

### 2. Clean Up After Tests

Use fixtures and temporary directories:

```python
# ✅ Good - uses tmp_path (auto-cleanup)
def test_with_temp_dir(tmp_path):
    temp_file = tmp_path / "test.txt"
    temp_file.write_text("test")

# ❌ Bad - doesn't clean up
def test_no_cleanup():
    temp_file = open("temp.txt", "w")  # Leaves files behind
```

### 3. Test Isolation

Each test should be independent:

```python
# ✅ Good - independent tests
def test_feature_a():
    assert feature_a() == "a"

def test_feature_b():
    assert feature_b() == "b"

# ❌ Bad - tests depend on order
def test_first():
    global.value = 1

def test_second():
    assert global.value == 1  # Depends on test_first running first
```

### 4. Descriptive Test Names

Make test names self-documenting:

```python
# ✅ Good
def test_create_config_with_invalid_temperature_raises_error():

# ❌ Bad
def test_config():
```

### 5. Test Edge Cases

Don't just test the happy path:

```python
# Test normal case
def test_create_config_with_valid_data():

# Test edge cases
def test_create_config_with_empty_name():
def test_create_config_with_negative_temperature():
def test_create_config_with_very_long_description():
```

### 6. Use Marks for Test Categories

```python
import pytest

@pytest.mark.unit
def test_fast_unit_test():
    """Quick test that runs in milliseconds."""

@pytest.mark.slow
def test_slow_integration_test():
    """Test that takes time to run."""
```

Run specific categories:
```bash
pytest -m unit        # Only fast unit tests
pytest -m "not slow"  # Everything except slow tests
```

## Troubleshooting

### Tests Not Found

**Problem**: `pytest` can't find your tests

**Solution**:
- Ensure test files start with `test_`
- Ensure test functions start with `test_`
- Check that you're running from the project root

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'utils'`

**Solution**:
```bash
# Install in development mode
pip install -e .

# Or ensure you're in the project root
cd /path/to/expertgpts
pytest
```

### Tests Fail When Run Together

**Problem**: Tests pass individually but fail when run together

**Solution**: Tests are probably sharing state. Ensure:
- Each test uses fresh fixtures
- No global state is modified
- Session state is properly cleaned up

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Contributing Tests

When adding new features:

1. **Write tests first** (Test-Driven Development)
2. **Ensure all tests pass** before submitting
3. **Aim for high coverage** (target: >80%)
4. **Document edge cases** in comments
5. **Use fictitious data** only

Run the test suite before committing:

```bash
./run_tests.sh
```

---

**Happy Testing! 🧪**
