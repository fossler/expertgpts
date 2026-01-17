"""Setup script to create example expert agents.

Run this script to populate the app with example Domain Expert Agents.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config_manager import ConfigManager
from utils.page_generator import PageGenerator
from utils.helpers import sanitize_name
from utils.constants import EXAMPLE_EXPERTS_COUNT


def should_create_example_experts() -> bool:
    """Check if example experts should be created.

    Returns True if no expert pages exist (pages/ only contains Home and Settings).
    """
    pages_dir = Path("pages")
    if not pages_dir.exists():
        return True

    # Check if expert pages exist (excluding Home and Settings)
    expert_pages = [
        f for f in pages_dir.glob("*.py")
        if f.name not in ["1000_Home.py", "9998_Settings.py", "9999_Help.py"]
        and not f.name.startswith("_")
    ]

    return len(expert_pages) == 0


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
            "name": "General Assistant",
            "description": "A helpful general-purpose assistant for everyday questions and tasks. Provides friendly, accurate assistance across a wide range of topics including general knowledge, problem-solving, and creative tasks.",
            "temperature": 1.0,
            "system_prompt": "You are a helpful assistant.",
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
            config_kwargs = {
                "expert_name": example["name"],
                "description": example["description"],
                "temperature": example["temperature"],
                "page_number": page_number,
            }

            # Add system_prompt if provided
            if "system_prompt" in example:
                config_kwargs["system_prompt"] = example["system_prompt"]

            config_manager.create_config(**config_kwargs)

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
    print("Setting up ExpertGPTs...\n")
    print("-" * 60)

    # Ensure pages directory exists
    Path("pages").mkdir(exist_ok=True)

    # Verify Home and Settings exist (they should be in git)
    home_page = Path("pages/1000_Home.py")
    settings_page = Path("pages/9998_Settings.py")

    if not home_page.exists():
        print("⚠️  Warning: Home page not found at pages/1000_Home.py")
        print("   This file should be in the repository. Please check your git checkout.")

    if not settings_page.exists():
        print("⚠️  Warning: Settings page not found at pages/9998_Settings.py")
        print("   This file should be in the repository. Please check your git checkout.")

    print()

    # Smart recreation: only create experts if none exist
    if should_create_example_experts():
        print("No expert pages found. Creating example experts...\n")
        created = create_example_experts()

        # Verify we created the expected number of experts
        if len(created) != EXAMPLE_EXPERTS_COUNT:
            print(f"⚠️  Warning: Expected {EXAMPLE_EXPERTS_COUNT} experts, but created {len(created)}")
            print("   Please update EXAMPLE_EXPERTS_COUNT in utils/constants.py")

        print(f"\n✅ Successfully created {len(created)} expert(s)!")
    else:
        print("ℹ️  Expert pages already exist. Skipping example expert creation.")
        print("   To recreate experts, use: python3 scripts/reset_application.py")

    print("\n🎉 You can now run the app with: streamlit run app.py")
