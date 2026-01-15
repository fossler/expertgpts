#!/usr/bin/env python3
"""Add experts.management UI translations to all locale files.

This script adds the expert management UI translations that were accidentally
removed during the locale cleanup. These are UI translations, not expert content.
"""

import json
from pathlib import Path

# Translations for "experts.management" section
TRANSLATIONS = {
    "de.json": {
        "title": "Expertenverwaltung",
        "description_label": "Beschreibung",
        "expert_behavior": "Expertenverhalten",
        "actions": "Aktionen",
        "temperature": "Temperatur: {temp}",
        "reasoning_effort": "Reasoning Aufwand: {level}",
        "thinking_mode_enabled": "Thinking-Modus aktiviert",
        "confirm_delete": "Möchten Sie den Experten '{name}' wirklich löschen?"
    },
    "es.json": {
        "title": "Gestión de Expertos",
        "description_label": "Descripción",
        "expert_behavior": "Comportamiento del Experto",
        "actions": "Acciones",
        "temperature": "Temperatura: {temp}",
        "reasoning_effort": "Esfecto de razonamiento: {level}",
        "thinking_mode_enabled": "Modo de pensamiento activado",
        "confirm_delete": "¿Está seguro de que desea eliminar el experto '{name}'?"
    },
    "fr.json": {
        "title": "Gestion des Experts",
        "description_label": "Description",
        "expert_behavior": "Comportement de l'Expert",
        "actions": "Actions",
        "temperature": "Température : {temp}",
        "reasoning_effort": "Effort de raisonnement : {level}",
        "thinking_mode_enabled": "Mode pensée activé",
        "confirm_delete": "Êtes-vous sûr de vouloir supprimer l'expert '{name}' ?"
    },
    "id.json": {
        "title": "Manajemen Ahli",
        "description_label": "Deskripsi",
        "expert_behavior": "Perilaku Ahli",
        "actions": "Tindakan",
        "temperature": "Suhu: {temp}",
        "reasoning_effort": "Usaha penalaran: {level}",
        "thinking_mode_enabled": "Mode berpikir diaktifkan",
        "confirm_delete": "Apakah Anda yakin ingin menghapus ahli '{name}'?"
    },
    "it.json": {
        "title": "Gestione Esperti",
        "description_label": "Descrizione",
        "expert_behavior": "Comportamento dell'Esperto",
        "actions": "Azioni",
        "temperature": "Temperatura: {temp}",
        "reasoning_effort": "Sforzo di ragionamento: {level}",
        "thinking_mode_enabled": "Modalità pensiero attivata",
        "confirm_delete": "Sei sicuro di voler eliminare l'esperto '{name}'?"
    },
    "ms.json": {
        "title": "Pengurusan Pakar",
        "description_label": "Penerangan",
        "expert_behavior": "Kelakuan Pakar",
        "actions": "Tindakan",
        "temperature": "Suhu: {temp}",
        "reasoning_effort": "Usaha penaakulan: {level}",
        "thinking_mode_enabled": "Mod pemikiran diaktifkan",
        "confirm_delete": "Adakah anda pasti mahu memadam pakar '{name}'?"
    },
    "pt.json": {
        "title": "Gerenciamento de Especialistas",
        "description_label": "Descrição",
        "expert_behavior": "Comportamento do Especialista",
        "actions": "Ações",
        "temperature": "Temperatura: {temp}",
        "reasoning_effort": "Esforço de raciocínio: {level}",
        "thinking_mode_enabled": "Modo de pensamento ativado",
        "confirm_delete": "Tem certeza de que deseja excluir o especialista '{name}'?"
    },
    "ru.json": {
        "title": "Управление экспертами",
        "description_label": "Описание",
        "expert_behavior": "Поведение эксперта",
        "actions": "Действия",
        "temperature": "Температура: {temp}",
        "reasoning_effort": "Усилие рассуждения: {level}",
        "thinking_mode_enabled": "Режим мышления включен",
        "confirm_delete": "Вы уверены, что хотите удалить эксперта '{name}'?"
    },
    "tr.json": {
        "title": "Uzman Yönetimi",
        "description_label": "Açıklama",
        "expert_behavior": "Uzman Davranışı",
        "actions": "İşlemler",
        "temperature": "Sıcaklık: {temp}",
        "reasoning_effort": "Muhakeme çabası: {level}",
        "thinking_mode_enabled": "Düşünme modu etkinleştirildi",
        "confirm_delete": "'{name}' uzmanını silmek istediğinizden emin misiniz?"
    },
    "wyw.json": {
        "title": "專家管理",
        "description_label": "描述",
        "expert_behavior": "專家行為",
        "actions": "操作",
        "temperature": "溫度: {temp}",
        "reasoning_effort": "推理努力: {level}",
        "thinking_mode_enabled": "思維模式已啟用",
        "confirm_delete": "您確定要刪除專家 '{name}' 嗎？"
    },
    "yue.json": {
        "title": "專家管理",
        "description_label": "描述",
        "expert_behavior": "專家行為",
        "actions": "操作",
        "temperature": "溫度: {temp}",
        "reasoning_effort": "推理努力: {level}",
        "thinking_mode_enabled": "思維模式已啟用",
        "confirm_delete": "你確定要刪除專家 '{name}' 麼？"
    },
    "zh-CN.json": {
        "title": "专家管理",
        "description_label": "描述",
        "expert_behavior": "专家行为",
        "actions": "操作",
        "temperature": "温度: {temp}",
        "reasoning_effort": "推理强度: {level}",
        "thinking_mode_enabled": "思维模式已启用",
        "confirm_delete": "您确定要删除专家 '{name}' 吗？"
    },
    "zh-TW.json": {
        "title": "專家管理",
        "description_label": "描述",
        "expert_behavior": "專家行為",
        "actions": "操作",
        "temperature": "溫度: {temp}",
        "reasoning_effort": "推理強度: {level}",
        "thinking_mode_enabled": "思維模式已啟用",
        "confirm_delete": "您確定要刪除專家 '{name}' 嗎？"
    },
}


