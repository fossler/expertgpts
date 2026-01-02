#!/bin/bash
# Script to run tests for ExpertGPTs

# Activate virtual environment
source .venv/bin/activate

# Run tests with verbose output
echo "Running ExpertGPTs test suite..."
echo "=================================="

python -m pytest -v

# Exit with pytest's exit code
exit $?
