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
        dict: Dictionary with theme color settings
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

    # Check if base parameter exists in config.toml
    in_theme_section = False
    base_path = None

    for line in content.split('\n'):
        line = line.strip()

        # Check if we're in the [theme] section
        if line == "[theme]":
            in_theme_section = True
            continue
        elif line.startswith("[") and line != "[theme]":
            in_theme_section = False
            continue

        # Look for base parameter
        if in_theme_section and "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key == "base":
                # Load theme from external file
                theme_file_path = Path(__file__).parent.parent / ".streamlit" / value
                return load_theme_file(theme_file_path)

    # No base parameter found - return default theme
    return {
        "primaryColor": "#6366F1",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F3F4F6",
        "textColor": "#1F2937",
    }


def load_theme_file(theme_file_path: Path) -> dict:
    """Load theme colors from external .toml file.

    Args:
        theme_file_path: Path to theme .toml file

    Returns:
        dict with primaryColor, backgroundColor, secondaryBackgroundColor, textColor
    """
    if not theme_file_path.exists():
        # Return default values if theme file doesn't exist
        return {
            "primaryColor": "#6366F1",
            "backgroundColor": "#FFFFFF",
            "secondaryBackgroundColor": "#F3F4F6",
            "textColor": "#1F2937",
        }

    content = theme_file_path.read_text()

    # Default theme colors
    theme_settings = {
        "primaryColor": "#6366F1",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F3F4F6",
        "textColor": "#1F2937",
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

        # Parse theme settings
        if in_theme_section and "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            # Store valid theme color settings
            if key in theme_settings:
                theme_settings[key] = value

    return theme_settings


def update_custom_theme(
    primaryColor: str,
    backgroundColor: str,
    secondaryBackgroundColor: str,
    textColor: str
) -> None:
    """Update the custom.toml theme file with new colors.

    Args:
        primaryColor: Color for buttons and interactive elements
        backgroundColor: Main background color
        secondaryBackgroundColor: Background color for sidebar
        textColor: Main text color
    """
    custom_theme_path = Path(__file__).parent.parent / ".streamlit" / "themes" / "custom.toml"

    # Create themes directory if it doesn't exist
    custom_theme_path.parent.mkdir(parents=True, exist_ok=True)

    # Write theme settings to custom.toml
    content = f"""[theme]
primaryColor = "{primaryColor}"
backgroundColor = "{backgroundColor}"
secondaryBackgroundColor = "{secondaryBackgroundColor}"
textColor = "{textColor}"
"""

    custom_theme_path.write_text(content)

    # Set secure permissions
    set_secure_permissions(custom_theme_path)


def save_theme_settings(base: str) -> None:
    """Save theme base path to config.toml file.

    Args:
        base: Path to theme file (e.g., "themes/modern_red.toml")

    Note:
        Saves only the base parameter. All color settings are stored
        in the external theme file. Preserves other settings in config.toml.
    """
    config_path = ensure_config_file_exists()

    # Read existing content
    content = config_path.read_text()

    # Parse existing settings (preserve non-theme settings)
    lines = content.split('\n')
    new_lines = []
    in_theme_section = False
    theme_found = False
    base_added = False

    # Theme color keys to remove when using base parameter
    theme_color_keys = {"primaryColor", "backgroundColor", "secondaryBackgroundColor", "textColor"}

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

        # If we're in the theme section, process theme settings
        if in_theme_section and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()

            # Remove old color keys when switching to base parameter
            if key in theme_color_keys:
                continue  # Skip color keys (they're in the theme file now)

            # Update or add base parameter
            if key == "base":
                new_lines.append(f'base = "{base}"')
                base_added = True
                continue

        new_lines.append(line)

    # If theme section doesn't exist, add it
    if not theme_found:
        new_lines.append("\n[theme]")

    # Add base parameter if not already added
    if not base_added:
        # Find the [theme] section
        theme_section_index = None
        for i, line in enumerate(new_lines):
            if line.strip() == "[theme]":
                theme_section_index = i
                break

        if theme_section_index is not None:
            # Insert base parameter after [theme] header
            new_lines.insert(theme_section_index + 1, f'base = "{base}"')

    # Write back to file
    new_content = '\n'.join(new_lines)
    config_path.write_text(new_content)

    # Ensure secure permissions after writing
    set_secure_permissions(config_path)


def reset_to_default_theme() -> None:
    """Reset theme settings to default theme (ocean_blue)."""
    save_theme_settings(base=".streamlit/themes/ocean_blue.toml")
