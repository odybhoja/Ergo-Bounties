#!/usr/bin/env python3
"""
Bounty Processor Module

This module is the core of the bounty finder system. It:
- Processes GitHub repositories and organizations to find bounties
- Extracts and normalizes bounty information
- Organizes bounties by various criteria (language, organization, currency)
- Calculates statistics and aggregates data

The processor acts as a bridge between the data sources (GitHub API) and 
the generators that create the output markdown files.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Set

from ..api.github_client import GitHubClient
from ..api.currency_client import CurrencyClient
from .extractors import is_bounty_issue, extract_bounty_info

# Configure logging
logger = logging.getLogger(__name__)

class BountyProcessor:
    """
    Processor for bounty data.
    Handles fetching and processing bounty information from GitHub.
    """

    def __init__(self, github_token: str, rates: Dict[str, float]):
        """
        Initialize the bounty processor.

        Args:
            github_token: GitHub API token
            rates: Dictionary of currency conversion rates
        """
        self.github_client = GitHubClient(github_token)
        self.currency_client = CurrencyClient()
        self.currency_client.rates = rates  # Use provided rates
        self.bounty_data = []
        self.project_totals = {}
        self.reserved_count = 0

    def process_repositories(self, repos_to_query: List[Dict[str, str]]) -> None:
        """
        Process repositories to find bounties.

        Args:
            repos_to_query: List of repository objects with 'owner' and 'repo' keys
        """
        for repo in repos_to_query:
            owner = repo['owner']
            repo_name = repo['repo']

            logger.info(f"Processing {owner}/{repo_name}...")

            # Get repository languages
            languages = self.github_client.get_repository_languages(owner, repo_name)
            primary_lang = languages[0] if languages else "Unknown"
            secondary_lang = languages[1] if len(languages) > 1 else "None"

            # Initialize project counter if not exists
            if owner not in self.project_totals:
                self.project_totals[owner] = {"count": 0, "value": 0.0}

            # Get issues
            issues = self.github_client.get_repository_issues(owner, repo_name)

            # Process each issue
            for issue in issues:
                self._process_issue(issue, owner, repo_name, primary_lang, secondary_lang)
        print(f"Reserved bounties: {self.reserved_count}")

    def process_organizations(self, orgs_to_query: List[Dict[str, str]], repos_to_query: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Process organizations to find repositories.

        Args:
            orgs_to_query: List of organization objects with 'org' key
            repos_to_query: Current list of repositories

        Returns:
            Updated list of repositories
        """
        updated_repos = repos_to_query.copy()
        processed_repos = {f"{repo['owner']}/{repo['repo']}" for repo in repos_to_query}

        for org_entry in orgs_to_query:
            org = org_entry['org']
            logger.info(f"Fetching repositories for organization: {org}")

            org_repos = self.github_client.get_organization_repos(org)
            for repo in org_repos:
                # Skip archived repositories
                if repo.get('archived', False):
                    logger.debug(f"Skipping archived repository: {org}/{repo['name']}")
                    continue

                # Skip forks if they don't have issues
                if repo.get('fork', False) and not repo.get('has_issues', False):
                    logger.debug(f"Skipping fork without issues: {org}/{repo['name']}")
                    continue

                # Add to repos_to_query if not already there
                repo_id = f"{org}/{repo['name']}"
                if repo_id not in processed_repos:
                    logger.info(f"Adding repository from organization: {repo_id}")
                    repo_entry = {"owner": org, "repo": repo['name']}
                    updated_repos.append(repo_entry)
                    processed_repos.add(repo_id)

        return updated_repos

    def _process_issue(self, issue: Dict[str, Any], owner: str, repo_name: str, primary_lang: str, secondary_lang: str) -> None:
        """
        Process a single issue to check if it's a bounty.

        Args:
            issue: Issue object from GitHub API
            owner: Repository owner
            repo_name: Repository name
            primary_lang: Primary language of the repository
            secondary_lang: Secondary language of the repository
        """
        if issue['state'] == 'open':
            # Instead of checking pull requests, check if a JSON exists in the submissions folder for this issue
            import os
            submission_path = "submissions"
            issue_number_str = str(issue['number'])
            found_submission = False
            if os.path.isdir(submission_path):
                for filename in os.listdir(submission_path):
                    if filename.endswith(".json") and issue_number_str in filename:
                        found_submission = True
                        break
            if found_submission:
                issue['state'] = 'Reserved'

            title = issue['title']
            labels = issue['labels']

            # Check if this is a bounty issue
            if is_bounty_issue(title, labels):
                title = title.replace(",", " ")

                # Extract bounty information
                amount, currency = extract_bounty_info(issue)

                # Store the bounty information
                bounty_info = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "owner": owner,
                    "repo": repo_name,
                    "title": title,
                    "url": issue['html_url'],
                    "amount": amount,
                    "currency": currency,
                    "primary_lang": primary_lang,
                    "secondary_lang": secondary_lang,
                    "labels": [label['name'] for label in labels],
                    "issue_number": issue['number'],
                    "creator": issue['user']['login'],  # GitHub username of the issue creator
                    "status": issue['state']  # Add status
                }

                self.bounty_data.append(bounty_info)

                # Update project totals
                self.project_totals[owner]["count"] += 1

                # Calculate ERG value for totals
                erg_value = self.currency_client.calculate_erg_value(amount, currency)
                self.project_totals[owner]["value"] += erg_value

    def get_bounty_data(self) -> List[Dict[str, Any]]:
        """
        Get the processed bounty data.

        Returns:
            List of bounty information dictionaries
        """
        return self.bounty_data

    def get_project_totals(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the project totals.

        Returns:
            Dictionary of project totals
        """
        return self.project_totals

    def add_extra_bounties(self, extra_bounties: List[Dict[str, Any]]) -> None:
        """
        Add manually specified bounties from extra_bounties.json.

        Args:
            extra_bounties: List of bounty objects with all required fields
        """
        for bounty in extra_bounties:
            # Add the bounty to the bounty data
            self.bounty_data.append(bounty)

            # Update project totals
            owner = bounty["owner"]
            if owner not in self.project_totals:
                self.project_totals[owner] = {"count": 0, "value": 0.0}

            self.project_totals[owner]["count"] += 1

            # Calculate ERG value for totals
            amount = bounty.get("amount", "Not specified")
            currency = bounty.get("currency", "Not specified")
            erg_value = self.currency_client.calculate_erg_value(amount, currency)
            self.project_totals[owner]["value"] += erg_value

    def get_total_stats(self) -> Tuple[int, float]:
        """
        Get overall total statistics.

        Returns:
            Tuple of (total_bounties, total_value)
        """
        total_bounties = sum(project["count"] for project in self.project_totals.values())
        total_value = sum(project["value"] for project in self.project_totals.values())
        return total_bounties, total_value
