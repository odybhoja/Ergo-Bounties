#!/usr/bin/env python3
"""
Common Utilities Module

This module provides utility functions used throughout the application:
- Directory operations (creating directories)
- Date and time formatting
- String formatting and conversion
- URL generation

These utility functions are designed to be reusable components that help with
common tasks across the application.
"""

import os
import json
import logging
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Union, Optional, List

# Configure logging
logger = logging.getLogger(__name__)

def ensure_directory(directory: Union[str, Path]) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to create
    """
    try:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        raise

def create_claim_url(
    owner: str, 
    repo_name: str, 
    issue_number: int, 
    title: str, 
    url: str, 
    currency: str, 
    amount: str, 
    creator: str
) -> str:
    """
    Create a URL for claiming a bounty through a GitHub PR.
    
    Args:
        owner: Repository owner
        repo_name: Repository name
        issue_number: Issue number
        title: Issue title
        url: Issue URL
        currency: Bounty currency
        amount: Bounty amount
        creator: Issue creator
        
    Returns:
        URL that opens a GitHub PR with pre-filled template
    """
    logger.debug(f"Creating claim URL for {owner}/{repo_name}#{issue_number}")
    
    # Create JSON template using json.dumps to properly escape special characters
    template_data = {
        "contributor": "YOUR_GITHUB_USERNAME",
        "wallet_address": "YOUR_WALLET_ADDRESS",
        "contact_method": "YOUR_CONTACT_INFO",
        "work_link": "",
        "work_title": title,
        "bounty_id": f"{owner}/{repo_name}#{issue_number}",
        "original_issue_link": url,
        "payment_currency": currency,
        "bounty_value": 0 if amount in ["Not specified", "Ongoing"] else float(amount) if amount.replace('.', '', 1).isdigit() else 0,
        "status": "in-progress",
        "submission_date": "",
        "expected_completion": "YYYY-MM-DD",
        "description": "I am working on this bounty",
        "review_notes": "",
        "payment_tx_id": "",
        "payment_date": ""
    }
    
    # Convert to JSON and URL encode
    json_content = json.dumps(template_data, indent=2)
    encoded_json = urllib.parse.quote(json_content)
    
    # Create the claim URL
    claim_url = (
        f"https://github.com/ErgoDevs/Ergo-Bounties/new/main"
        f"?filename=submissions/{owner.lower()}-{repo_name.lower()}-{issue_number}.json"
        f"&value={encoded_json}"
        f"&message=Claim%20Bounty%20{owner}/{repo_name}%23{issue_number}"
        f"&description=I%20want%20to%20claim%20this%20bounty%20posted%20by%20{creator}.%0A%0ABounty:%20{urllib.parse.quote(title)}"
    )
    
    return claim_url

def get_current_timestamp() -> str:
    """
    Get current timestamp in a formatted string.
    
    Returns:
        Formatted timestamp (YYYY-MM-DD HH:MM:SS)
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_navigation_badges(
    total_bounties: int, 
    languages_count: int, 
    currencies_count: int, 
    orgs_count: int, 
    conversion_rates_count: int, 
    relative_path: str = ""
) -> str:
    """
    Format navigation badges for markdown files.
    
    Args:
        total_bounties: Total number of bounties
        languages_count: Number of languages
        currencies_count: Number of currencies
        orgs_count: Number of organizations
        conversion_rates_count: Number of conversion rates
        relative_path: Relative path for links (e.g., "../" for subdirectories)
        
    Returns:
        Formatted navigation badges as markdown
    """
    badges = []
    badges.append(f"[![All Bounties](https://img.shields.io/badge/All%20Bounties-{total_bounties}-blue)]({relative_path}all.md)")
    badges.append(f"[![By Language](https://img.shields.io/badge/By%20Language-{languages_count}-green)]({relative_path}by_language/)")
    badges.append(f"[![By Currency](https://img.shields.io/badge/By%20Currency-{currencies_count}-yellow)]({relative_path}by_currency/)")
    badges.append(f"[![By Organization](https://img.shields.io/badge/By%20Organization-{orgs_count}-orange)]({relative_path}by_org/)")
    
    if conversion_rates_count > 0:
        badges.append(f"[![Currency Prices](https://img.shields.io/badge/Currency%20Prices-{conversion_rates_count}-purple)]({relative_path}currency_prices.md)")
    
    return " ".join(badges)

def add_footer_buttons(relative_path: str = "") -> str:
    """
    Add standard footer buttons to markdown files.
    
    Args:
        relative_path: Relative path for links (e.g., "../" for subdirectories)
        
    Returns:
        HTML code for footer buttons
    """
    return f"""

---

<div align="center">
  <p>
    <a href="{relative_path}../docs/donate.md"><img src="https://img.shields.io/badge/❤️%20Donate-F44336" alt="Donate"></a>
    <a href="{relative_path}../docs/bounty-submission-guide.md#reserving-a-bounty"><img src="https://img.shields.io/badge/🔒%20Claim-4CAF50" alt="Claim a Bounty"></a>
  </p>
</div>
"""

def format_currency_filename(currency: str) -> str:
    """
    Format a currency name for use in filenames.
    
    Args:
        currency: Currency name or code
        
    Returns:
        Filename-friendly version of the currency name
    """
    if currency == "Not specified":
        return "not_specified"
    elif currency == "g GOLD":
        return "gold"
    else:
        return currency.lower()

def format_currency_link(currency: str, directory: str = "by_currency") -> str:
    """
    Format a currency name as a link to its dedicated page.
    
    Args:
        currency: Currency name or code
        directory: Directory containing currency files
        
    Returns:
        Markdown link to the currency page
    """
    filename = format_currency_filename(currency)
    return f"[{currency}]({directory}/{filename}.md)"

def format_organization_link(org: str, directory: str = "by_org") -> str:
    """
    Format an organization name as a link to its dedicated page.
    
    Args:
        org: Organization name
        directory: Directory containing organization files
        
    Returns:
        Markdown link to the organization page
    """
    return f"[{org}]({directory}/{org.lower()}.md)"

def format_language_link(language: str, directory: str = "by_language") -> str:
    """
    Format a language name as a link to its dedicated page.
    
    Args:
        language: Programming language name
        directory: Directory containing language files
        
    Returns:
        Markdown link to the language page
    """
    return f"[{language}]({directory}/{language.lower()}.md)"

def wrap_with_guardrails(content: str, header: str = "") -> str:
    """
    Wrap content with guardrails for protection against automatic updates.
    
    Args:
        content: Markdown content
        header: Optional header to include before the content
        
    Returns:
        Content wrapped with guardrails
    """
    timestamp = get_current_timestamp()
    
    guardrails = f"""<!-- GENERATED FILE - DO NOT EDIT DIRECTLY -->
<!-- Generated on: {timestamp} -->

{header}

{content}

<!-- END OF GENERATED CONTENT -->
"""
    return guardrails
