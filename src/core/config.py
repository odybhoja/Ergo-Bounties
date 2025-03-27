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
            
        # Try .env file in src directory
        env_file = Path(os.path.join('src', '.env'))
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
        constants_path = Path('src/config/constants.json')
        try:
            with open(constants_path, 'r', encoding='utf-8') as f:
                constants = json.load(f)
                logger.info(f"Loaded constants from {constants_path}")
                return constants
        except Exception as e:
            logger.warning(f"Error loading constants from {constants_path}: {e}")
            return {}

    def _load_json_config(self, filename: str, data_key: str = "items") -> List[Any]:
        """
        Helper to load JSON configuration files with fallback path logic.

        Args:
            filename: The name of the JSON file (e.g., 'tracked_repos.json').
            data_key: Optional key to extract data from if the JSON is structured (not used here, but good practice).

        Returns:
            Loaded data as a list, or an empty list on error.
        """
        primary_path = Path('src/config') / filename
        fallback_path = self.bounties_dir / filename # Assumes self.bounties_dir is 'data'

        config_path = primary_path if primary_path.exists() else fallback_path

        if not config_path.exists():
             logger.error(f"Configuration file not found at {primary_path} or {fallback_path}")
             return []

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # If data is expected under a specific key (like {"items": [...]}), extract it.
                # For current files, the root is the list.
                # data = data.get(data_key, []) if isinstance(data, dict) else data

                if not isinstance(data, list):
                     logger.error(f"Expected a list in {config_path}, but got {type(data)}")
                     return []

                logger.info(f"Loaded {len(data)} items from {config_path}")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {config_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading {config_path}: {e}")
            return []

    def load_tracked_repos(self) -> List[Dict[str, str]]:
        """
        Load tracked repositories from configuration file.
        
        Returns:
            List of repository objects with 'owner' and 'repo' keys
        """
        return self._load_json_config('tracked_repos.json')

    def load_tracked_orgs(self) -> List[Dict[str, str]]:
        """
        Load tracked organizations from configuration file.
        
        Returns:
            List of organization objects with 'org' key
        """
        return self._load_json_config('tracked_orgs.json')

    def load_extra_bounties(self) -> List[Dict[str, Any]]:
        """
        Load manually added bounties from extra_bounties.json file.
        
        Returns:
            List of bounty objects with all required fields, including updated timestamps.
        """
        extra_bounties = self._load_json_config('extra_bounties.json')

        # Update timestamp for each bounty to ensure it's current
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for bounty in extra_bounties:
            if 'timestamp' not in bounty or not bounty['timestamp']:
                bounty['timestamp'] = timestamp

        return extra_bounties

    # Removed get_currency_file_name (moved to utils.common)
    # Removed get_currency_display_name (moved to utils.common)

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
