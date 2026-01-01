"""Utility for managing Streamlit secrets.toml file.

This module provides functions to read and write API keys to the
.streamlit/secrets.toml file, which is the Streamlit-recommended
way to manage secrets in production.
"""

import os
from pathlib import Path


# Secure file permissions: read/write for owner only (600)
SECURE_FILE_PERMISSIONS = 0o600


def set_secure_permissions(file_path: Path) -> None:
    """Set secure file permissions (600) on the given file.

    Args:
        file_path: Path to the file to secure

    Note:
        600 permissions means:
        - Owner: read + write
        - Group: no permissions
        - Others: no permissions
    """
    try:
        file_path.chmod(SECURE_FILE_PERMISSIONS)
    except OSError as e:
        # Log warning but don't fail if we can't set permissions
        # (e.g., on Windows or filesystems that don't support Unix permissions)
        print(f"Warning: Could not set secure permissions on {file_path}: {e}")


def get_secrets_path() -> Path:
    """Get the path to the secrets.toml file.

    Returns:
        Path: Path to .streamlit/secrets.toml in project root
    """
    # Get the project root (parent of utils directory)
    project_root = Path(__file__).parent.parent
    return project_root / ".streamlit" / "secrets.toml"


def ensure_secrets_file_exists() -> Path:
    """Ensure the .streamlit directory and secrets.toml file exist.

    Creates the .streamlit directory and secrets.toml file if they don't exist.
    Sets secure 600 permissions on the file.

    Returns:
        Path: Path to secrets.toml file
    """
    secrets_path = get_secrets_path()
    secrets_dir = secrets_path.parent

    # Create .streamlit directory if it doesn't exist
    if not secrets_dir.exists():
        secrets_dir.mkdir(parents=True, exist_ok=True)

    # Create secrets.toml file if it doesn't exist
    if not secrets_path.exists():
        secrets_path.write_text("")
        # Set secure permissions on newly created file
        set_secure_permissions(secrets_path)

    return secrets_path


def save_api_key(api_key: str) -> None:
    """Save DeepSeek API key to secrets.toml file.

    Args:
        api_key: The DeepSeek API key to save

    Note:
        This will overwrite any existing DEEPSEEK_API_KEY in secrets.toml.
        The application will need to rerun for the new key to be loaded via st.secrets.
        Secure 600 permissions will be set on the file after writing.
    """
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

    # Update the DEEPSEEK_API_KEY
    existing_lines['DEEPSEEK_API_KEY'] = f'"{api_key}"'

    # Write back to file
    new_content = '\n'.join([f'{k} = {v}' for k, v in existing_lines.items()])
    secrets_path.write_text(new_content + '\n')

    # Ensure secure permissions after writing
    set_secure_permissions(secrets_path)


def get_api_key_from_file() -> str | None:
    """Get DeepSeek API key directly from secrets.toml file.

    This is useful for displaying the current key without using st.secrets
    (which requires a rerun to update).

    Returns:
        str | None: The API key if found, None otherwise
    """
    secrets_path = get_secrets_path()

    if not secrets_path.exists():
        return None

    content = secrets_path.read_text()

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('DEEPSEEK_API_KEY'):
            if '=' in line:
                value = line.split('=', 1)[1].strip()
                # Remove quotes if present
                value = value.strip('"').strip("'")
                return value

    return None


def has_api_key_file() -> bool:
    """Check if secrets.toml file exists and has DEEPSEEK_API_KEY.

    Returns:
        bool: True if API key exists in file, False otherwise
    """
    return get_api_key_from_file() is not None
