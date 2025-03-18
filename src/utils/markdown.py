#!/usr/bin/env python3
"""
Markdown Templates and Utilities Module

This module provides templates and utility functions for generating markdown content:
- Table generators for different bounty views
- Navigation and filter section generators
- Header and footer templates
- Guardrail wrappers for protecting generated content

These utilities ensure consistent formatting across all generated markdown files.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .common import (
    format_navigation_badges, 
    add_footer_buttons,
    format_currency_filename, 
    format_currency_link,
    format_organization_link,
    format_language_link,
    get_current_timestamp,
    wrap_with_guardrails,
    create_claim_url
)

# Configure logging
logger = logging.getLogger(__name__)

def generate_navigation_section(
    total_bounties: int, 
    languages_count: int, 
    currencies_count: int, 
    orgs_count: int, 
    conversion_rates_count: int, 
    relative_path: str = ""
) -> str:
    """
    Generate a navigation section with badges for markdown files.
    
    Args:
        total_bounties: Total number of bounties
        languages_count: Number of languages
        currencies_count: Number of currencies
        orgs_count: Number of organizations
        conversion_rates_count: Number of conversion rates
        relative_path: Relative path for links
        
    Returns:
        Formatted navigation section as markdown
    """
    content = "## Navigation\n\n"
    content += format_navigation_badges(
        total_bounties, 
        languages_count, 
        currencies_count, 
        orgs_count, 
        conversion_rates_count, 
        relative_path
    )
    content += "\n\n"
    return content

def generate_filter_section(
    languages: Dict[str, List[Dict[str, Any]]], 
    currencies_dict: Dict[str, List[Dict[str, Any]]], 
    orgs: Dict[str, List[Dict[str, Any]]],
    path_prefix: str = ""
) -> str:
    """
    Generate a filter section for markdown files.
    
    Args:
        languages: Dictionary of languages and their bounties
        currencies_dict: Dictionary of currencies and their bounties
        orgs: Dictionary of organizations and their bounties
        path_prefix: Prefix for paths in links
        
    Returns:
        Formatted filter section as markdown
    """
    content = "## Filter Bounties\n\n"
    
    # Programming Languages
    content += "**By Programming Language:** "
    lang_links = []
    for lang_name, lang_bounties_list in languages.items():
        lang_links.append(f"[{lang_name} ({len(lang_bounties_list)})]({path_prefix}by_language/{lang_name.lower()}.md)")
    content += " • ".join(lang_links)
    content += "\n\n"
    
    # Currencies
    content += "**By Currency:** "
    currency_links = []
    for currency_name, currency_bounties_list in currencies_dict.items():
        currency_file_name = format_currency_filename(currency_name)
        currency_links.append(f"[{currency_name} ({len(currency_bounties_list)})]({path_prefix}by_currency/{currency_file_name}.md)")
    content += " • ".join(currency_links)
    content += "\n\n"
    
    # Organizations
    content += "**By Organization:** "
    org_links = []
    for org_name, org_bounties_list in orgs.items():
        org_links.append(f"[{org_name} ({len(org_bounties_list)})]({path_prefix}by_org/{org_name.lower()}.md)")
    content += " • ".join(org_links)
    content += "\n\n"
    
    return content

def generate_standard_bounty_table(
    bounties: List[Dict[str, Any]], 
    conversion_rates: Dict[str, float]
) -> str:
    """
    Generate a standard bounty table for markdown files.
    
    Args:
        bounties: List of bounty data
        conversion_rates: Dictionary of conversion rates
        
    Returns:
        Formatted bounty table as markdown
    """
    from ..api.currency_client import CurrencyClient
    
    content = "|Organisation|Repository|Title & Link|Bounty Amount|Paid in|Primary Language|Reserve|\n"
    content += "|---|---|---|---|---|---|---|\n"
    
    # Set up currency client for conversions
    currency_client = CurrencyClient()
    currency_client.rates = conversion_rates
    
    # Sort bounties by ERG value (highest first)
    sorted_bounties = sorted(
        bounties,
        key=lambda b: currency_client.calculate_erg_value(b["amount"], b["currency"]),
        reverse=True
    )
    
    # Add rows for each bounty
    for bounty in sorted_bounties:
        owner = bounty["owner"]
        repo_name = bounty["repo"]
        title = bounty["title"]
        url = bounty["url"]
        amount = bounty["amount"]
        currency = bounty["currency"]
        primary_lang = bounty["primary_lang"]
        issue_number = bounty["issue_number"]
        creator = bounty["creator"]
        
        # Calculate ERG equivalent for display
        erg_equiv = currency_client.convert_to_erg(amount, currency)
        erg_display = f"({erg_equiv} ERG)" if erg_equiv != amount and amount != "Not specified" and amount != "Ongoing" else ""
        
        # Create a claim link that opens a PR template
        claim_url = create_claim_url(owner, repo_name, issue_number, title, url, currency, amount, creator)
        
        # Add organization, language and currency links
        org_link = format_organization_link(owner)
        primary_lang_link = format_language_link(primary_lang)
        currency_link = format_currency_link(currency)
        
        # Create a reserve button or status label based on bounty status
        if "status" in bounty and bounty["status"] == "In Progress":
            reserve_button = "<kbd>In Progress</kbd>"
        else:
            reserve_button = f"[<kbd>Reserve</kbd>]({claim_url})"
        
        # Format the amount display based on special cases
        if amount == "Not specified":
            amount_display = "Not specified"
        elif amount == "Ongoing":
            amount_display = "Ongoing program"
        else:
            amount_display = f"{amount} {erg_display}"
        
        content += f"| {org_link} | [{repo_name}](https://github.com/{owner}/{repo_name}) | [{title}]({url}) | {amount_display} | {currency_link} | {primary_lang_link} | {reserve_button} |\n"
    
    return content

def generate_ongoing_programs_table(ongoing_programs: List[Dict[str, Any]]) -> str:
    """
    Generate a table for ongoing programs.
    
    Args:
        ongoing_programs: List of ongoing program bounty data
        
    Returns:
        Formatted ongoing programs table as markdown
    """
    content = "| Organization | Program | Details | Primary Language |\n"
    content += "|-------------|---------|---------|------------------|\n"
    
    # Sort by organization
    ongoing_programs = sorted(ongoing_programs, key=lambda b: b["owner"])
    
    # Add rows for each program
    for program in ongoing_programs:
        owner = program["owner"]
        title = program["title"]
        url = program["url"]
        primary_lang = program["primary_lang"]
        
        # Add organization and language links
        org_link = format_organization_link(owner)
        primary_lang_link = format_language_link(primary_lang)
        
        content += f"| {org_link} | [{title}]({url}) | [Details]({url}) | {primary_lang_link} |\n"
    
    return content

def update_readme_badges(
    total_bounties: int,
    total_value: float, 
    high_value_count: int
) -> bool:
    """
    Update the badges in the README.md file.
    
    Args:
        total_bounties: Total number of bounties
        total_value: Total ERG value of all bounties
        high_value_count: Number of high-value bounties
        
    Returns:
        True if successful, False otherwise
    """
    try:
        readme_path = "README.md"
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Directly write a new README with the updated content
        with open(readme_path, 'w', encoding='utf-8') as f:
            # Replace line by line, making sure to retain all content
            lines = content.split('\n')
            for line in lines:
                # Open Bounties badge line
                if "Open%20Bounties" in line and "img.shields.io" in line:
                    # Replace the line with the updated badge
                    line = re.sub(
                        r'Open%20Bounties-\d+\+?-4CAF50', 
                        f'Open%20Bounties-{total_bounties}%2B-4CAF50', 
                        line
                    )
                    # Also update the path from /bounties/ to /data/
                    line = line.replace("/bounties/", "/data/")
                    print(f"DEBUG: Updated bounties badge line: {line}")
                
                # Total Value badge line
                elif "Total%20Value" in line and "img.shields.io" in line:
                    # Replace the line with the updated badge
                    line = re.sub(
                        r'Total%20Value-[\d,\.]+%20ERG-2196F3', 
                        f'Total%20Value-{total_value:,.2f}%20ERG-2196F3', 
                        line
                    )
                    # Also update the path from /bounties/ to /data/
                    line = line.replace("/bounties/", "/data/")
                    print(f"DEBUG: Updated total value badge line: {line}")
                
                # High Value badge line
                elif "High%20Value" in line and "img.shields.io" in line:
                    # Replace the line with the updated badge
                    line = re.sub(
                        r'High%20Value-\d+\+?%20Over%201000%20ERG-FFC107', 
                        f'High%20Value-{high_value_count}%2B%20Over%201000%20ERG-FFC107', 
                        line
                    )
                    # Also update the path from /bounties/ to /data/
                    line = line.replace("/bounties/", "/data/")
                    print(f"DEBUG: Updated high value badge line: {line}")
                
                # Featured Bounties badge line
                elif "Featured%20Bounties" in line and "img.shields.io" in line:
                    # Update the path from /bounties/ to /data/
                    line = line.replace("/bounties/", "/data/")
                    print(f"DEBUG: Updated featured bounties badge line: {line}")
                
                # Browse Bounties badge line
                elif "Browse%20Bounties" in line and "img.shields.io" in line:
                    # Update the path from /bounties/ to /data/
                    line = line.replace("/bounties/", "/data/")
                    print(f"DEBUG: Updated browse bounties badge line: {line}")
                
                # Currency Rates badge line
                elif "Current%20Rates" in line and "img.shields.io" in line:
                    # Update the path from /bounties/ to /data/
                    line = line.replace("/bounties/", "/data/")
                    print(f"DEBUG: Updated currency rates badge line: {line}")
                
                # By language badges
                elif "/bounties/by_language/" in line:
                    # Update all language badge paths
                    line = line.replace("/bounties/by_language/", "/data/by_language/")
                    print(f"DEBUG: Updated language badge line: {line}")
                
                # By currency badges
                elif "/bounties/by_currency/" in line:
                    # Update all currency badge paths
                    line = line.replace("/bounties/by_currency/", "/data/by_currency/")
                    print(f"DEBUG: Updated currency badge line: {line}")
                
                # By org badges
                elif "/bounties/by_org/" in line:
                    # Update all org badge paths
                    line = line.replace("/bounties/by_org/", "/data/by_org/")
                    print(f"DEBUG: Updated org badge line: {line}")
                
                # Latest Update line (at the end of the file)
                elif "Latest Update:" in line:
                    # Replace the timestamp
                    today = datetime.now().strftime("%Y-%m-%d")
                    line = f"<!-- Latest Update: {today} -->"
                    print(f"DEBUG: Updated timestamp: {line}")
                
                # Don't add newlines after the final line with content
                if line.strip() or line.startswith("<!-- Latest Update:"):
                    f.write(line + '\n')
                else:
                    # Only preserve exactly one blank line at the end
                    if not f.tell() or f.tell() and f.tell() and content.split('\n')[-1].strip():
                        f.write('\n')
            
        logger.info("Updated README.md badges successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error updating README.md badges: {e}")
        return False

def update_partially_generated_file(
    file_path: str,
    start_marker: str,
    end_marker: str,
    new_content: str
) -> bool:
    """
    Update a section of a file between two markers.
    
    Args:
        file_path: Path to the file to update
        start_marker: Start marker text
        end_marker: End marker text
        new_content: New content to insert between markers
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find the content between the markers
        pattern = f"({re.escape(start_marker)})(.*?)({re.escape(end_marker)})"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Replace the content between the markers
            updated_content = content.replace(
                match.group(0),
                f"{start_marker}\n\n{new_content}\n\n{end_marker}"
            )
            
            # Write the updated content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            logger.info(f"Updated section in {file_path} successfully")
            return True
        else:
            logger.error(f"Could not find markers in {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating {file_path}: {e}")
        return False

def wrap_with_full_guardrails(content: str, title: str = "") -> str:
    """
    Wrap content with full guardrails, including header and timestamp.
    
    Args:
        content: Content to wrap
        title: Optional title to use as H1 heading
        
    Returns:
        Content wrapped with full guardrails
    """
    return wrap_with_guardrails(content, title)
