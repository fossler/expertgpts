#!/usr/bin/env python3
"""Remove expert content from locale files.

This script removes the 'experts' and 'expert_names' sections from all
locale files, eliminating data duplication between YAML configs and locales.

After running this script:
- Locale files will contain ONLY UI translations
- Expert content will exist ONLY in YAML configs
- Language prefix will be injected at runtime

Usage:
    python3 scripts/remove_expert_content_from_locales.py
"""

import json
from pathlib import Path


def remove_expert_content_from_locale(locale_file: Path) -> bool:
    """Remove expert content from a single locale file.

    Args:
        locale_file: Path to the locale JSON file

    Returns:
        bool: True if file was modified, False otherwise
    """
    print(f"Processing {locale_file.name}...")

    with open(locale_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Track if we removed anything
    modified = False

    # Remove expert content sections
    if "experts" in data:
        print(f"  ✓ Removed 'experts' section")
        del data["experts"]
        modified = True

    if "expert_names" in data:
        print(f"  ✓ Removed 'expert_names' section")
        del data["expert_names"]
        modified = True

    # Check for any other expert-related keys
    expert_keys = [k for k in data.keys() if k.startswith("expert_")]
    for key in expert_keys:
        print(f"  ✓ Removed '{key}' section")
        del data[key]
        modified = True

    if modified:
        # Write back to file with proper formatting
        with open(locale_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Saved cleaned file")
    else:
        print(f"  ℹ️  No expert content found (already cleaned)")

    return modified


def main():
    """Remove expert content from all locale files."""
    print("=" * 60)
    print("Removing Expert Content from Locale Files")
    print("=" * 60)
    print()

    locale_dir = Path("locales/ui")

    if not locale_dir.exists():
        print(f"❌ Error: Locale directory not found: {locale_dir}")
        return 1

    # Find all locale JSON files
    locale_files = sorted(locale_dir.glob("*.json"))

    if not locale_files:
        print(f"❌ Error: No locale files found in {locale_dir}")
        return 1

    print(f"Found {len(locale_files)} locale file(s)\n")

    # Process each file
    modified_count = 0
    for locale_file in locale_files:
        if remove_expert_content_from_locale(locale_file):
            modified_count += 1
        print()

    # Summary
    print("=" * 60)
    print(f"Summary: {modified_count}/{len(locale_files)} files modified")
    print("=" * 60)

    if modified_count > 0:
        print("\n✅ Expert content successfully removed from locale files!")
        print("\nNext steps:")
        print("1. Review the changes with: git diff locales/ui/")
        print("2. Test the app to ensure experts still work correctly")
        print("3. Commit the changes")
    else:
        print("\nℹ️  All locale files were already clean (no expert content found)")

    return 0


if __name__ == "__main__":
    exit(main())
