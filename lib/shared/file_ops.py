"""Centralized file operations for ExpertGPTs.

This module provides shared file system utilities to eliminate duplication
across secrets_manager, app_defaults_manager, chat_history_manager, and
config_toml_manager.
"""

from pathlib import Path
from typing import Optional

# Constants
SECURE_FILE_PERMISSIONS = 0o600
PROJECT_ROOT = Path(__file__).parent.parent.parent


def get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Path: Project root directory (parent of lib/)
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


def safe_path_join(base_dir: Path, user_path: str) -> Path:
    """Safely join paths, preventing directory traversal attacks.

    This function ensures that the resulting path stays within the base directory,
    protecting against path traversal sequences like '../' or '..\\'.

    Args:
        base_dir: The base directory that bounds the allowed path space
        user_path: User-provided path component (could be untrusted)

    Returns:
        Path: Safe, absolute path within base_dir

    Raises:
        ValueError: If path traversal is detected or if path is outside base_dir

    Example:
        >>> base = Path("/home/user/app")
        >>> safe_path_join(base, "config.yaml")
        Path('/home/user/app/config.yaml')
        >>> safe_path_join(base, "../../etc/passwd")
        ValueError: Path traversal detected
    """
    # Resolve both paths to their absolute form
    full_path = (base_dir / user_path).resolve()
    base_resolved = base_dir.resolve()

    # Ensure the resolved path is within base directory
    # Convert to strings for comparison to handle different Path representations
    try:
        full_path.relative_to(base_resolved)
    except ValueError:
        raise ValueError(
            f"Path traversal detected: '{user_path}' resolves outside base directory"
        )

    return full_path


def validate_cwd(cwd_path: Path) -> Path:
    """Validate that a working directory path is safe for subprocess execution.

    This function performs security checks on a directory path before using it
    as the working directory for subprocess calls, preventing command injection
    through path manipulation.

    Args:
        cwd_path: The proposed working directory path

    Returns:
        Path: Validated, resolved path

    Raises:
        ValueError: If path fails security validation

    Security checks:
        - Path must exist and be a directory
        - Path must not contain hidden directories (starting with '.')
        - Path must resolve to a safe location
    """
    # Resolve to absolute path
    resolved = cwd_path.resolve()

    # Ensure it exists and is a directory
    if not resolved.exists():
        raise ValueError(f"Invalid working directory: {cwd_path} (does not exist)")

    if not resolved.is_dir():
        raise ValueError(f"Invalid working directory: {cwd_path} (not a directory)")

    # Check for suspicious paths (hidden directories)
    # This prevents attackers from using paths like /.git/config
    if any(part.startswith('.') for part in resolved.parts if part not in {'.', '..'}):
        raise ValueError(
            f"Hidden directory in path: {cwd_path} "
            "(potential path traversal attempt)"
        )

    return resolved
