#!/usr/bin/env python3
"""ExpertGPTs Application Launcher.

This script handles first-time setup before launching the app.
Python equivalent of start_app.sh
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Main entry point for the application launcher."""

    # Get the project root directory (script location)
    project_root = Path(__file__).parent.resolve()
    import os
    os.chdir(project_root)

    # Check for setup marker
    marker_file = project_root / ".setup_complete"

    if not marker_file.exists():
        print("")
        print("🚀 First run detected - setting up ExpertGPTs...")
        print("   This will create 7 example expert agents.")
        print("")

        # Check for existing auto-generated files and clean them up
        pages_dir = project_root / "pages"
        configs_dir = project_root / "configs"

        # Check and clean pages directory
        if pages_dir.exists():
            # Count expert pages (exclude Home: 1000, Settings: 9999, and hidden files)
            expert_pages = [
                f for f in pages_dir.glob("*.py")
                if f.name not in ["1000_Home.py", "9999_Settings.py"]
                and not f.name.startswith(".")
            ]

            if expert_pages:
                print("")
                print(f"🧹 Found {len(expert_pages)} existing expert page(s). Cleaning up...")
                for page in expert_pages:
                    page.unlink()
                print("   ✅ Removed existing expert pages")

        # Check and clean configs directory
        if configs_dir.exists():
            config_files = list(configs_dir.glob("*.yaml"))

            if config_files:
                print("")
                print(f"🧹 Found {len(config_files)} existing config file(s). Cleaning up...")
                for config in config_files:
                    config.unlink()
                print("   ✅ Removed existing config files")

        print("")

        # Run setup
        try:
            result = subprocess.run(
                [sys.executable, "scripts/setup.py"],
                cwd=project_root,
                check=True,
                capture_output=False,
            )

            # Success - create marker
            marker_file.touch()
            print("")
            print("✅ Setup complete!")

        except subprocess.CalledProcessError:
            # Setup failed
            print("")
            print("❌ Setup failed. Please check the errors above.")
            print("   You can try running manually: python3 scripts/setup.py")
            sys.exit(1)

    # Launch Streamlit app (forward all arguments)
    print("")
    print("🤖 Starting ExpertGPTs...")
    print("")

    # Forward all arguments to streamlit
    streamlit_cmd = ["streamlit", "run", "app.py"] + sys.argv[1:]

    try:
        subprocess.run(streamlit_cmd, cwd=project_root)
    except KeyboardInterrupt:
        print("\n")
        print("👋 ExpertGPTs stopped by user.")
        sys.exit(0)
    except SystemExit:
        # Streamlit exited normally (e.g., via browser close)
        sys.exit(0)


if __name__ == "__main__":
    main()
