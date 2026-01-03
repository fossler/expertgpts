#!/bin/bash
# Cleanup script for development
# Removes all expert pages and configs, keeping only Home and Settings

set -e  # Exit on error

# Get the project root directory (script location)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
cd "$PROJECT_ROOT"

echo "🧹 Cleaning up expert pages and configs..."
echo ""

# Clean pages directory
if [ -d "pages" ]; then
    PAGE_COUNT=$(find pages -maxdepth 1 -type f -name "*.py" ! -name "1000_Home.py" ! -name "9999_Settings.py" ! -name ".*" | wc -l | tr -d ' ')

    if [ "$PAGE_COUNT" -gt 0 ]; then
        echo "   Removing $PAGE_COUNT expert page(s)..."
        find pages -maxdepth 1 -type f -name "*.py" ! -name "1000_Home.py" ! -name "9999_Settings.py" ! -name ".*" -delete
        echo "   ✅ Removed expert pages"
    else
        echo "   ℹ️  No expert pages to remove"
    fi
fi

# Clean configs directory
if [ -d "configs" ]; then
    CONFIG_COUNT=$(find configs -maxdepth 1 -type f -name "*.yaml" 2>/dev/null | wc -l | tr -d ' ')

    if [ "$CONFIG_COUNT" -gt 0 ]; then
        echo "   Removing $CONFIG_COUNT config file(s)..."
        find configs -maxdepth 1 -type f -name "*.yaml" -delete
        echo "   ✅ Removed config files"
    else
        echo "   ℹ️  No config files to remove"
    fi
fi

# Remove setup marker to trigger first-run setup on next start
if [ -f ".setup_complete" ]; then
    rm .setup_complete
    echo "   🗑️  Removed setup marker"
fi

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Remaining files:"
echo "   Pages:"
ls -1 pages/*.py 2>/dev/null || echo "      None"
echo ""
echo "   Configs:"
ls -1 configs/*.yaml 2>/dev/null || echo "      None"
echo ""
echo "🚀 Run './start_app.sh' or 'python3 scripts/setup.py' to recreate experts"
