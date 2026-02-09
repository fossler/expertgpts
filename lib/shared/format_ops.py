"""Centralized file format operations for ExpertGPTs.

Provides unified read/write operations for TOML, YAML, and JSON files
with consistent error handling and permissions management.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import json

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python < 3.11

import yaml

from lib.shared.file_ops import set_secure_permissions


def read_toml(file_path: Path) -> Dict[str, Any]:
    """Read a TOML file.

    Returns empty dict if file doesn't exist or is invalid.

    Args:
        file_path: Path to TOML file

    Returns:
        dict: Parsed TOML data, or empty dict on error
    """
    if not file_path.exists():
        return {}

    try:
        content = file_path.read_text()
        return tomllib.loads(content)
    except Exception as e:
        print(f"Warning: Error reading {file_path}: {e}")
        return {}


def write_toml(file_path: Path, data: Dict[str, Any], header: str = "") -> bool:
    """Write data to a TOML file with secure permissions.

    Args:
        file_path: Path to TOML file
        data: Dictionary to write
        header: Optional header comment to add at the top

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Try tomli_w first
        try:
            import tomli_w
            toml_content = tomli_w.dumps(data)
        except ImportError:
            # Fallback for simple cases
            toml_content = header + "\n"
            for section, values in data.items():
                toml_content += f"\n[{section}]\n"
                for key, value in values.items():
                    if isinstance(value, str):
                        toml_content += f'{key} = "{value}"\n'
                    elif isinstance(value, bool):
                        toml_content += f'{key} = {str(value).lower()}\n'
                    else:
                        toml_content += f'{key} = {value}\n'

        file_path.write_text(toml_content)
        set_secure_permissions(file_path)
        return True
    except Exception as e:
        print(f"Error writing TOML to {file_path}: {e}")
        return False


def read_yaml(file_path: Path) -> Optional[Dict[str, Any]]:
    """Read a YAML file.

    Returns None if file doesn't exist or is invalid.

    Args:
        file_path: Path to YAML file

    Returns:
        dict: Parsed YAML data, or None on error
    """
    if not file_path.exists():
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Error reading YAML from {file_path}: {e}")
        return None


def write_yaml(file_path: Path, data: Dict[str, Any]) -> bool:
    """Write data to a YAML file with secure permissions.

    Args:
        file_path: Path to YAML file
        data: Dictionary to write

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

        set_secure_permissions(file_path)
        return True
    except Exception as e:
        print(f"Error writing YAML to {file_path}: {e}")
        return False


def read_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """Read a JSON file.

    Returns None if file doesn't exist or is invalid.

    Args:
        file_path: Path to JSON file

    Returns:
        dict: Parsed JSON data, or None on error
    """
    if not file_path.exists():
        return None

    try:
        content = file_path.read_text(encoding='utf-8')
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Warning: Corrupted JSON file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Warning: Error reading JSON from {file_path}: {e}")
        return None


def write_json(file_path: Path, data: Any, indent: int = 2) -> bool:
    """Write data to a JSON file with secure permissions.

    Args:
        file_path: Path to JSON file
        data: Data to serialize
        indent: JSON indentation (default: 2)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        json_content = json.dumps(data, indent=indent, ensure_ascii=False)
        file_path.write_text(json_content, encoding='utf-8')
        set_secure_permissions(file_path)
        return True
    except Exception as e:
        print(f"Error writing JSON to {file_path}: {e}")
        return False
