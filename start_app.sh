#!/bin/bash
# ExpertGPTs Application Launcher
# This script handles first-time setup before launching the app

set -e  # Exit on error

# Get the project root directory (script location)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Check for setup marker
MARKER_FILE=".setup_complete"

if [ ! -f "$MARKER_FILE" ]; then
    echo ""
    echo "🚀 First run detected - setting up ExpertGPTs..."
    echo "   This will create 7 example expert agents."
    echo ""

    # Check for existing auto-generated files and clean them up
    PAGES_DIR="pages"
    CONFIGS_DIR="configs"

    # Check and clean pages directory
    if [ -d "$PAGES_DIR" ]; then
        # Count expert pages (exclude Home: 1000, Settings: 9999, and hidden files)
        EXPERT_COUNT=$(find "$PAGES_DIR" -maxdepth 1 -type f -name "*.py" ! -name "1000_Home.py" ! -name "9999_Settings.py" ! -name ".*" | wc -l | tr -d ' ')

        if [ "$EXPERT_COUNT" -gt 0 ]; then
            echo ""
            echo "🧹 Found $EXPERT_COUNT existing expert page(s). Cleaning up..."
            find "$PAGES_DIR" -maxdepth 1 -type f -name "*.py" ! -name "1000_Home.py" ! -name "9999_Settings.py" ! -name ".*" -delete
            echo "   ✅ Removed existing expert pages"
        fi
    fi

    # Check and clean configs directory
    if [ -d "$CONFIGS_DIR" ]; then
        CONFIG_COUNT=$(find "$CONFIGS_DIR" -maxdepth 1 -type f -name "*.yaml" | wc -l | tr -d ' ')

        if [ "$CONFIG_COUNT" -gt 0 ]; then
            echo ""
            echo "🧹 Found $CONFIG_COUNT existing config file(s). Cleaning up..."
            find "$CONFIGS_DIR" -maxdepth 1 -type f -name "*.yaml" -delete
            echo "   ✅ Removed existing config files"
        fi
    fi

    echo ""

    # Run setup
    if python3 scripts/setup.py; then
        # Success - create marker
        touch "$MARKER_FILE"
        echo ""
        echo "✅ Setup complete!"
    else
        # Setup failed
        echo ""
        echo "❌ Setup failed. Please check the errors above."
        echo "   You can try running manually: python3 scripts/setup.py"
        exit 1
    fi
fi

# Launch Streamlit app (forward all arguments)
echo ""
echo "🤖 Starting ExpertGPTs..."
echo ""
streamlit run app.py "$@"
