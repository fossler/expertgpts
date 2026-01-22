"""Utility for managing Streamlit secrets.toml file.

This module provides functions to read and write API keys to the
.streamlit/secrets.toml file, which is the Streamlit-recommended
way to manage secrets in production.
"""

import os
from pathlib import Path
from lib.shared.file_ops import set_secure_permissions, get_streamlit_path, ensure_file_exists


def get_secrets_path() -> Path:
    """Get the path to the secrets.toml file.

    Returns:
        Path: Path to .streamlit/secrets.toml in project root
    """
    return get_streamlit_path("secrets.toml")


def ensure_secrets_file_exists() -> Path:
    """Ensure the .streamlit directory and secrets.toml file exist.

    Creates the .streamlit directory and secrets.toml file if they don't exist.
    Sets secure 600 permissions on the file.

    Returns:
        Path: Path to secrets.toml file
    """
    return ensure_file_exists(get_secrets_path(), default_content="")

def save_provider_api_key(provider: str, api_key: str) -> None:
    """Save API key for a specific provider to secrets.toml file.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")
        api_key: The API key to save

    Note:
        This will overwrite any existing API key for this provider in secrets.toml.
        The application will need to rerun for the new key to be loaded via st.secrets.
        Secure 600 permissions will be set on the file after writing.
    """
    from lib.shared.constants import get_provider_api_key_env

    secrets_path = ensure_secrets_file_exists()

    # Read existing content
    existing_content = secrets_path.read_text() if secrets_path.exists() else ""

    # Parse existing content to preserve other secrets
    existing_lines = {}
    if existing_content.strip():
        for line in existing_content.split('\n'):
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                existing_lines[key.strip()] = value.strip()

    # Get the environment variable name for this provider's API key
    env_key = get_provider_api_key_env(provider)

    # Update the API key
    existing_lines[env_key] = f'"{api_key}"'

    # Write back to file
    new_content = '\n'.join([f'{k} = {v}' for k, v in existing_lines.items()])
    secrets_path.write_text(new_content + '\n')

    # Ensure secure permissions after writing
    set_secure_permissions(secrets_path)


def get_provider_api_key(provider: str) -> str | None:
    """Get API key for a specific provider directly from secrets.toml file.

    This is useful for displaying the current key without using st.secrets
    (which requires a rerun to update).

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")

    Returns:
        str | None: The API key if found, None otherwise
    """
    from lib.shared.constants import get_provider_api_key_env

    secrets_path = get_secrets_path()

    if not secrets_path.exists():
        return None

    env_key = get_provider_api_key_env(provider)
    content = secrets_path.read_text()

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith(env_key):
            if '=' in line:
                value = line.split('=', 1)[1].strip()
                # Remove quotes if present
                value = value.strip('"').strip("'")
                return value

    return None


def get_all_provider_api_keys() -> dict[str, str]:
    """Get all provider API keys from secrets.toml file.

    Returns:
        dict: Dictionary mapping provider keys to their API keys
               (e.g., {"deepseek": "sk-abc...", "openai": "sk-def..."})
    """
    from lib.shared.constants import LLM_PROVIDERS

    api_keys = {}

    for provider in LLM_PROVIDERS.keys():
        api_key = get_provider_api_key(provider)
        if api_key:
            api_keys[provider] = api_key

    return api_keys


def has_provider_api_key(provider: str) -> bool:
    """Check if secrets.toml file has API key for a specific provider.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")

    Returns:
        bool: True if API key exists in file for this provider, False otherwise
    """
    return get_provider_api_key(provider) is not None
