"""
Ergo Bounty Finder

This package contains scripts and modules for finding, processing, and generating reports
for Ergo ecosystem bounties. The main components are:

1. API Clients - For interacting with GitHub and other external APIs
2. Core - Core application logic for processing bounties
3. Generators - For generating markdown output files
4. Utils - Utility functions used throughout the application

The main entry point is bounty_finder.py which orchestrates the entire process.
"""

# Re-export main functionality for easier imports
from .api import GitHubClient, CurrencyClient
from .core import BountyConfig, BountyProcessor, BountyExtractor
