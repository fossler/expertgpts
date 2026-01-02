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

    # Run setup
    if python3 scripts/setup_examples.py; then
        # Success - create marker
        touch "$MARKER_FILE"
        echo ""
        echo "✅ Setup complete!"
    else
        # Setup failed
        echo ""
        echo "❌ Setup failed. Please check the errors above."
        echo "   You can try running manually: python3 scripts/setup_examples.py"
        exit 1
    fi
fi

# Launch Streamlit app (forward all arguments)
echo ""
echo "🤖 Starting ExpertGPTs..."
echo ""
streamlit run app.py "$@"
