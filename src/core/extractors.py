#!/usr/bin/env python3
"""
Bounty Information Extractors Module

This module contains functions for extracting and parsing bounty information from
GitHub issues, including:
- Detecting bounty labels
- Extracting bounty amounts and currencies from issue labels
- Extracting bounty amounts and currencies from issue titles and descriptions

It provides a consistent interface for identifying and normalizing bounty data
across different formats and sources.
"""

import re
import logging
from typing import List, Dict, Tuple, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)

# Define currency normalization mappings
CURRENCY_MAPPINGS = {
    '$': 'SigUSD',
    '€': 'EUR',
    '£': 'GBP',
    'dollars': 'SigUSD',
    'usd': 'SigUSD',
    'erg': 'ERG',
    'ergos': 'ERG',
    'sigusd': 'SigUSD',
    'rsn': 'RSN',
    'bene': 'BENE',
    'gort': 'GORT',
}

# Define unit normalization mappings
UNIT_MAPPINGS = {
    'gram': 'g',
    'g': 'g',
    'oz': 'oz',
    'ounce': 'oz',
}


def is_bounty_issue(title: str, labels: List[Dict[str, Any]]) -> bool:
    """
    Determine if an issue is a bounty based on title and labels.

    Args:
        title: Issue title
        labels: List of label objects from GitHub API

    Returns:
        True if the issue appears to be a bounty
    """
    # Check if the title contains "bounty" or "b-" prefix
    if "bounty" in title.lower() or title.lower().startswith("b-"):
        return True

    # Check if any label contains 'bounty' or 'b-'
    if has_bounty_label(labels):
        return True

    return False


def has_bounty_label(labels: List[Dict[str, Any]]) -> bool:
    """
    Check if any label contains 'bounty' or 'b-'.

    Args:
        labels: List of label objects from GitHub API

    Returns:
        True if any label contains 'bounty' or 'b-'
    """
    return any("bounty" in label['name'].lower() or "b-" in label['name'].lower() for label in labels)


def extract_from_labels(labels: List[Dict[str, Any]]) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract bounty amount and currency from issue labels.

    Args:
        labels: List of label objects from GitHub API

    Returns:
        Tuple of (amount, currency) or (None, None) if not found

    Examples:
        - "bounty-100erg" -> ("100", "ERG")
        - "b-50sigusd" -> ("50", "SigUSD")
        - "bounty-2g gold" -> ("2", "g GOLD")
    """
    # Define regex patterns for different bounty formats
    label_patterns = [
        # Cryptocurrency patterns
        r'bounty\s*-?\s*(\d+(?:\.\d+)?)\s*(sigusd|rsn|bene|erg|gort)',
        r'b-(\d+(?:\.\d+)?)\s*(sigusd|rsn|bene|erg|gort)',
        r'(\d+(?:\.\d+)?)\s*(sigusd|rsn|bene|erg|gort)\s*bounty',
        # Precious metals patterns
        r'bounty\s*-?\s*(\d+(?:\.\d+)?)\s*(gram|g|oz|ounce)s?\s+(?:of\s+)?(gold|silver|platinum)',
        r'(\d+(?:\.\d+)?)\s*(gram|g|oz|ounce)s?\s+(?:of\s+)?(gold|silver|platinum)\s*bounty'
    ]

    for label in labels:
        label_name = label['name'].lower()
        logger.debug(f"Checking label: {label_name}")

        for pattern in label_patterns:
            match = re.search(pattern, label_name, re.IGNORECASE)
            if match:
                if len(match.groups()) == 3 and match.group(3) in ['gold', 'silver', 'platinum']:
                    # Handle precious metals format
                    amount = match.group(1)
                    unit = UNIT_MAPPINGS.get(match.group(2).lower(), match.group(2).lower())
                    metal = match.group(3).upper()

                    logger.info(f"Found bounty in label: {amount} {unit} {metal}")
                    return amount, f"{unit} {metal}"
                else:
                    # Handle cryptocurrency format
                    amount = match.group(1)
                    currency = match.group(2).upper()
                    currency = CURRENCY_MAPPINGS.get(currency.lower(), currency)

                    logger.info(f"Found bounty in label: {amount} {currency}")
                    return amount, currency

    logger.debug("No bounty found in labels")
    return None, None


def extract_from_text(title: str, body: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract bounty amount and currency from issue title and body.

    Args:
        title: Issue title
        body: Issue body text

    Returns:
        Tuple of (amount, currency) or (None, None) if not found

    Examples:
        - "Bounty: $100" -> ("100", "SigUSD")
        - "50 ERG bounty" -> ("50", "ERG")
        - "Bounty: 2g of GOLD" -> ("2", "g GOLD")
    """
    # Define regex patterns for different bounty formats in text
    patterns = [
        r'bounty:?\s*[\$€£]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(sigusd|gort|rsn|bene|erg|usd|ergos?|dollars?|€|£|\$)?',
        r'[\$€£]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:sigusd|gort|rsn|bene|erg|usd|ergos?|bounty)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(sigusd|gort|rsn|bene|erg|usd|ergos?)\s*bounty',
        r'bounty:?\s*(\d+(?:\.\d+)?)\s*(gram|g|oz|ounce)s?\s+(?:of\s+)?(gold|silver|platinum)',
        r'(\d+(?:\.\d+)?)\s*(gram|g|oz|ounce)s?\s+(?:of\s+)?(gold|silver|platinum)\s*bounty',
        r'bounty\s+(?:of|is|:)?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(sigusd|gort|rsn|bene|erg|usd|ergos?|dollars?|€|£|\$)?'
    ]

    # Combine title and body for searching
    text = f"{title} {body}".lower() if body else title.lower()
    logger.debug(f"Searching for bounty in text (length: {len(text)})")

    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) == 3 and match.group(3) in ['gold', 'silver', 'platinum']:
                # Handle precious metals format
                amount = match.group(1).replace(',', '')
                unit = UNIT_MAPPINGS.get(match.group(2).lower(), match.group(2).lower())
                metal = match.group(3).upper()

                logger.info(f"Found bounty in text: {amount} {unit} {metal}")
                return amount, f"{unit} {metal}"
            else:
                # Handle cryptocurrency/fiat format
                amount = match.group(1).replace(',', '')
                currency = match.group(2) if len(match.groups()) > 1 and match.group(2) else 'USD'

                # Normalize currency names
                currency = CURRENCY_MAPPINGS.get(currency.lower(), currency.upper())

                logger.info(f"Found bounty in text: {amount} {currency}")
                return amount, currency

    logger.debug("No bounty found in text")
    return None, None


def extract_bounty_info(
    issue: Dict[str, Any],
    fallback_level: str = "Not specified"
) -> Tuple[str, str]:
    """
    Extract bounty information from a GitHub issue.

    Args:
        issue: GitHub issue object
        fallback_level: Level to use if no bounty information is found

    Returns:
        Tuple of (amount, currency) with normalized values
    """
    # First try to extract from labels
    amount, currency = extract_from_labels(issue.get('labels', []))

    # If not found in labels, try title and body
    if not amount or not currency:
        amount, currency = extract_from_text(
            issue.get('title', ''),
            issue.get('body', '')
        )

    # If still not found, use fallback
    if not amount or not currency:
        return fallback_level, fallback_level

    return amount, currency
