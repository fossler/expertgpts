"""Setup script to create example expert agents.

Run this script to populate the app with example Domain Expert Agents.
"""

import shutil
from pathlib import Path
from utils.config_manager import ConfigManager
from utils.page_generator import PageGenerator


def copy_settings_page():
    """Copy the Settings page from templates to pages directory."""
    template_settings = Path("templates/9999_Settings.py")
    pages_settings = Path("pages/9999_Settings.py")

    if template_settings.exists():
        shutil.copy2(template_settings, pages_settings)
        print(f"✅ Copied Settings page to pages/")
    else:
        print(f"⚠️  Warning: Settings template not found at {template_settings}")


def create_example_experts():
    """Create a set of example expert agents."""

    config_manager = ConfigManager()
    page_generator = PageGenerator()

    examples = [
        {
            "name": "Python Expert",
            "description": "Expert in Python programming, software development, debugging, and best practices. Specialized in helping with Python code, libraries, frameworks, and solving programming challenges.",
            "temperature": 0.7,
        },
        {
            "name": "Data Scientist",
            "description": "Expert in data analysis, machine learning, statistics, and data visualization. Helps with data preprocessing, model selection, feature engineering, and interpreting results.",
            "temperature": 1.0,
        },
        {
            "name": "Writing Assistant",
            "description": "Expert in writing, editing, and content creation. Specializes in grammar, style, tone, clarity, and various forms of writing including articles, reports, and creative content.",
            "temperature": 0.8,
        },
        {
            "name": "Linux System Admin",
            "description": "Expert in Linux system administration, shell scripting, server management, security, and troubleshooting. Helps with command-line operations, system configuration, and DevOps practices.",
            "temperature": 0.5,
        },
        {
            "name": "Career Coach",
            "description": "Expert in career guidance, resume writing, interview preparation, and professional development. Helps with career planning, job search strategies, and workplace advice.",
            "temperature": 1.2,
        },
        {
            "name": "Translation Expert",
            "description": "Expert in translating texts between German and English. Automatically detects the source language and translates to the other language. Handles formal and informal texts, technical documents, and everyday conversations. Provides accurate translations while preserving context and meaning.",
            "temperature": 0.3,
        },
        {
            "name": "Spell Checker",
            "description": "Expert in spell checking and text correction across multiple languages. Automatically detects the language of the input text and corrects spelling, grammar, and punctuation errors. After corrections, provides a clear summary listing all changes made with before/after examples. Supports English, German, and other major languages. Maintains the original writing style while improving accuracy.",
            "temperature": 0.2,
        },
    ]

    created = []

    for example in examples:
        try:
            # Create config
            expert_id = config_manager.create_config(
                expert_name=example["name"],
                description=example["description"],
                temperature=example["temperature"],
            )

            # Generate page
            page_path = page_generator.generate_page(
                expert_id=expert_id,
                expert_name=example["name"],
            )

            created.append({
                "name": example["name"],
                "id": expert_id,
                "page": page_path,
            })

            print(f"✅ Created: {example['name']}")
            print(f"   ID: {expert_id}")
            print(f"   Page: {page_path}")
            print()

        except Exception as e:
            print(f"❌ Error creating {example['name']}: {e}")
            print()

    return created


if __name__ == "__main__":
    print("Creating example expert agents...\n")
    print("-" * 60)

    # Copy Settings page first
    copy_settings_page()
    print()

    # Create example experts
    created = create_example_experts()

    print(f"\n✅ Successfully created {len(created)} expert(s)!")
    print("\n🎉 You can now run the app with: streamlit run Home.py")
