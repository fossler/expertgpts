#!/usr/bin/env python3
"""Update translation files with new keys from en.json.

This script reads the English translation file (source of truth) and updates
all other language files with missing keys, preserving existing translations.
"""

import json
from pathlib import Path


def load_json(file_path: Path) -> dict:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: dict, file_path: Path):
    """Save JSON file with proper formatting."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def merge_keys(source: dict, target: dict) -> dict:
    """Recursively merge keys from source into target, preserving existing translations.

    Args:
        source: Source dictionary (en.json with all keys)
        target: Target dictionary (existing translation)

    Returns:
        Updated target dictionary with all keys from source
    """
    result = target.copy()

    for key, value in source.items():
        if key not in result:
            # New key - add it with source value (will need translation)
            result[key] = value
        elif isinstance(value, dict) and isinstance(result[key], dict):
            # Recursive merge for nested dictionaries
            result[key] = merge_keys(value, result[key])
        # else: key exists and is not a dict, keep existing translation

    return result


def main():
    """Main function to update all translation files."""
    # Set up paths
    locales_dir = Path(__file__).parent.parent / "locales" / "ui"
    source_file = locales_dir / "en.json"

    if not source_file.exists():
        print(f"Error: Source file {source_file} not found")
        return

    # Load source (English)
    source_data = load_json(source_file)

    # Get all language files
    lang_files = sorted(locales_dir.glob("*.json"))

    # Exclude en.json (source)
    target_files = [f for f in lang_files if f.name != "en.json"]

    print(f"Found {len(target_files)} language files to update")
    print(f"Source: {source_file.name}")
    print(f"Targets: {[f.name for f in target_files]}")
    print()

    # Update each language file
    for target_file in target_files:
        print(f"Updating {target_file.name}...")

        try:
            # Load existing translation
            target_data = load_json(target_file)

            # Merge keys
            updated_data = merge_keys(source_data, target_data)

            # Save updated file
            save_json(updated_data, target_file)

            print(f"  ✓ Updated {target_file.name}")
        except Exception as e:
            print(f"  ✗ Error updating {target_file.name}: {e}")

    print()
    print("Translation files updated successfully!")
    print()
    print("NOTE: New keys have been added with English text as placeholders.")
    print("You should review and translate these keys for each language.")


if __name__ == "__main__":
    main()
