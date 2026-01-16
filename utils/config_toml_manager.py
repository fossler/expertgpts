"""Utility for managing Streamlit config.toml file.

This module provides functions to read and write theme settings to the
.streamlit/config.toml file, which controls the visual appearance of the app.
"""

from pathlib import Path
from typing import Optional
import os


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
        print(f"Warning: Could not set secure permissions on {file_path}: {e}")


def get_config_path() -> Path:
    """Get the path to the config.toml file.

    Returns:
        Path: Path to .streamlit/config.toml in project root
    """
    # Get the project root (parent of utils directory)
    project_root = Path(__file__).parent.parent
    return project_root / ".streamlit" / "config.toml"


def ensure_config_file_exists() -> Path:
    """Ensure the .streamlit directory and config.toml file exist.

    Creates the .streamlit directory and config.toml file if they don't exist.

    Returns:
        Path: Path to config.toml file
    """
    config_path = get_config_path()
    config_dir = config_path.parent

    # Create .streamlit directory if it doesn't exist
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)

    # Create config.toml file if it doesn't exist
    if not config_path.exists():
        config_path.write_text("[theme]\n")
        # Set secure permissions on newly created file
        set_secure_permissions(config_path)

    return config_path


def get_theme_settings() -> dict:
    """Get current theme settings from config.toml.

    Returns:
        dict: Dictionary with theme color settings (no theme_name - not supported by Streamlit)
    """
    config_path = get_config_path()

    if not config_path.exists():
        # Return default values if config doesn't exist
        return {
            "primaryColor": "#6366F1",
            "backgroundColor": "#FFFFFF",
            "secondaryBackgroundColor": "#F3F4F6",
            "textColor": "#1F2937",
        }

    content = config_path.read_text()

    # Parse the config file to extract theme settings
    theme_settings = {
        "primaryColor": "#FF6B6B",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F0F2F6",
        "textColor": "#262730",
    }

    in_theme_section = False
    for line in content.split('\n'):
        line = line.strip()

        # Check if we're in the [theme] section
        if line == "[theme]":
            in_theme_section = True
            continue
        elif line.startswith("[") and line != "[theme]":
            in_theme_section = False
            continue

        # Parse theme settings (skip deprecated options like theme_name, base)
        if in_theme_section and "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            # Store valid theme settings only
            if key in theme_settings:
                theme_settings[key] = value

    return theme_settings


def save_theme_settings(
    primaryColor: str = None,
    backgroundColor: str = None,
    secondaryBackgroundColor: str = None,
    textColor: str = None
) -> None:
    """Save theme settings to config.toml file.

    Args:
        primaryColor: Color for buttons and interactive elements
        backgroundColor: Main background color
        secondaryBackgroundColor: Background color for sidebar
        textColor: Main text color

    Note:
        Only updates the fields that are provided (not None).
        Preserves other settings in the config file.
        Does NOT save theme_name (not supported by Streamlit - use base="light" or base="dark" instead).
    """
    config_path = ensure_config_file_exists()

    # Read existing content
    content = config_path.read_text()

    # Parse existing settings (preserve non-theme settings)
    lines = content.split('\n')
    new_lines = []
    in_theme_section = False
    theme_found = False

    # Track which theme settings we've seen (removed theme_name - not valid)
    theme_keys = {"primaryColor", "backgroundColor", "secondaryBackgroundColor", "textColor"}
    seen_theme_settings = set()

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check for theme section
        if stripped == "[theme]":
            in_theme_section = True
            theme_found = True
            new_lines.append(line)
            continue
        elif stripped.startswith("[") and in_theme_section:
            # We've reached the next section
            in_theme_section = False

        # If we're in the theme section, check for theme settings
        if in_theme_section and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()

            # Skip deprecated/invalid options (theme_name, base, etc.)
            if key not in theme_keys:
                # Preserve non-theme settings or skip invalid ones
                if key not in ("theme_name", "base"):
                    new_lines.append(line)
                continue

            # Update the setting if a new value is provided
            seen_theme_settings.add(key)

            if key == "primaryColor" and primaryColor is not None:
                new_lines.append(f'{key} = "{primaryColor}"')
                continue
            elif key == "backgroundColor" and backgroundColor is not None:
                new_lines.append(f'{key} = "{backgroundColor}"')
                continue
            elif key == "secondaryBackgroundColor" and secondaryBackgroundColor is not None:
                new_lines.append(f'{key} = "{secondaryBackgroundColor}"')
                continue
            elif key == "textColor" and textColor is not None:
                new_lines.append(f'{key} = "{textColor}"')
                continue

            # Keep existing setting if no new value provided
            new_lines.append(line)
        else:
            # Keep all non-theme-setting lines
            new_lines.append(line)

    # If theme section doesn't exist, add it
    if not theme_found:
        new_lines.append("\n[theme]")

    # Add any new theme settings that weren't in the file
    theme_section_index = None
    for i, line in enumerate(new_lines):
        if line.strip() == "[theme]":
            theme_section_index = i
            break

    if theme_section_index is not None:
        # Insert new settings after [theme] header
        insert_position = theme_section_index + 1
        settings_to_add = []

        if "primaryColor" not in seen_theme_settings and primaryColor is not None:
            settings_to_add.append(f'primaryColor = "{primaryColor}"')
            seen_theme_settings.add("primaryColor")

        if "backgroundColor" not in seen_theme_settings and backgroundColor is not None:
            settings_to_add.append(f'backgroundColor = "{backgroundColor}"')
            seen_theme_settings.add("backgroundColor")

        if "secondaryBackgroundColor" not in seen_theme_settings and secondaryBackgroundColor is not None:
            settings_to_add.append(f'secondaryBackgroundColor = "{secondaryBackgroundColor}"')
            seen_theme_settings.add("secondaryBackgroundColor")

        if "textColor" not in seen_theme_settings and textColor is not None:
            settings_to_add.append(f'textColor = "{textColor}"')
            seen_theme_settings.add("textColor")

        # Insert the new settings
        for setting in reversed(settings_to_add):
            new_lines.insert(insert_position, setting)

    # Write back to file
    new_content = '\n'.join(new_lines)
    config_path.write_text(new_content)

    # Ensure secure permissions after writing
    set_secure_permissions(config_path)


def reset_to_default_theme() -> None:
    """Reset theme settings to default values."""
    save_theme_settings(
        primaryColor="#6366F1",
        backgroundColor="#FFFFFF",
        secondaryBackgroundColor="#F3F4F6",
        textColor="#1F2937"
    )
