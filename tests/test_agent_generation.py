"""Tests for automatic agent generation."""

import os
import pytest
import shutil
from pathlib import Path

from lib.config import ConfigManager
from lib.shared.page_generator import PageGenerator


class TestAgentGeneration:
    """Test suite for agent generation functionality."""

    @pytest.fixture
    def temp_dirs(self, tmp_path):
        """Create temporary directories for testing.

        Args:
            tmp_path: pytest's temporary path fixture

        Yields:
            Tuple of (temp_pages_dir, temp_configs_dir, temp_template_path)
        """
        temp_pages_dir = tmp_path / "pages"
        temp_configs_dir = tmp_path / "configs"
        temp_template_path = tmp_path / "templates" / "template.py"

        # Create directories
        temp_pages_dir.mkdir()
        temp_configs_dir.mkdir()
        temp_template_path.parent.mkdir()

        # Copy actual template to temp location
        actual_template = Path("templates/template.py")
        if actual_template.exists():
            shutil.copy(actual_template, temp_template_path)

        yield temp_pages_dir, temp_configs_dir, temp_template_path

        # Cleanup happens automatically via tmp_path

    @pytest.fixture
    def test_data(self):
        """Fictitious test data for agent generation.

        Returns:
            Dictionary with test agent data
        """
        return {
            "valid_agent": {
                "name": "Test Wizard",
                "description": "An expert in testing, debugging, and quality assurance. "
                "Specializes in writing unit tests, integration tests, and end-to-end tests. "
                "Knows pytest, unittest, and testing best practices.",
                "temperature": 0.7,
                "custom_prompt": None,
            },
            "agent_with_custom_prompt": {
                "name": "Code Reviewer",
                "description": "Expert in code review and maintaining code quality standards.",
                "temperature": 0.5,
                "custom_prompt": "You are a strict code reviewer. Check for bugs, "
                "security issues, and code style violations. Be constructive but thorough.",
            },
            "creative_agent": {
                "name": "Storyteller",
                "description": "Creative writing expert specializing in engaging narratives "
                "and compelling storytelling techniques.",
                "temperature": 1.5,
                "custom_prompt": None,
            },
        }

    def test_create_config(self, temp_dirs, test_data):
        """Test creating a configuration file.

        Args:
            temp_dirs: Temporary directories fixture
            test_data: Test data fixture
        """
        temp_pages_dir, temp_configs_dir, _ = temp_dirs
        data = test_data["valid_agent"]

        # Create config manager with temp directory
        config_manager = ConfigManager(config_dir=str(temp_configs_dir))

        # Create page generator to get page number
        page_generator = PageGenerator(pages_dir=str(temp_pages_dir))
        page_number = page_generator.get_next_page_number()

        # Create config with required page_number parameter
        expert_id = config_manager.create_config(
            expert_name=data["name"],
            description=data["description"],
            page_number=page_number,
            temperature=data["temperature"],
            system_prompt=data["custom_prompt"],
        )

        # Verify config was created
        config_file = temp_configs_dir / f"{expert_id}.yaml"
        assert config_file.exists(), "Config file should be created"

        # Load and verify config
        config = config_manager.load_config(expert_id)
        assert config["expert_name"] == data["name"]
        assert config["description"] == data["description"]
        assert config["temperature"] == data["temperature"]
        assert "system_prompt" in config
        assert len(config["system_prompt"]) > 0

    def test_create_page(self, temp_dirs, test_data):
        """Test creating a page file.

        Args:
            temp_dirs: Temporary directories fixture
            test_data: Test data fixture
        """
        temp_pages_dir, _, temp_template_path = temp_dirs
        data = test_data["valid_agent"]

        # Create page generator first to get page number
        page_generator = PageGenerator(
            pages_dir=str(temp_pages_dir),
            template_path=str(temp_template_path)
        )
        page_number = page_generator.get_next_page_number()

        # Create config with page number
        config_manager = ConfigManager(config_dir=str(temp_dirs[1]))
        expert_id = config_manager.create_config(
            expert_name=data["name"],
            description=data["description"],
            page_number=page_number,
            temperature=data["temperature"],
        )

        # Generate page
        page_path, _ = page_generator.generate_page(
            expert_id=expert_id,
            expert_name=data["name"],
        )

        # Verify page was created
        page_file = Path(page_path)
        assert page_file.exists(), "Page file should be created"
        assert page_file.parent == temp_pages_dir, "Page should be in pages directory"

        # Verify page content
        content = page_file.read_text()
        assert f'EXPERT_ID = "{expert_id}"' in content
        assert f'EXPERT_NAME = "{data["name"]}"' in content
        assert "messages_{EXPERT_ID}" in content

    def test_full_agent_generation(self, temp_dirs, test_data):
        """Test complete agent generation workflow.

        Args:
            temp_dirs: Temporary directories fixture
            test_data: Test data fixture
        """
        temp_pages_dir, temp_configs_dir, temp_template_path = temp_dirs
        data = test_data["agent_with_custom_prompt"]

        # Initialize managers
        page_generator = PageGenerator(
            pages_dir=str(temp_pages_dir),
            template_path=str(temp_template_path)
        )
        page_number = page_generator.get_next_page_number()

        config_manager = ConfigManager(config_dir=str(temp_configs_dir))

        # Generate complete agent
        expert_id = config_manager.create_config(
            expert_name=data["name"],
            description=data["description"],
            page_number=page_number,
            temperature=data["temperature"],
            system_prompt=data["custom_prompt"],
        )

        page_path, _ = page_generator.generate_page(
            expert_id=expert_id,
            expert_name=data["name"],
        )

        # Verify both files exist
        config_file = temp_configs_dir / f"{expert_id}.yaml"
        page_file = Path(page_path)

        assert config_file.exists(), "Config file should exist"
        assert page_file.exists(), "Page file should exist"

        # Verify config content
        config = config_manager.load_config(expert_id)
        assert config["expert_name"] == data["name"]
        assert config["temperature"] == data["temperature"]
        assert config["system_prompt"] == data["custom_prompt"]

        # Verify page content
        page_content = page_file.read_text()
        assert expert_id in page_content
        assert data["name"] in page_content

    def test_list_experts(self, temp_dirs, test_data):
        """Test listing multiple experts.

        Args:
            temp_dirs: Temporary directories fixture
            test_data: Test data fixture
        """
        temp_pages_dir, temp_configs_dir, _ = temp_dirs
        config_manager = ConfigManager(config_dir=str(temp_configs_dir))
        page_generator = PageGenerator(pages_dir=str(temp_pages_dir))

        # Create multiple experts
        created_ids = []
        for key in ["valid_agent", "creative_agent"]:
            data = test_data[key]
            page_number = page_generator.get_next_page_number()
            expert_id = config_manager.create_config(
                expert_name=data["name"],
                description=data["description"],
                page_number=page_number,
                temperature=data["temperature"],
            )
            created_ids.append(expert_id)

        # List all experts
        experts = config_manager.list_experts_lightweight()

        assert len(experts) == 2, "Should have 2 experts"
        assert all("expert_id" in expert for expert in experts)
        assert all("expert_name" in expert for expert in experts)

        # Verify names match
        expert_names = {e["expert_name"] for e in experts}
        assert "Test Wizard" in expert_names
        assert "Storyteller" in expert_names

    def test_page_naming(self, temp_dirs, test_data):
        """Test that pages are named with proper ordering.

        Args:
            temp_dirs: Temporary directories fixture
            test_data: Test data fixture
        """
        temp_pages_dir, temp_configs_dir, temp_template_path = temp_dirs
        config_manager = ConfigManager(config_dir=str(temp_configs_dir))
        page_generator = PageGenerator(
            pages_dir=str(temp_pages_dir),
            template_path=str(temp_template_path)
        )

        # Create multiple pages
        pages_created = []
        for i in range(3):
            data = test_data["valid_agent"]
            page_number = page_generator.get_next_page_number()
            expert_id = config_manager.create_config(
                expert_name=f"{data['name']} {i}",
                description=data["description"],
                page_number=page_number,
                temperature=data["temperature"],
            )

            page_path, _ = page_generator.generate_page(
                expert_id=expert_id,
                expert_name=f"{data['name']} {i}",
            )
            pages_created.append(Path(page_path).name)

        # Verify ordering (pages start from 1001 in actual implementation)
        assert pages_created[0].startswith("1001_")
        assert pages_created[1].startswith("1002_")
        assert pages_created[2].startswith("1003_")

    def test_delete_expert(self, temp_dirs, test_data):
        """Test deleting an expert configuration.

        Args:
            temp_dirs: Temporary directories fixture
            test_data: Test data fixture
        """
        temp_pages_dir, temp_configs_dir, _ = temp_dirs
        data = test_data["valid_agent"]

        config_manager = ConfigManager(config_dir=str(temp_configs_dir))
        page_generator = PageGenerator(pages_dir=str(temp_pages_dir))

        # Create expert
        page_number = page_generator.get_next_page_number()
        expert_id = config_manager.create_config(
            expert_name=data["name"],
            description=data["description"],
            page_number=page_number,
            temperature=data["temperature"],
        )

        # Verify it exists
        config_file = temp_configs_dir / f"{expert_id}.yaml"
        assert config_file.exists()

        # Delete it
        result = config_manager.delete_config(expert_id)
        assert result is True, "Delete should succeed"

        # Verify it's gone
        assert not config_file.exists(), "Config file should be deleted"

        # Try to load deleted config
        with pytest.raises(FileNotFoundError):
            config_manager.load_config(expert_id)

    def test_custom_system_prompt(self, temp_dirs, test_data):
        """Test that custom system prompts are handled correctly.

        Args:
            temp_dirs: Temporary directories fixture
            test_data: Test data fixture
        """
        temp_pages_dir, temp_configs_dir, _ = temp_dirs
        data = test_data["agent_with_custom_prompt"]

        config_manager = ConfigManager(config_dir=str(temp_configs_dir))
        page_generator = PageGenerator(pages_dir=str(temp_pages_dir))

        # Create with custom prompt
        page_number = page_generator.get_next_page_number()
        expert_id = config_manager.create_config(
            expert_name=data["name"],
            description=data["description"],
            page_number=page_number,
            temperature=data["temperature"],
            system_prompt=data["custom_prompt"],
        )

        # Load and verify
        config = config_manager.load_config(expert_id)
        assert config["system_prompt"] == data["custom_prompt"]

    def test_auto_generated_system_prompt(self, temp_dirs, test_data):
        """Test that system prompts are auto-generated when not provided.

        Args:
            temp_dirs: Temporary directories fixture
            test_data: Test data fixture
        """
        temp_pages_dir, temp_configs_dir, _ = temp_dirs
        data = test_data["valid_agent"]

        config_manager = ConfigManager(config_dir=str(temp_configs_dir))
        page_generator = PageGenerator(pages_dir=str(temp_pages_dir))

        # Create without custom prompt
        page_number = page_generator.get_next_page_number()
        expert_id = config_manager.create_config(
            expert_name=data["name"],
            description=data["description"],
            page_number=page_number,
            temperature=data["temperature"],
            system_prompt=None,  # No custom prompt
        )

        # Load and verify auto-generated prompt
        config = config_manager.load_config(expert_id)
        assert config["system_prompt"] is not None
        assert data["name"] in config["system_prompt"]
        assert data["description"] in config["system_prompt"]


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"])
