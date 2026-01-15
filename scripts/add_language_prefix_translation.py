#!/usr/bin/env python3
"""Add language_prefix_auto translation to all locale files.

This script adds the 'info.language_prefix_auto' key to all 13 locale files
with appropriate translations.
"""

import json
from pathlib import Path

# Translations for "The expert will automatically respond in the user's selected language."
TRANSLATIONS = {
    "de.json": "Der Experte antwortet automatisch in der vom Benutzer ausgewählten Sprache.",
    "es.json": "El experto responderá automáticamente en el idioma seleccionado por el usuario.",
    "fr.json": "L'expert répondra automatiquement dans la langue sélectionnée par l'utilisateur.",
    "id.json": "Ahli akan merespons secara otomatis dalam bahasa yang dipilih pengguna.",
    "it.json": "L'esperto risponderà automaticamente nella lingua selezionata dall'utente.",
    "ms.json": "Pakar akan bertindak balas secara automatik dalam bahasa yang dipilih oleh pengguna.",
    "pt.json": "O especialista responderá automaticamente no idioma selecionado pelo usuário.",
    "ru.json": "Эксперт автоматически ответит на выбранном пользователем языке.",
    "tr.json": "Uzman, kullanıcının seçtiği dilde otomatik olarak yanıt verecektir.",
    "wyw.json": "專家會自動用用戶選擇嘅語言回應。",
    "yue.json": "專家會自動用用戶選擇嘅語言回應。",
    "zh-CN.json": "专家将自动使用用户选择的语言进行回复。",
    "zh-TW.json": "專家將自動使用用戶選擇的語言進行回覆。",
}


def add_translation_to_locale(locale_file: Path, translation: str) -> bool:
    """Add language_prefix_auto translation to a locale file.

    Args:
        locale_file: Path to the locale JSON file
        translation: The translated text to add

    Returns:
        bool: True if file was modified, False otherwise
    """
    print(f"Processing {locale_file.name}...")

    with open(locale_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Check if key already exists
    if "info" in data and "language_prefix_auto" in data["info"]:
        print(f"  ℹ️  Key already exists, skipping")
        return False

    # Ensure 'info' section exists
    if "info" not in data:
        data["info"] = {}

    # Add the translation
    data["info"]["language_prefix_auto"] = translation

    # Write back to file
    with open(locale_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Added translation")
    return True


def main():
    """Add translations to all locale files."""
    print("=" * 70)
    print("Adding 'language_prefix_auto' Translation to All Locale Files")
    print("=" * 70)
    print()

    locale_dir = Path("locales/ui")

    if not locale_dir.exists():
        print(f"❌ Error: Locale directory not found: {locale_dir}")
        return 1

    modified_count = 0

    # Process each translation
    for locale_file, translation in TRANSLATIONS.items():
        file_path = locale_dir / locale_file

        if not file_path.exists():
            print(f"⚠️  Warning: {locale_file} not found, skipping")
            continue

        if add_translation_to_locale(file_path, translation):
            modified_count += 1

    print()
    print("=" * 70)
    print(f"Summary: {modified_count} locale file(s) modified")
    print("=" * 70)

    if modified_count > 0:
        print("\n✅ Translation successfully added to all locale files!")

    return 0


if __name__ == "__main__":
    exit(main())
