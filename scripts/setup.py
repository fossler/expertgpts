"""Setup script to create example expert agents.

Run this script to populate the app with example Domain Expert Agents.
"""

import shutil
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config_manager import ConfigManager
from utils.page_generator import PageGenerator
from utils.helpers import sanitize_name
from utils.constants import EXAMPLE_EXPERTS_COUNT


def copy_settings_page():
    """Copy the Settings page from templates to pages directory."""
    template_settings = Path("templates/9999_Settings.py")
    pages_settings = Path("pages/9999_Settings.py")

    if template_settings.exists():
        shutil.copy2(template_settings, pages_settings)
        print(f"✅ Copied Settings page to pages/")
    else:
        print(f"⚠️  Warning: Settings template not found at {template_settings}")


def copy_home_page():
    """Copy the Home page from templates to pages directory."""
    template_home = Path("templates/1000_Home.py")
    pages_home = Path("pages/1000_Home.py")

    if template_home.exists():
        shutil.copy2(template_home, pages_home)
        print(f"✅ Copied Home page to pages/")
    else:
        print(f"⚠️  Warning: Home template not found at {template_home}")


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
            # Get next page number (doesn't create file)
            page_number = page_generator.get_next_page_number()

            # Calculate expert_id
            expert_id = f"{page_number}_{sanitize_name(example['name'])}"

            # Create configuration (uses page_number for naming)
            config_manager.create_config(
                expert_name=example["name"],
                description=example["description"],
                temperature=example["temperature"],
                page_number=page_number,
            )

            # Create page with correct expert_id from the start (no workaround needed!)
            page_path, _ = page_generator.generate_page(
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

    # Ensure pages directory exists before any file operations
    Path("pages").mkdir(exist_ok=True)

    # Copy Home page first (so experts start at 1001)
    copy_home_page()
    print()

    # Copy Settings page
    copy_settings_page()
    print()

    # Create example experts
    created = create_example_experts()

    # Verify we created the expected number of experts
    if len(created) != EXAMPLE_EXPERTS_COUNT:
        print(f"⚠️  Warning: Expected {EXAMPLE_EXPERTS_COUNT} experts, but created {len(created)}")
        print("   Please update EXAMPLE_EXPERTS_COUNT in utils/constants.py")

    print(f"\n✅ Successfully created {len(created)} expert(s)!")
    print("\n🎉 You can now run the app with: streamlit run app.py")
