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

import requests
import logging
import time
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)

class GitHubClient:
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
        self.token = token
        self.headers = {"Authorization": f"token {token}"}
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    def _make_request(self, url: str, method: str = "GET") -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Dict[str, str]]]]:
        """
        Make a request to the GitHub API with retry logic and rate limit handling.
        
        Args:
            url: API endpoint URL
            method: HTTP method (default: GET)
            
        Returns:
            Tuple of (response JSON data, pagination links)
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method, 
                    url=url, 
                    headers=self.headers, 
                    timeout=30
                )
                
                # Check for rate limiting
                if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
                    remaining = int(response.headers['X-RateLimit-Remaining'])
                    if remaining == 0:
                        reset_time = int(response.headers['X-RateLimit-Reset'])
                        sleep_time = max(1, reset_time - time.time())
                        logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds")
                        time.sleep(sleep_time)
                        continue
                
                response.raise_for_status()
                return response.json(), response.links
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt+1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Max retries exceeded for URL: {url}")
                    return None, None
        
        return None, None
    
    def get_organization_repos(self, org: str) -> List[Dict[str, Any]]:
        """
        Get all repositories for an organization.
        
        Args:
            org: Organization name
            
        Returns:
            List of repository objects
        """
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100"
        all_repos = []
        
        logger.info(f"Fetching repositories for organization: {org}")
        
        while url:
            data, links = self._make_request(url)
            if not data:
                break
                
            all_repos.extend(data)
            url = links.get('next', {}).get('url') if links else None
            
            logger.debug(f"Fetched {len(data)} repositories from {org}, total: {len(all_repos)}")
        
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
        url = f"https://api.github.com/repos/{owner}/{repo}/languages"
        
        logger.debug(f"Fetching languages for repository: {owner}/{repo}")
        
        data, _ = self._make_request(url)
        if not data:
            return []
            
        # Sort languages by bytes of code and get top 2
        sorted_languages = sorted(data.items(), key=lambda x: x[1], reverse=True)[:2]
        result = [lang[0] for lang in sorted_languages]
        
        logger.debug(f"Languages for {owner}/{repo}: {result}")
        return result
    
    def get_repository_issues(self, owner: str, repo: str, state: str = 'open') -> List[Dict[str, Any]]:
        """
        Get issues from a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            
        Returns:
            List of issue objects
        """
        url = f'https://api.github.com/repos/{owner}/{repo}/issues?state={state}&per_page=100'
        all_issues = []
        
        logger.info(f"Fetching {state} issues from repository: {owner}/{repo}")
        
        while url:
            data, links = self._make_request(url)
            if not data:
                break
                
            all_issues.extend(data)
            url = links.get('next', {}).get('url') if links else None
            
            logger.debug(f"Fetched {len(data)} issues from {owner}/{repo}, total: {len(all_issues)}")
        
        logger.info(f"Successfully fetched {len(all_issues)} issues from {owner}/{repo}")
        return all_issues
