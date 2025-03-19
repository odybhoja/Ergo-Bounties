#!/usr/bin/env python3
"""
GitHub API Client Module

This module handles all interactions with the GitHub API, including fetching repositories,
issues, and language data. It implements rate limiting handling, error recovery, and
provides a clean interface for the rest of the application.

Primary interactions:
- Fetching organization repositories
- Fetching repository language information
- Fetching issues from repositories
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

from src.api.base_client import BaseClient

# Configure logging
logger = logging.getLogger(__name__)


class GitHubClient(BaseClient):
    """
    Client for interacting with the GitHub API.
    Handles authentication, rate limiting, and provides methods for common API operations.
    """

    def __init__(self, token: str, max_retries: int = 3, retry_delay: int = 5):
        """
        Initialize the GitHub API client.

        Args:
            token: GitHub API token for authentication
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay in seconds between retries
        """
        super().__init__(
            base_url="https://api.github.com",
            timeout=30,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )
        self.token = token
        self.session.headers.update({"Authorization": f"token {token}"})

    def get_organization_repos(self, org: str) -> List[Dict[str, Any]]:
        """
        Get all repositories for an organization.

        Args:
            org: Organization name

        Returns:
            List of repository objects
        """
        url = f"/orgs/{org}/repos?per_page=100"
        all_repos = []

        logger.info(f"Fetching repositories for organization: {org}")

        while url:
            data, links = self._make_request(url)
            if not data:
                break

            all_repos.extend(data)
            url = links.get("next", {}).get("url") if links else None

            logger.debug(
                f"Fetched {len(data)} repositories from {org}, total: {len(all_repos)}"
            )

        logger.info(f"Successfully fetched {len(all_repos)} repositories from {org}")
        return all_repos

    def get_repository_languages(self, owner: str, repo: str) -> List[str]:
        """
        Get languages used in a repository, sorted by usage.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of languages (top 2 by usage)
        """
        url = f"/repos/{owner}/{repo}/languages"

        logger.debug(f"Fetching languages for repository: {owner}/{repo}")

        data, _ = self._make_request(url)
        if not data:
            return []
            
        # Sort languages by bytes of code and get top 2 (or all if fewer than 2)
        sorted_languages = sorted(data.items(), key=lambda x: x[1], reverse=True)
        result = [lang[0] for lang in sorted_languages]
        
        logger.debug(f"Languages for {owner}/{repo}: {result}")
        return result[:2]

    def get_repository_issues(
        self, owner: str, repo: str, state: str = "open"
    ) -> List[Dict[str, Any]]:
        """
        Get issues from a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)

        Returns:
            List of issue objects
        """
        url = f"/repos/{owner}/{repo}/issues?state={state}&per_page=100"
        all_issues = []

        logger.info(f"Fetching {state} issues from repository: {owner}/{repo}")

        while url:
            data, links = self._make_request(url)
            if not data:
                break

            all_issues.extend(data)
            url = links.get("next", {}).get("url") if links else None

            logger.debug(
                f"Fetched {len(data)} issues from {owner}/{repo}, total: {len(all_issues)}"
            )

        logger.info(f"Successfully fetched {len(all_issues)} issues from {owner}/{repo}")
        return all_issues
