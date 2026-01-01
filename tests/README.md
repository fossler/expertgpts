# Test Suite for ExpertGPTs

This directory contains automated tests for the ExpertGPTs application.

## Running Tests

### Run all tests:
```bash
pytest
```

### Run with verbose output:
```bash
pytest -v
```

### Run specific test file:
```bash
pytest tests/test_agent_generation.py
```

### Run with coverage report:
```bash
pytest --cov=utils --cov-report=html
```

### Run a specific test:
```bash
pytest tests/test_agent_generation.py::TestAgentGeneration::test_create_config
```

## Test Files

### `test_agent_generation.py`
Tests for the agent generation functionality, including:
- Configuration file creation
- Page file generation
- Full agent generation workflow
- Listing multiple experts
- Page naming and ordering
- Deleting experts
- Custom system prompts
- Auto-generated system prompts

## Test Data

Tests use fictitious test data:
- **Test Wizard**: Testing and QA expert
- **Code Reviewer**: Code review specialist
- **Storyteller**: Creative writing assistant

## Adding New Tests

1. Create a new test file in `tests/` directory
2. Name it `test_<feature>.py`
3. Use pytest fixtures for setup/teardown
4. Run tests to verify they work

Example:
```python
def test_my_feature():
    # Arrange
    test_data = {"key": "value"}

    # Act
    result = my_function(test_data)

    # Assert
    assert result == expected
```

## Best Practices

- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Use fixtures for common setup
- Clean up temporary files
- Test both success and failure cases
- Use fictitious test data, not real data
