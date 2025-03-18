#!/bin/bash
# Ergo Bounties Test Script
# This script runs the validation tools to check bounty data.

echo "Ergo Bounties Testing Tool"
echo "=========================="
echo

# Make sure scripts are executable
chmod +x src/bounty_finder.py
chmod +x src/tests/test_runner.py
chmod +x src/tests/run_bounty_check.py
chmod +x src/tests/freshness.py
chmod +x run.py

# Set up PYTHONPATH to include the current directory
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Generate files first using the main bounty finder (like run.py does)
echo "Generating files with bounty finder..."
# Force refresh to ensure we get complete data
export FORCE_REFRESH=true
# Run the main script directly
python -m src.bounty_finder

# Now run validation checks
echo -e "\nRunning validation tool..."
python -m src.tests.run_bounty_check

# Run file freshness check
echo -e "\nRunning file freshness check..."
python -m src.tests.freshness data 1
freshness_result=$?

# Run GitHub Actions compatibility check
echo -e "\nRunning GitHub Actions compatibility check..."
python -m src.tests.github_actions_check
gh_actions_result=$?

# Check final exit code
if [ $gh_actions_result -eq 0 ] && [ $freshness_result -eq 0 ]; then
  echo -e "\n✅ All tests completed successfully"
else
  echo -e "\n❌ Tests failed"
  exit 1
fi
