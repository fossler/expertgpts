# Test Suite for ExpertGPTs

This directory contains automated tests for the ExpertGPTs application.

## Running Tests

### Run all tests:
```bash
uv run pytest
```

### Run unit tests only:
```bash
uv run pytest -m unit
```

### Run specific test file:
```bash
uv run pytest tests/test_agent_generation.py
```

### Run with coverage report:
```bash
uv run pytest --cov=lib --cov-report=html
```

### Run a specific test:
```bash
uv run pytest tests/test_agent_generation.py::TestAgentGeneration::test_create_config
```

Pytest is configured in `[tool.pytest.ini_options]` of `pyproject.toml` (verbose output, strict markers `unit`, `integration`, `slow`).

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

### `test_attachments.py`
Text and image attachments: message content round trip, size/type validation, image store (incl. path traversal), `to_api_content()` and `supports_images()`.

### `test_i18n.py`
Language prefixes, system prompt construction, locale files without expert content, YAML configs with expert content, end-to-end language workflows.

### `test_llm_params.py`
Model catalog consistency, provider-specific reasoning parameters (OpenAI, DeepSeek, Z.AI, KIMI) and temperature rules (fixed, capped, ignored while thinking).

### `test_message_origin.py`
Assistant messages record `provider`/`model`, which survive saving and loading the chat history.

### `test_page_regeneration.py`
`PageGenerator.regenerate_pages()` keeps each page's identity and skips system pages.

### `test_streaming_cache.py`
Background streaming via `StreamingCache`: cache files, completion/error handling, cleanup, concurrent experts, resume after navigation, crash resilience.

### `test_transcription.py`
Voice input: transcription provider routing, OpenAI language hint vs. GLM-ASR context prompt, error results, audio duration.

## Test Data

`test_agent_generation.py` uses fictitious test data:
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