def add_translations_to_locale(locale_file: Path, translations: dict) -> bool:
    """Add experts.management translations to a locale file.

    Args:
        locale_file: Path to the locale JSON file
        translations: Dictionary of translations to add

    Returns:
        bool: True if file was modified, False otherwise
    """
    print(f"Processing {locale_file.name}...")

    with open(locale_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Check if experts.management already exists
    if "experts" in data and "management" in data["experts"]:
        print(f"  ℹ️  experts.management already exists, skipping")
        return False

    # Ensure 'experts' section exists
    if "experts" not in data:
        data["experts"] = {}

    # Add the management section
    data["experts"]["management"] = translations

    # Write back to file
    with open(locale_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Added experts.management section")
    return True


def main():
    """Add translations to all locale files."""
    print("=" * 70)
    print("Adding 'experts.management' UI Translations to All Locale Files")
    print("=" * 70)
    print()

    locale_dir = Path("locales/ui")

    if not locale_dir.exists():
        print(f"❌ Error: Locale directory not found: {locale_dir}")
        return 1

    modified_count = 0

    # Process each translation
    for locale_file, translations in TRANSLATIONS.items():
        file_path = locale_dir / locale_file

        if not file_path.exists():
            print(f"⚠️  Warning: {locale_file} not found, skipping")
            continue

        if add_translations_to_locale(file_path, translations):
            modified_count += 1

    print()
    print("=" * 70)
    print(f"Summary: {modified_count} locale file(s) modified")
    print("=" * 70)

    if modified_count > 0:
        print("\n✅ Expert Management UI translations successfully added!")
        print("\nThese are UI translations for the Settings page, not expert content.")
        print("The app should now display correctly in the Expert Management section.")

    return 0


if __name__ == "__main__":
    exit(main())
