#!/usr/bin/env python3
"""
Configuration Module

This module handles configuration loading and management for the bounty finder application.
It provides access to:
- GitHub API tokens
- Tracked repositories and organizations
- Extra manually-added bounties
- Constants and settings

The configuration is loaded from files in the bounties directory and environment variables.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

class BountyConfig:
    """
    Configuration handler for the bounty finder application.
    Manages loading configuration from files and environment variables.
    """
    
    def __init__(self, bounties_dir: Union[str, Path] = 'bounties'):
        """
        Initialize the configuration handler.
        
        Args:
            bounties_dir: Directory where bounty files are stored
        """
        self.bounties_dir = Path(bounties_dir)
        self.github_token = self._get_github_token()
        self.constants = self._load_constants()
        
    def _get_github_token(self) -> Optional[str]:
        """
        Get GitHub token from environment variable or .env file.
        
        Returns:
            GitHub token or None if not found
        """
        # First try environment variable
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            logger.info("GitHub token found in environment variables")
            return token
            
        # Then try .env file in the scripts directory
        env_file = Path(os.path.join('scripts', '.env'))
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if line.startswith('github_token='):
                                token = line.split('=', 1)[1].strip('"\'')
                                logger.info("GitHub token loaded from .env file")
                                return token
                            elif line.startswith('GITHUB_TOKEN='):
                                token = line.split('=', 1)[1].strip('"\'')
                                logger.info("GitHub token loaded from .env file")
                                return token
            except Exception as e:
                logger.error(f"Error reading .env file: {e}")
        
        # Also try .env in the root directory
        env_file = Path('.env')
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if line.startswith('github_token='):
                                token = line.split('=', 1)[1].strip('"\'')
                                logger.info("GitHub token loaded from .env file")
                                return token
                            elif line.startswith('GITHUB_TOKEN='):
                                token = line.split('=', 1)[1].strip('"\'')
                                logger.info("GitHub token loaded from .env file")
                                return token
            except Exception as e:
                logger.error(f"Error reading .env file: {e}")
        
        logger.error("GITHUB_TOKEN environment variable or .env file with 'github_token=' is required")
        return None
    
    def _load_constants(self) -> Dict[str, Any]:
        """
        Load constants from the JSON configuration file.
        
        Returns:
            Dictionary of constants
        """
        constants_path = Path('scripts/constants.json')
        try:
            with open(constants_path, 'r', encoding='utf-8') as f:
                constants = json.load(f)
                logger.info(f"Loaded constants from {constants_path}")
                return constants
        except Exception as e:
            logger.warning(f"Error loading constants from {constants_path}: {e}")
            return {}
    
    def load_tracked_repos(self) -> List[Dict[str, str]]:
        """
        Load tracked repositories from configuration file.
        
        Returns:
            List of repository objects with 'owner' and 'repo' keys
        """
        repos_path = self.bounties_dir / 'tracked_repos.json'
        try:
            with open(repos_path, 'r', encoding='utf-8') as f:
                repos = json.load(f)
                logger.info(f"Loaded {len(repos)} tracked repositories")
                return repos
        except Exception as e:
            logger.error(f"Error reading {repos_path}: {e}")
            return []
    
    def load_tracked_orgs(self) -> List[Dict[str, str]]:
        """
        Load tracked organizations from configuration file.
        
        Returns:
            List of organization objects with 'org' key
        """
        orgs_path = self.bounties_dir / 'tracked_orgs.json'
        try:
            with open(orgs_path, 'r', encoding='utf-8') as f:
                orgs = json.load(f)
                logger.info(f"Loaded {len(orgs)} tracked organizations")
                return orgs
        except Exception as e:
            logger.warning(f"Error reading {orgs_path}: {e}")
            return []
    
    def load_extra_bounties(self) -> List[Dict[str, Any]]:
        """
        Load manually added bounties from extra_bounties.json file.
        
        Returns:
            List of bounty objects with all required fields
        """
        extra_bounties_path = self.bounties_dir / 'extra_bounties.json'
        try:
            with open(extra_bounties_path, 'r', encoding='utf-8') as f:
                extra_bounties = json.load(f)
                
                # Update timestamp for each bounty to ensure it's current
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for bounty in extra_bounties:
                    if 'timestamp' not in bounty or not bounty['timestamp']:
                        bounty['timestamp'] = timestamp
                        
                logger.info(f"Loaded {len(extra_bounties)} extra bounties")
                return extra_bounties
        except Exception as e:
            logger.warning(f"Error reading {extra_bounties_path}: {e}")
            return []
    
    def get_currency_file_name(self, currency: str) -> str:
        """
        Get the filename to use for a currency.
        
        Args:
            currency: Currency code
            
        Returns:
            Normalized filename for the currency
        """
        currency_file_names = self.constants.get("currency_file_names", {})
        
        if currency in currency_file_names:
            return currency_file_names[currency]
        elif currency == "Not specified":
            return "not_specified"
        elif currency == "g GOLD":
            return "gold"
        else:
            return currency.lower()
    
    def get_currency_display_name(self, currency: str) -> str:
        """
        Get the display name for a currency.
        
        Args:
            currency: Currency code
            
        Returns:
            Formatted display name for the currency
        """
        currency_display_names = self.constants.get("currency_display_names", {})
        
        if currency in currency_display_names:
            return currency_display_names[currency]
        return currency
    
    def is_valid(self) -> bool:
        """
        Check if the configuration is valid for running the application.
        
        Returns:
            True if the configuration is valid, False otherwise
        """
        if self.github_token is None:
            logger.error("Invalid configuration: Missing GitHub token")
            return False
            
        tracked_repos = self.load_tracked_repos()
        if not tracked_repos:
            logger.error("Invalid configuration: No tracked repositories found")
            return False
            
        return True
    
    def ensure_directories(self) -> None:
        """
        Ensure that all required directories exist.
        Creates them if they don't exist.
        """
        # Main bounties directory
        os.makedirs(self.bounties_dir, exist_ok=True)
        
        # Subdirectories
        subdirs = ['by_language', 'by_currency', 'by_org']
        for subdir in subdirs:
            os.makedirs(self.bounties_dir / subdir, exist_ok=True)
            
        logger.info("Ensured all required directories exist")
