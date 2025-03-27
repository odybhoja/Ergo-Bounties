#!/usr/bin/env python3
"""
API Connectivity Check Script

This script checks the basic reachability of external APIs used by the bounty finder.
It performs simple HEAD requests to the base URLs.
Exits with 0 if all APIs are reachable, 1 otherwise.
"""

import sys
import requests
import logging

# Configure logging for this script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# APIs to check {Name: Base URL}
APIS_TO_CHECK = {
    "GitHub API": "https://api.github.com",
    "Spectrum API": "https://api.spectrum.fi",
    "Ergo Explorer API": "https://api.ergoplatform.com/api"
}

TIMEOUT = 10  # seconds

def check_api(name: str, url: str) -> bool:
    """Checks connectivity to a single API endpoint using a HEAD request."""
    logger.info(f"Checking connectivity to {name} ({url})...")
    try:
        response = requests.head(url, timeout=TIMEOUT)
        # Consider any non-5xx status code as reachable for a basic check
        if response.status_code < 500:
            logger.info(f"{name} is reachable (Status: {response.status_code}).")
            return True
        else:
            logger.error(f"{name} returned status {response.status_code}.")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to {name}: {e}")
        return False

def main():
    """Runs connectivity checks for all defined APIs."""
    all_reachable = True
    for name, url in APIS_TO_CHECK.items():
        if not check_api(name, url):
            all_reachable = False

    if all_reachable:
        logger.info("All APIs checked are reachable.")
        sys.exit(0)
    else:
        logger.error("One or more APIs are unreachable.")
        sys.exit(1)

if __name__ == "__main__":
    main()
