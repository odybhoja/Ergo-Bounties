#!/bin/bash
# Ergo Bounties Test Script
# This script runs the validation tools to check bounty data.

echo "Ergo Bounties Testing Tool"
echo "=========================="
echo

# Make sure scripts are executable
chmod +x scripts/bounty_finder.py
chmod +x scripts/tests/test_runner.py
chmod +x scripts/tests/run_bounty_check.py

# Check if we want verbose output
if [[ "$1" == "--verbose" ]]; then
  echo "Running test runner with verbose output..."
  python scripts/tests/test_runner.py --verbose
else
  # Run the full validation tool by default
  echo "Running full validation tool..."
  python scripts/tests/run_bounty_check.py
fi

# Run GitHub Actions compatibility check
echo -e "\nRunning GitHub Actions compatibility check..."
python scripts/tests/github_actions_check.py
gh_actions_result=$?

# Check final exit code
if [ $? -eq 0 ] && [ $gh_actions_result -eq 0 ]; then
  echo -e "\n✅ All tests completed successfully"
else
  echo -e "\n❌ Tests failed"
  exit 1
fi
