"""
Module for generating high-value bounties markdown file.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any

from ..utils import ensure_directory, create_claim_url, format_navigation_badges, calculate_erg_value
from ..conversion_rates import convert_to_erg

# Configure logging
logger = logging.getLogger('high_value_generator')

def generate_high_value_bounties_file(
    bounty_data: List[Dict[str, Any]], 
    conversion_rates: Dict[str, float], 
    total_bounties: int, 
    total_value: float,
    languages: Dict[str, List[Dict[str, Any]]], 
    currencies_dict: Dict[str, List[Dict[str, Any]]], 
    orgs: Dict[str, List[Dict[str, Any]]], 
    bounties_dir: str,
    high_value_threshold: int = 1000
) -> None:
    """
    Generate a high-value bounties markdown file.
    
    Args:
        bounty_data: List of bounty data
        conversion_rates: Dictionary of conversion rates
        total_bounties: Total number of bounties
        total_value: Total value of bounties
        languages: Dictionary of languages and their bounties
        currencies_dict: Dictionary of currencies and their bounties
        orgs: Dictionary of organizations and their bounties
        bounties_dir: Bounties directory
        high_value_threshold: Threshold for high-value bounties (in ERG)
    """
    logger.info(f"Generating high-value bounties file with threshold {high_value_threshold} ERG")
    
    high_value_file = f'{bounties_dir}/high-value-bounties.md'
    with open(high_value_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("# High Value Bounties (1000+ ERG)\n\n")
        f.write(f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*\n\n")
        
        # Add navigation badges
        f.write("## Navigation\n\n")
        f.write(format_navigation_badges(
            total_bounties, 
            len(languages), 
            len(currencies_dict), 
            len(orgs), 
            len(conversion_rates)
        ))
        f.write("\n\n")
        
        # Find all high value bounties
        high_value_bounties = []
        for bounty in bounty_data:
            amount = bounty["amount"]
            currency = bounty["currency"]
            
            if amount != "Not specified" and amount != "Ongoing":
                try:
                    # Convert to ERG equivalent
                    value = calculate_erg_value(amount, currency, conversion_rates)
                    
                    if value >= high_value_threshold:
                        bounty_with_value = bounty.copy()
                        bounty_with_value["erg_value"] = value
                        high_value_bounties.append(bounty_with_value)
                except (ValueError, TypeError):
                    pass
        
        # Sort by ERG value (highest first)
        high_value_bounties.sort(key=lambda x: x.get("erg_value", 0), reverse=True)
        
        # Write intro text
        high_value_count = len(high_value_bounties)
        f.write(f"This page lists all bounties with an ERG value of {high_value_threshold}+ ERG, sorted by value (highest first).\n\n")
        f.write(f"**Total high-value bounties: {high_value_count}**\n\n")
        
        # Write bounties table
        f.write("## Available Bounties\n\n")
        f.write("|Organisation|Repository|Title & Link|Primary Language|ERG Value|Paid In|Reserve|\n")
        f.write("|---|---|---|---|---|---|---|\n")
        
        # Add rows for each high-value bounty
        for bounty in high_value_bounties:
            owner = bounty["owner"]
            title = bounty["title"]
            url = bounty["url"]
            amount = bounty["amount"]
            currency = bounty["currency"]
            primary_lang = bounty["primary_lang"]
            issue_number = bounty["issue_number"]
            creator = bounty["creator"]
            repo_name = bounty["repo"]
            
            # Try to convert to ERG equivalent
            erg_equiv = bounty["erg_value"]
            
            # Create a claim link that opens a PR template
            claim_url = create_claim_url(owner, repo_name, issue_number, title, url, currency, amount, creator)
            
            # Format the currency name for the file link
            if currency == "Not specified":
                currency_file_name = "not_specified"
            elif currency == "g GOLD":
                currency_file_name = "gold"
            else:
                currency_file_name = currency.lower()
            
            # Add links to organization, language, and currency pages
            org_link = f"[{owner}](by_org/{owner.lower()}.md)"
            currency_link = f"[{currency}](by_currency/{currency_file_name}.md)"
            primary_lang_link = f"[{primary_lang}](by_language/{primary_lang.lower()}.md)"
            
            # Create a nicer reserve button
            reserve_button = f"[<kbd>Reserve</kbd>]({claim_url})"
            
            # Format the row with the new columns
            f.write(f"| {org_link} | [{repo_name}](https://github.com/{owner}/{repo_name}) | [{title}]({url}) | {primary_lang_link} | {erg_equiv:.2f} | {currency_link} | {reserve_button} |\n")
        
        # Add footer with action buttons
        f.write("\n\n---\n\n")
        f.write("<div align=\"center\">\n")
        f.write("  <p>\n")
        f.write("    <a href=\"/docs/donate.md\">\n")
        f.write("      <img src=\"https://img.shields.io/badge/❤️%20Donate-F44336\" alt=\"Donate\">\n")
        f.write("    </a>\n")
        f.write("    <a href=\"/docs/bounty-submission-guide.md#reserving-a-bounty\">\n")
        f.write("      <img src=\"https://img.shields.io/badge/🔒%20Claim-4CAF50\" alt=\"Claim a Bounty\">\n")
        f.write("    </a>\n")
        f.write("  </p>\n")
        f.write("</div>\n")
    
    logger.info(f"Generated high-value bounties file with {len(high_value_bounties)} bounties")
