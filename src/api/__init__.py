"""
API Clients Package

This package contains clients for various APIs used by the application:
- GitHub API client for fetching repository and issue data
- Currency API client for fetching exchange rates
"""

from .github_client import GitHubClient
from .currency_client import CurrencyClient
