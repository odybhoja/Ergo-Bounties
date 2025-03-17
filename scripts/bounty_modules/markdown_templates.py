"""
Module for centralized markdown template generation.
Contains templates and utility functions for generating consistent markdown files with guardrails.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger('markdown_templates')

# Templates for file headers with guardrails
FULL_FILE_HEADER = '''<!-- 
/** WARNING: AUTO-GENERATED FILE. DO NOT MODIFY DIRECTLY **/
/** Any changes made to this file will be overwritten by the automated system **/
/** Instead, update the generation scripts in .github/workflows/scripts/ **/
-->

{title}

*Report generated: {timestamp} UTC*

'''

FULL_FILE_FOOTER = '''

<!-- 
/** GENERATION END **/
/** Content above is automatically generated and will be overwritten **/
-->'''

PARTIAL_SECTION_HEADER = '''<!-- 
/** WARNING: GENERATED CONTENT BEGINS - DO NOT MODIFY SECTION DIRECTLY **/
/** Any changes made to the generated section will be overwritten **/
/** Instead, update the generation scripts in .github/workflows/scripts/ **/
-->

'''

PARTIAL_SECTION_FOOTER = '''

<!-- 
/** GENERATED CONTENT ENDS **/
/** Content between these markers is automatically generated and will be overwritten **/
-->'''

def generate_navigation_section(
    total_bounties: int, 
    languages_count: int, 
    currencies_count: int, 
    orgs_count: int, 
    conversion_rates_count: int, 
    relative_path: str = ""
) -> str:
    """
    Generate standardized navigation section with badges.
    
    Args:
        total_bounties: Total number of bounties
        languages_count: Number of languages
        currencies_count: Number of currencies
        orgs_count: Number of organizations
        conversion_rates_count: Number of conversion rates
        relative_path: Relative path for links (e.g., "../" for subdirectories)
        
    Returns:
        Markdown string with navigation badges
    """
    content = "## Navigation\n\n"
    
    badges = []
    badges.append(f"[![All Bounties](https://img.shields.io/badge/All%20Bounties-{total_bounties}-blue)]({relative_path}all.md)")
    badges.append(f"[![By Language](https://img.shields.io/badge/By%20Language-{languages_count}-green)]({relative_path}by_language/)")
    badges.append(f"[![By Currency](https://img.shields.io/badge/By%20Currency-{currencies_count}-yellow)]({relative_path}by_currency/)")
    badges.append(f"[![By Organization](https://img.shields.io/badge/By%20Organization-{orgs_count}-orange)]({relative_path}by_org/)")
    
    if conversion_rates_count > 0:
        badges.append(f"[![Currency Prices](https://img.shields.io/badge/Currency%20Prices-{conversion_rates_count}-purple)]({relative_path}currency_prices.md)")
    
    content += " ".join(badges)
    content += "\n\n"
    
    return content

def generate_filter_section(
    languages: Dict[str, List[Dict[str, Any]]], 
    currencies_dict: Dict[str, List[Dict[str, Any]]], 
    orgs: Dict[str, List[Dict[str, Any]]], 
    relative_path: str = ""
) -> str:
    """
    Generate standardized filter section with links to other pages.
    
    Args:
        languages: Dictionary of languages and their bounties
        currencies_dict: Dictionary of currencies and their bounties
        orgs: Dictionary of organizations and their bounties
        relative_path: Relative path for links (e.g., "../" for subdirectories)
        
    Returns:
        Markdown string with filter options
    """
    content = "## Filter Bounties\n\n"
    
    # Programming Languages
    content += "**By Programming Language:** "
    lang_links = []
    for lang, lang_bounties in languages.items():
        lang_links.append(f"[{lang} ({len(lang_bounties)})]({relative_path}by_language/{lang.lower()}.md)")
    content += " • ".join(lang_links)
    content += "\n\n"
    
    # Currencies
    content += "**By Currency:** "
    currency_links = []
    for currency, currency_bounties in currencies_dict.items():
        # Format the currency name for the file link
        currency_file_name = format_currency_filename(currency)
        currency_links.append(f"[{currency} ({len(currency_bounties)})]({relative_path}by_currency/{currency_file_name}.md)")
    content += " • ".join(currency_links)
    content += "\n\n"
    
    # Organizations
    content += "**By Organization:** "
    org_links = []
    for org, org_bounties in orgs.items():
        org_links.append(f"[{org} ({len(org_bounties)})]({relative_path}by_org/{org.lower()}.md)")
    content += " • ".join(org_links)
    content += "\n\n"
    
    return content

def format_currency_filename(currency: str) -> str:
    """
    Format currency name for consistent file linking.
    
    Args:
        currency: Currency name
        
    Returns:
        Formatted filename string
    """
    if currency == "Not specified":
        return "not_specified"
    elif currency == "g GOLD":
        return "gold"
    else:
        return currency.lower()

def format_currency_link(currency: str, relative_path: str = "") -> str:
    """
    Format currency name as a markdown link.
    
    Args:
        currency: Currency name
        relative_path: Relative path for links
        
    Returns:
        Markdown link to currency page
    """
    currency_file_name = format_currency_filename(currency)
    return f"[{currency}]({relative_path}by_currency/{currency_file_name}.md)"

def format_organization_link(org: str, relative_path: str = "") -> str:
    """
    Format organization name as a markdown link.
    
    Args:
        org: Organization name
        relative_path: Relative path for links
        
    Returns:
        Markdown link to organization page
    """
    return f"[{org}]({relative_path}by_org/{org.lower()}.md)"

def format_language_link(language: str, relative_path: str = "") -> str:
    """
    Format language name as a markdown link.
    
    Args:
        language: Language name
        relative_path: Relative path for links
        
    Returns:
        Markdown link to language page
    """
    return f"[{language}]({relative_path}by_language/{language.lower()}.md)"

def generate_standard_bounty_table(
    bounties: List[Dict[str, Any]], 
    conversion_rates: Dict[str, float],
    relative_path: str = "",
    show_language: bool = True
) -> str:
    """
    Generate standardized bounty table with consistent formatting.
    
    Args:
        bounties: List of bounty dictionaries
        conversion_rates: Dictionary of conversion rates
        relative_path: Relative path for links
        show_language: Whether to show language column (True) or secondary language (False)
        
    Returns:
        Markdown string with bounty table
    """
    from scripts.bounty_modules.utils import calculate_erg_value, create_claim_url, convert_to_erg
    
    content = ""
    
    # Determine table headers based on show_language parameter
    if show_language:
        content += "|Organisation|Repository|Title & Link|Primary Language|ERG Value|Paid In|Reserve|\n"
        content += "|---|---|---|---|---|---|---|\n"
    else:
        content += "|Organisation|Repository|Title & Link|ERG Value|Paid In|Secondary Language|Reserve|\n"
        content += "|---|---|---|---|---|---|---|\n"
    
    # Sort bounties by ERG value
    sorted_bounties = get_sorted_bounties_by_value(bounties, conversion_rates)
    
    # Add rows for each bounty (excluding those with "Not specified" amounts)
    has_written_row = False
    for bounty in sorted_bounties:
        owner = bounty["owner"]
        title = bounty["title"]
        url = bounty["url"]
        amount = bounty["amount"]
        currency = bounty["currency"]
        primary_lang = bounty["primary_lang"]
        secondary_lang = bounty.get("secondary_lang", "")
        
        # Skip ongoing programs for main tables
        if amount == "Ongoing":
            continue
            
        # Skip bounties with "Not specified" amounts, but keep at least one row
        if amount == "Not specified" and has_written_row:
            continue
        
        # Try to convert to ERG equivalent
        erg_equiv = convert_to_erg(amount, currency, conversion_rates)
        
        # Create a claim link that opens a PR template
        issue_number = bounty["issue_number"]
        creator = bounty["creator"]
        repo_name = bounty["repo"]
        
        claim_url = create_claim_url(owner, repo_name, issue_number, title, url, currency, amount, creator)
        
        # Create a nicer reserve button
        reserve_button = f"[<kbd>Reserve</kbd>]({claim_url})"
        
        # Format the row with the new columns
        if show_language:
            content += (f"| {format_organization_link(owner, relative_path)} | "
                      f"[{repo_name}](https://github.com/{owner}/{repo_name}) | "
                      f"[{title}]({url}) | "
                      f"{format_language_link(primary_lang, relative_path)} | "
                      f"{erg_equiv} | "
                      f"{format_currency_link(currency, relative_path)} | "
                      f"{reserve_button} |\n")
        else:
            content += (f"| {format_organization_link(owner, relative_path)} | "
                      f"[{repo_name}](https://github.com/{owner}/{repo_name}) | "
                      f"[{title}]({url}) | "
                      f"{erg_equiv} ERG | "
                      f"{format_currency_link(currency, relative_path)} | "
                      f"{secondary_lang} | "
                      f"{reserve_button} |\n")
        
        has_written_row = True
    
    return content

def generate_ongoing_programs_table(ongoing_programs: List[Dict[str, Any]]) -> str:
    """
    Generate table for ongoing programs with consistent formatting.
    
    Args:
        ongoing_programs: List of ongoing program dictionaries
        
    Returns:
        Markdown string with ongoing programs table
    """
    content = "|Organisation|Repository|Title & Link|Primary Language|Value|ERG Value|Paid In|Reserve|\n"
    content += "|---|---|---|---|---|---|---|---|\n"
    
    for program in ongoing_programs:
        owner = program["owner"]
        title = program["title"]
        url = program["url"]
        primary_lang = program["primary_lang"]
        repo = program["repo"]
        
        # Add links to organization pages
        org_link = format_organization_link(owner, "../")
        
        # Create a nicer details button
        details_button = f"[<kbd>Details</kbd>](#{title.lower().replace(' ', '-').replace('/', '').replace('[', '').replace(']', '')})"
        
        # For each program, add a row to the table
        content += f"| {org_link} | [{repo}](https://github.com/{owner}/{repo}) | [{title}]({url}) | {primary_lang} | Varies | Based on contribution | ERG | {details_button} |\n"
    
    return content

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

def wrap_with_full_guardrails(content: str, title: str) -> str:
    """
    Wrap entire content with guardrails for fully generated files.
    
    Args:
        content: Markdown content
        title: Title for the header
        
    Returns:
        Content wrapped with guardrails
    """
    header = FULL_FILE_HEADER.format(
        title=title,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    return header + content + FULL_FILE_FOOTER

def wrap_section_with_guardrails(content: str) -> str:
    """
    Wrap section with guardrails for partially generated files.
    
    Args:
        content: Markdown content
        
    Returns:
        Content wrapped with section guardrails
    """
    return PARTIAL_SECTION_HEADER + content + PARTIAL_SECTION_FOOTER

def get_sorted_bounties_by_value(bounties: List[Dict[str, Any]], conversion_rates: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Sort bounties by ERG value and return sorted list.
    
    Args:
        bounties: List of bounty dictionaries
        conversion_rates: Dictionary of conversion rates
        
    Returns:
        Sorted list of bounties
    """
    from .utils import calculate_erg_value
    
    # Calculate ERG equivalent for each bounty for sorting
    for bounty in bounties:
        amount = bounty["amount"]
        currency = bounty["currency"]
        try:
            # Calculate ERG value for sorting
            erg_value = calculate_erg_value(amount, currency, conversion_rates)
            bounty["erg_value"] = erg_value
        except (ValueError, TypeError):
            bounty["erg_value"] = 0.0
    
    # Sort bounties by ERG value (highest first)
    return sorted(bounties, key=lambda x: x.get("erg_value", 0.0), reverse=True)

def update_partially_generated_file(
    file_path: str,
    start_marker: str,
    end_marker: str,
    new_content: str
) -> bool:
    """
    Update a section in a partially generated file with new content surrounded by guardrails.
    
    Args:
        file_path: Path to the file
        start_marker: Start marker for the section to replace
        end_marker: End marker for the section to replace
        new_content: New content to insert
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the existing file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the section to replace
        start_index = content.find(start_marker)
        if start_index == -1:
            logger.error(f"Start marker '{start_marker}' not found in {file_path}")
            return False
        
        # Find the end marker after the start marker
        end_index = content.find(end_marker, start_index)
        if end_index == -1:
            logger.error(f"End marker '{end_marker}' not found after start marker in {file_path}")
            return False
        
        # Create the wrapped content
        wrapped_content = start_marker + "\n" + PARTIAL_SECTION_HEADER + new_content + PARTIAL_SECTION_FOOTER + end_marker
        
        # Replace the section
        new_file_content = content[:start_index] + wrapped_content + content[end_index + len(end_marker):]
        
        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_file_content)
        
        logger.info(f"Successfully updated section in {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating {file_path}: {e}")
        return False
