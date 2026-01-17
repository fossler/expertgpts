"""Reset Application Script.

This script completely resets the application by:
1. Deleting all expert configurations from configs/
2. Deleting all expert pages from pages/
3. Deleting all chat history files from chat_history/
4. Running setup.py to recreate the example experts

Use this script when you want to start fresh or restore the application to its
initial state with the default example experts.
"""

import shutil
import subprocess
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.constants import EXAMPLE_EXPERTS_COUNT


def confirm_reset():
    """Ask user to confirm the reset operation."""
    print("⚠️  WARNING: This will DELETE ALL configs, pages, and chat history!")
    print("-" * 60)
    print("This action will:")
    print("  • Delete all YAML config files in configs/")
    print("  • Delete all expert page files in pages/")
    print("  • Delete all chat history files in chat_history/")
    print(f"  • Recreate {EXAMPLE_EXPERTS_COUNT} example experts from scratch")
    print("-" * 60)

    response = input(f"\nType 'yes' to confirm, or anything else to cancel: ")
    return response.lower() == 'yes'


def delete_configs():
    """Delete all YAML configuration files."""
    configs_dir = Path("configs")

    if not configs_dir.exists():
        print("❌ Configs directory not found!")
        return False

    config_files = list(configs_dir.glob("*.yaml"))

    if not config_files:
        print("ℹ️  No config files to delete.")
        return True

    print(f"\n🗑️  Deleting {len(config_files)} config file(s)...")
    for config_file in config_files:
        config_file.unlink()
        print(f"   Deleted: {config_file.name}")

    return True


def delete_pages():
    """Delete all expert page files (excluding Home, Settings, and hidden files)."""
    pages_dir = Path("pages")

    if not pages_dir.exists():
        print("❌ Pages directory not found!")
        return False

    # Get all Python files, excluding Home (1000), Settings (9998), Help (9999), and hidden files (starting with _)
    page_files = [
        f for f in pages_dir.glob("*.py")
        if not f.name.startswith("_") and f.name not in ["1000_Home.py", "9998_Settings.py", "9999_Help.py"]
    ]

    if not page_files:
        print("ℹ️  No expert pages to delete.")
        return True

    print(f"\n🗑️  Deleting {len(page_files)} expert page(s)...")
    for page_file in page_files:
        page_file.unlink()
        print(f"   Deleted: {page_file.name}")

    return True


def delete_chat_history():
    """Delete all chat history JSON files."""
    chat_history_dir = Path("chat_history")

    if not chat_history_dir.exists():
        print("ℹ️  Chat history directory not found (no history to delete).")
        return True

    chat_files = list(chat_history_dir.glob("*.json"))

    if not chat_files:
        print("ℹ️  No chat history files to delete.")
        return True

    print(f"\n🗑️  Deleting {len(chat_files)} chat history file(s)...")
    for chat_file in chat_files:
        chat_file.unlink()
        print(f"   Deleted: {chat_file.name}")

    return True


def run_setup():
    """Run the setup.py script to perform application setup."""
    print("\n🔄 Running scripts/setup.py to set up the application...\n")
    print("-" * 60)

    try:
        # Get the script location relative to this file
        script_dir = Path(__file__).parent
        setup_script = script_dir / "setup.py"
        project_root = script_dir.parent

        # Run setup.py as a subprocess
        result = subprocess.run(
            [sys.executable, str(setup_script)],
            check=True,
            capture_output=False,
            text=True,
            cwd=project_root  # Set working directory to project root
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running setup.py: {e}")
        return False
    except FileNotFoundError:
        print("❌ setup.py not found!")
        return False


def main():
    """Main reset function."""
    print("\n" + "=" * 60)
    print("🔄 ExpertGPTs Application Reset")
    print("=" * 60)

    # Confirm before proceeding
    if not confirm_reset():
        print("\n❌ Reset cancelled.")
        return 1

    print("\n✅ Reset confirmed. Proceeding...\n")

    # Delete configs
    if not delete_configs():
        print("\n❌ Failed to delete configs. Aborting.")
        return 1

    # Delete pages
    if not delete_pages():
        print("\n❌ Failed to delete pages. Aborting.")
        return 1

    # Delete chat history
    if not delete_chat_history():
        print("\n❌ Failed to delete chat history. Aborting.")
        return 1

    # Recreate example experts
    if not run_setup():
        print("\n❌ Failed to recreate example experts.")
        return 1

    print("\n" + "=" * 60)
    print("✅ Application reset successfully!")
    print("=" * 60)
    print("\n🎉 You can now run the app with: streamlit run app.py\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
