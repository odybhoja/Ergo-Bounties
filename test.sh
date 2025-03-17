#!/bin/bash
# Simple wrapper script to run the bounty validation tool

# Set terminal colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}═════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}                      ERGO BOUNTIES VALIDATION TOOL                          ${NC}"
echo -e "${CYAN}═════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Running bounty validation check...${NC}"
echo ""

# Make the Python script executable if it isn't already
chmod +x scripts/tests/run_bounty_check.py

# Run the Python script
python3 scripts/tests/run_bounty_check.py

# Store the exit code
exit_code=$?

# Exit with the same code
exit $exit_code
