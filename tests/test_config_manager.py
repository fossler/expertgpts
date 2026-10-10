"""Tests for updating expert configurations."""

import pytest

from lib.config.config_manager import ConfigManager
from lib.shared.format_ops import read_yaml


@pytest.fixture
def manager(tmp_path):
    return ConfigManager(config_dir=str(tmp_path))


@pytest.fixture
def expert_id(manager):
    return manager.create_config(
        expert_name="Helper",
        description="Helps",
        page_number=1001,
        system_prompt="You help.",
        provider="deepseek",
        model="deepseek-flash",
    )


def _stored(manager, expert_id):
    return read_yaml(manager.config_dir / f"{expert_id}.yaml")


@pytest.mark.unit
def test_api_key_is_never_stored(manager, expert_id, monkeypatch):
    # Regenerating the system prompt needs the key, but it must not be saved
    calls = []
    monkeypatch.setattr(
        manager,
        "_generate_system_prompt",
        lambda *args: calls.append(args) or "Generated prompt",
    )
    manager.update_config(
        expert_id, {"system_prompt": None, "api_key": "secret-key-value"}
    )
    stored = _stored(manager, expert_id)
    assert calls and "secret-key-value" in calls[0]
    assert stored["system_prompt"] == "Generated prompt"
    assert "api_key" not in stored
    assert "secret-key-value" not in str(stored)


@pytest.mark.unit
def test_llm_fields_are_stored_in_metadata_only(manager, expert_id):
    updates = {
        "provider": "zai",
        "model": "glm-5.3",
        "thinking_level": "max",
        "temperature": 0.5,
        "api_key": None,
    }
    manager.update_config(expert_id, updates)
    stored = _stored(manager, expert_id)
    assert stored["metadata"]["provider"] == "zai"
    assert stored["metadata"]["model"] == "glm-5.3"
    assert stored["metadata"]["thinking_level"] == "max"
    assert stored["temperature"] == 0.5
    for field in ("provider", "model", "thinking_level", "api_key"):
        assert field not in stored
    # The caller's dict is left untouched
    assert updates["provider"] == "zai" and "api_key" in updates
