"""Configuration manager for Domain Expert Agents."""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from utils.helpers import sanitize_name


class ConfigManager:
    """Manages configuration files for expert agents."""

    def __init__(self, config_dir: str = "configs"):
        """Initialize the config manager.

        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

    def create_config(
        self,
        expert_name: str,
        description: str,
        page_number: int,
        temperature: float = 1.0,
        system_prompt: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> str:
        """Create a new configuration file for an expert.

        Args:
            expert_name: Name of the expert agent
            description: Description of the expert's domain
            page_number: Page number for filename (matches page numbering)
            temperature: Temperature for AI responses (0.0-2.0)
            system_prompt: Optional custom system prompt (None triggers AI generation)
            api_key: DeepSeek API key (required for AI generation)

        Returns:
            expert_id: Unique ID for the created expert (matches filename without extension)
        """
        # Generate expert_id based on page number and name (matches filename)
        safe_name = sanitize_name(expert_name)
        expert_id = f"{page_number}_{safe_name}"

        # Create system prompt if not provided or empty
        if system_prompt is None or system_prompt.strip() == "":
            system_prompt = self._generate_system_prompt(
                expert_name, description, temperature, api_key
            )

        config = {
            "expert_id": expert_id,
            "expert_name": expert_name,
            "description": description,
            "temperature": temperature,
            "system_prompt": system_prompt,
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "version": "1.0",
                "model": "deepseek-chat",
            },
        }

        # Config filename matches expert_id
        config_path = self.config_dir / f"{expert_id}.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        return expert_id

    def load_config(self, expert_id: str) -> Dict:
        """Load configuration for an expert.

        Args:
            expert_id: Unique ID of the expert (matches filename without extension)

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        config_path = self.config_dir / f"{expert_id}.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration not found: {expert_id}")

        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def update_config(self, expert_id: str, updates: Dict) -> None:
        """Update configuration for an expert.

        Args:
            expert_id: Unique ID of the expert
            updates: Dictionary of fields to update
        """
        config = self.load_config(expert_id)

        # Handle AI generation for system_prompt
        if "system_prompt" in updates:
            new_system_prompt = updates["system_prompt"]

            # If None or empty string, trigger AI generation (if API key provided)
            if new_system_prompt is None or new_system_prompt.strip() == "":
                api_key = updates.get("api_key")
                expert_name = updates.get("expert_name", config.get("expert_name"))
                description = updates.get("description", config.get("description"))
                temperature = updates.get("temperature", config.get("temperature", 1.0))

                updates["system_prompt"] = self._generate_system_prompt(
                    expert_name, description, temperature, api_key
                )

        # Continue with normal update
        config.update(updates)
        config["updated_at"] = datetime.now().isoformat()

        # Save config file
        config_path = self.config_dir / f"{expert_id}.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    def list_experts(self) -> List[Dict]:
        """List all available experts.

        Returns:
            List of expert configurations (including temperature and system_prompt)
        """
        experts = []

        for config_file in self.config_dir.glob("*.yaml"):
            try:
                config = self.load_config(config_file.stem)
                experts.append({
                    "expert_id": config["expert_id"],
                    "expert_name": config["expert_name"],
                    "description": config["description"],
                    "temperature": config.get("temperature", 1.0),
                    "system_prompt": config.get("system_prompt", ""),
                    "metadata": config.get("metadata", {}),
                    "created_at": config.get("created_at", "Unknown"),
                })
            except Exception as e:
                print(f"Error loading config {config_file}: {e}")
                continue

        # Sort by creation date
        experts.sort(key=lambda x: x["created_at"], reverse=False)
        return experts

    def delete_config(self, expert_id: str) -> bool:
        """Delete a configuration file.

        Args:
            expert_id: Unique ID of the expert (matches filename without extension)

        Returns:
            True if deleted, False if not found
        """
        config_path = self.config_dir / f"{expert_id}.yaml"

        if config_path.exists():
            config_path.unlink()
            return True
        return False

    def _generate_system_prompt(
        self,
        expert_name: str,
        description: str,
        temperature: float = 1.0,
        api_key: Optional[str] = None,
    ) -> str:
        """Generate a system prompt using AI or fallback template.

        Args:
            expert_name: Name of the expert
            description: Description of the expert's domain
            temperature: Temperature for AI generation
            api_key: DeepSeek API key (if None, uses template only)

        Returns:
            Generated system prompt (AI-generated or template fallback)
        """
        # Import here to avoid circular dependency
        from utils.deepseek_client import DeepSeekClient

        # If no API key provided, use template directly
        if not api_key:
            return self._get_template_system_prompt(expert_name, description)

        try:
            # Try AI generation
            client = DeepSeekClient(api_key=api_key)
            return client.generate_system_prompt(expert_name, description, temperature)
        except Exception:
            # Silent fallback to template
            return self._get_template_system_prompt(expert_name, description)

    def _get_template_system_prompt(self, expert_name: str, description: str) -> str:
        """Get the template-based system prompt (fallback).

        Args:
            expert_name: Name of the expert
            description: Description of the expert's domain

        Returns:
            Template system prompt
        """
        return f"""You are {expert_name}, a domain-specific expert AI assistant.

{description}

## Guidelines
- Provide accurate, expert-level information in your domain
- If you're unsure about something, acknowledge it honestly
- Use clear, professional language appropriate for your domain
- Ask clarifying questions when needed to provide better assistance
- Provide practical, actionable advice when applicable

Remember: You are a specialized expert. Stay within your domain of expertise and provide high-quality, accurate information."""
