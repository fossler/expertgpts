"""Centralized file operations for ExpertGPTs.

This module provides shared file system utilities to eliminate duplication
across secrets_manager, app_defaults_manager, chat_history_manager, and
config_toml_manager.
"""

from pathlib import Path
from typing import Optional

# Constants
SECURE_FILE_PERMISSIONS = 0o600
PROJECT_ROOT = Path(__file__).parent.parent


def get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Path: Project root directory (parent of utils/)
    """
    return PROJECT_ROOT


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


def ensure_file_exists(
    file_path: Path,
    default_content: str = "",
    set_permissions: bool = True
) -> Path:
    """Ensure a file exists, creating it with default content if needed.

    Args:
        file_path: Path to the file
        default_content: Default content to write if file doesn't exist
        set_permissions: Whether to set secure permissions (default: True)

    Returns:
        Path: Path to the file
    """
    # Create parent directory if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Create file if it doesn't exist
    if not file_path.exists():
        file_path.write_text(default_content)
        if set_permissions:
            set_secure_permissions(file_path)

    return file_path


def get_streamlit_path(filename: str) -> Path:
    """Get path to a file in .streamlit directory.

    Args:
        filename: Name of the config file (e.g., "secrets.toml", "config.toml")

    Returns:
        Path: Path to .streamlit/{filename}
    """
    return get_project_root() / ".streamlit" / filename
