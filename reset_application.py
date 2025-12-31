"""Reset Application Script.

This script completely resets the application by:
1. Deleting all expert configurations from configs/
2. Deleting all expert pages from pages/
3. Running setup_examples.py to recreate the example experts

Use this script when you want to start fresh or restore the application to its
initial state with the default example experts.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def confirm_reset():
    """Ask user to confirm the reset operation."""
    print("⚠️  WARNING: This will DELETE ALL configs and pages!")
    print("-" * 60)
    print("This action will:")
    print("  • Delete all YAML config files in configs/")
    print("  • Delete all expert page files in pages/")
    print("  • Recreate 7 example experts from scratch")
    print("-" * 60)

    response = input("\nType 'yes' to confirm, or anything else to cancel: ")
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
    """Delete all expert page files (excluding Home.py and hidden files)."""
    pages_dir = Path("pages")

    if not pages_dir.exists():
        print("❌ Pages directory not found!")
        return False

    # Get all Python files, excluding Home.py and hidden files (starting with _)
    page_files = [
        f for f in pages_dir.glob("*.py")
        if not f.name.startswith("_") and f.name != "Home.py"
    ]

    if not page_files:
        print("ℹ️  No expert pages to delete.")
        return True

    print(f"\n🗑️  Deleting {len(page_files)} expert page(s)...")
    for page_file in page_files:
        page_file.unlink()
        print(f"   Deleted: {page_file.name}")

    return True


def run_setup_examples():
    """Run the setup_examples.py script to recreate example experts."""
    print("\n🔄 Running setup_examples.py to recreate example experts...\n")
    print("-" * 60)

    try:
        # Run setup_examples.py as a subprocess
        result = subprocess.run(
            [sys.executable, "setup_examples.py"],
            check=True,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running setup_examples.py: {e}")
        return False
    except FileNotFoundError:
        print("❌ setup_examples.py not found!")
        return False


def main():
    """Main reset function."""
    print("\n" + "=" * 60)
    print("🔄 DeepAgents Application Reset")
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

    # Recreate example experts
    if not run_setup_examples():
        print("\n❌ Failed to recreate example experts.")
        return 1

    print("\n" + "=" * 60)
    print("✅ Application reset successfully!")
    print("=" * 60)
    print("\n🎉 You can now run the app with: streamlit run Home.py\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
