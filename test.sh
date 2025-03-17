#!/bin/bash
# Ergo Bounties Test Script
# This script runs the validation tools to check bounty data.

echo "Ergo Bounties Testing Tool"
echo "=========================="
echo

# Make sure scripts are executable
chmod +x src/bounty_finder.py
chmod +x tests/test_runner.py
chmod +x tests/run_bounty_check.py
chmod +x tests/freshness.py
chmod +x run.py

# Set up PYTHONPATH to include the current directory
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Check if we want verbose output
if [[ "$1" == "--verbose" ]]; then
  echo "Running test runner with verbose output..."
  python -m tests.test_runner --verbose
else
  # Run the full validation tool by default
  echo "Running full validation tool..."
  python -m tests.run_bounty_check
fi

# Run file freshness check
echo -e "\nRunning file freshness check..."
python -m tests.freshness data 1
freshness_result=$?

# Run GitHub Actions compatibility check
echo -e "\nRunning GitHub Actions compatibility check..."
python -m tests.github_actions_check
gh_actions_result=$?

# Check final exit code
if [ $gh_actions_result -eq 0 ] && [ $freshness_result -eq 0 ]; then
  echo -e "\n✅ All tests completed successfully"
else
  echo -e "\n❌ Tests failed"
  exit 1
fi
