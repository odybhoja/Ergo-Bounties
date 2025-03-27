#!/bin/bash
# Ergo Bounties Test Script with Dynamic CLI Metrics Table
# This script runs the validation tools to check bounty data and then dynamically updates a sexy table with metrics: number of orgs, repos, issues, bounties, and amounts.
# It uses ANSI escape codes for colours and updates the table periodically.

# Define colours for use with ANSI escape codes.
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[1;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

# Clear the terminal screen for a fresh look.
clear

# Function to print the header of the metrics table.
# Corrected border lengths and characters
print_table_header() {
  printf "${BLUE}┏────────────────────────────────────────────────────┓\n" # 44 dashes
  printf "┃ %-50s ┃\n" "Ergo Bounties Metrics Dashboard" # Width 44
  printf "┡──────────────────┯────────────┯───────────┯────────┩\n" # 16-10-9-6 dashes
  printf "│ %-16s │ %-10s │ %-9s │ %-6s │\n" "Metric" "Value" "Unit" "Status"
  printf "├──────────────────┼────────────┼───────────┼────────┤\n" # 16-10-9-6 dashes
}

# Function to print a table row for a metric.
# Arguments: metric name, value, unit (optional), status (optional)
# Manually calculate padding for status column to handle ANSI codes correctly
print_metric_row() {
    local name="$1"
    local value="$2"
    local unit="${3:-}"   # Default to empty string if not provided
    local status="${4:-}" # Default to empty string if not provided
    local status_col_width=6

    # Print the first part of the row
    printf "│ %-16s │ %-10s │ %-9s │ " "$name" "$value" "$unit"

    # Print status with manual padding
    echo -e -n "$status" # Print status without newline, interpreting ANSI codes

    # Calculate visible length of status (strip ANSI codes)
    local visible_status=$(echo -e "$status" | sed 's/\x1b\[[0-9;]*m//g')
    local visible_len=${#visible_status}

    # Calculate padding
    local padding_len=$((status_col_width - visible_len))
    if [ $padding_len -lt 0 ]; then padding_len=0; fi # Ensure padding isn't negative

    # Print padding spaces
    printf "%*s" $padding_len ""

    # Print closing border and newline
    printf " │\n"
}

# Function to print the footer of the table.
# Corrected border lengths and characters
print_table_footer() {
    printf "└──────────────────┴────────────┴───────────┴────────┘${NC}\n" # 16-10-9-6 dashes
    printf "${YELLOW}Press Ctrl+C to exit${NC}\n"
}

# Function to fetch current metrics.
fetch_metrics() {
  BOUNTIES=$(grep -F "| **Total**" data/summary.md | awk '{gsub(/\*/,""); print $4}')
  # Remove commas from AMOUNTS as well
  AMOUNTS=$(grep -F "| **Total**" data/summary.md | awk '{gsub(/\*|,/,""); print $6}')
  TRACKED_REPOS=$(jq '. | length' src/config/tracked_repos.json)
  TRACKED_ORGS=$(jq '. | length' src/config/tracked_orgs.json)

  # Fetch currency prices (extracting the second column - ERG Equivalent)
  SIGUSD_PRICE=$(grep -F "SigUSD" data/currency_prices.md | sed -n 's/.*|\s*[^|]*\s*|\s*\([^|]*\)\s*|\s*[^|]*\s*|.*/\1/p')
  GORT_PRICE=$(grep -F "GORT" data/currency_prices.md | sed -n 's/.*|\s*[^|]*\s*|\s*\([^|]*\)\s*|\s*[^|]*\s*|.*/\1/p')
  RSN_PRICE=$(grep -F "RSN" data/currency_prices.md | sed -n 's/.*|\s*[^|]*\s*|\s*\([^|]*\)\s*|\s*[^|]*\s*|.*/\1/p')
  BENE_PRICE=$(grep -F "BENE" data/currency_prices.md | sed -n 's/.*|\s*[^|]*\s*|\s*\([^|]*\)\s*|\s*[^|]*\s*|.*/\1/p')
  GGOLD_PRICE=$(grep -F "gGOLD" data/currency_prices.md | sed -n 's/.*|\s*[^|]*\s*|\s*\([^|]*\)\s*|\s*[^|]*\s*|.*/\1/p')
}

# Function to update the metrics table.
update_dashboard() {
  # Clear the terminal completely using ANSI escape code.
  printf "\033c"
  print_table_header
  fetch_metrics
  print_metric_row "Bounties" "$BOUNTIES" "count"
  print_metric_row "Total Amount" "$AMOUNTS" "ERG"
  print_metric_row "Tracked Repos" "$TRACKED_REPOS" "count"
  print_metric_row "Tracked Orgs" "$TRACKED_ORGS" "count"

  print_metric_row "SigUSD Price" "$SIGUSD_PRICE" "ERG"
  print_metric_row "GORT Price" "$GORT_PRICE" "ERG"
  print_metric_row "RSN Price" "$RSN_PRICE" "ERG"
  print_metric_row "BENE Price" "$BENE_PRICE" "ERG"
  print_metric_row "gGOLD Price" "$GGOLD_PRICE" "ERG"

    # Define colorized checkmark and X
  CHECKMARK="${GREEN}✔${NC}"
  CROSS="${RED}✗${NC}"

  # Pass checkmark/cross as the 4th argument (Status), leave Unit (3rd arg) blank
  print_metric_row "Validation Tool" "$VALIDATION_STATUS" "" "$( [ "$VALIDATION_STATUS" = "Passed" ] && echo "$CHECKMARK" || echo "$CROSS" )"
  print_metric_row "Freshness Check" "$FRESHNESS_STATUS" "" "$( [ "$FRESHNESS_STATUS" = "Passed" ] && echo "$CHECKMARK" || echo "$CROSS" )"
  print_metric_row "GitHub Actions" "$GHA_STATUS" "" "$( [ "$GHA_STATUS" = "Passed" ] && echo "$CHECKMARK" || echo "$CROSS" )"
  # Add Unit Tests status row
  print_metric_row "Unit Tests" "$UNIT_TEST_STATUS" "" "$( [ "$UNIT_TEST_STATUS" = "Passed" ] && echo "$CHECKMARK" || echo "$CROSS" )"
  # Add API Connectivity status row
  print_metric_row "API Checks" "$API_STATUS" "" "$( [ "$API_STATUS" = "Passed" ] && echo "$CHECKMARK" || echo "$CROSS" )"
  print_table_footer
}

# Begin test environment initialization and run tests
echo -e "\nInitializing test environment..."

# Ensure required scripts are executable
chmod +x src/bounty_finder.py
# chmod +x src/tests/test_runner.py # Removed as file is deleted
chmod +x src/tests/run_bounty_check.py
chmod +x src/tests/freshness.py
chmod +x src/tests/check_apis.py # Added
chmod +x run.py
echo "Scripts permissions set."

# Set PYTHONPATH to include the current directory.
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
echo "PYTHONPATH updated."

# Generate files using the bounty finder.
echo "Generating files with bounty finder..."
export FORCE_REFRESH=true
python -m src.bounty_finder
echo "File generation completed."

# Run validation checks.
echo "Running validation tool..."
if python -m src.tests.run_bounty_check &> /dev/null; then
  VALIDATION_STATUS="Passed"
else
  VALIDATION_STATUS="Failed"
fi
echo "Validation completed."

# Run file freshness check.
echo "Running file freshness check..."
if python -m src.tests.freshness data 1 &> /dev/null; then
  FRESHNESS_STATUS="Passed"
else
  FRESHNESS_STATUS="Failed"
fi
echo "Freshness check completed."

# Run GitHub Actions compatibility check.
echo "Running GitHub Actions compatibility check..."
if python -m src.tests.github_actions_check &> /dev/null; then
    GHA_STATUS="Passed"
  else
    GHA_STATUS="Failed"
  fi
echo "GitHub Actions check completed."

# Run Python unit tests using pytest.
echo "Running Python unit tests with pytest..."
# Run tests verbosely with pytest, capture output
UNIT_TEST_OUTPUT=$(pytest -v src/tests 2>&1)
if [ $? -eq 0 ]; then
  UNIT_TEST_STATUS="Passed"
else
  UNIT_TEST_STATUS="Failed"
  # Optionally print output only on failure
  echo -e "${RED}Unit tests failed:\n$UNIT_TEST_OUTPUT${NC}"
fi
echo "Unit tests completed."

# Run API connectivity check.
echo "Running API connectivity check..."
# Run check, capture output to avoid cluttering main output unless failed
API_CHECK_OUTPUT=$(python -m src.tests.check_apis 2>&1)
if [ $? -eq 0 ]; then
  API_STATUS="Passed"
else
  API_STATUS="Failed"
  # Optionally print output only on failure
  echo -e "${RED}API connectivity check failed:\n$API_CHECK_OUTPUT${NC}"
fi
echo "API connectivity check completed."


# Check if all tests passed
if [ "$VALIDATION_STATUS" = "Passed" ] && [ "$FRESHNESS_STATUS" = "Passed" ] && [ "$GHA_STATUS" = "Passed" ] && [ "$UNIT_TEST_STATUS" = "Passed" ] && [ "$API_STATUS" = "Passed" ]; then
  echo -e "\n${GREEN}All tests completed successfully.${NC}"
else
  echo -e "\n${RED}One or more tests failed.${NC}"
fi

update_dashboard
