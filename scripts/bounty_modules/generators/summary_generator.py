"""
Module for generating summary markdown files.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any

from ..utils import ensure_directory, create_claim_url, calculate_erg_value
from .. import markdown_templates as mt

# Configure logging
logger = logging.getLogger('summary_generator')

def generate_main_file(
    bounty_data: List[Dict[str, Any]], 
    project_totals: Dict[str, Dict[str, Any]], 
    languages: Dict[str, List[Dict[str, Any]]], 
    currencies_dict: Dict[str, List[Dict[str, Any]]], 
    orgs: Dict[str, List[Dict[str, Any]]], 
    conversion_rates: Dict[str, float], 
    total_bounties: int, 
    total_value: float, 
    bounties_dir: str
) -> None:
    """
    Generate the main markdown file with all bounties.
    
    Args:
        bounty_data: List of bounty data
        project_totals: Dictionary of project totals
        languages: Dictionary of languages and their bounties
        currencies_dict: Dictionary of currencies and their bounties
        orgs: Dictionary of organizations and their bounties
        conversion_rates: Dictionary of conversion rates
        total_bounties: Total number of bounties
        total_value: Total value of bounties
        bounties_dir: Bounties directory
    """
    logger.info("Generating main bounty file")
    
    md_file = f'{bounties_dir}/all.md'
    
    # Build content with guardrails
    content = ""
    
    # Add navigation section
    content += mt.generate_navigation_section(
        total_bounties, 
        len(languages), 
        len(currencies_dict), 
        len(orgs), 
        len(conversion_rates)
    )
    
    # Add filter section
    content += mt.generate_filter_section(
        languages, 
        currencies_dict, 
        orgs
    )
    
    # Check if there are any ongoing programs
    ongoing_programs = [b for b in bounty_data if b["amount"] == "Ongoing"]
    
    if ongoing_programs:
        # Write ongoing programs section with link to dedicated page
        content += "## Ongoing Reward Programs\n\n"
        content += "The Ergo ecosystem offers ongoing reward programs to encourage continuous contributions in key areas.\n\n"
        content += "**[View Ongoing Programs →](/docs/ongoing-programs.md)**\n\n"
    
    # Add bounties table
    content += "## All Bounties\n\n"
    content += mt.generate_standard_bounty_table(bounty_data, conversion_rates)
    
    # Add footer with action buttons
    content += mt.add_footer_buttons()
    
    # Wrap the entire content with guardrails
    final_content = mt.wrap_with_full_guardrails(content, "# All Open Bounties")
    
    # Write to file
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    logger.info("Generated main bounty file")

def generate_summary_file(
    project_totals: Dict[str, Dict[str, Any]], 
    languages: Dict[str, List[Dict[str, Any]]], 
    currencies_dict: Dict[str, List[Dict[str, Any]]], 
    orgs: Dict[str, List[Dict[str, Any]]], 
    conversion_rates: Dict[str, float], 
    total_bounties: int, 
    total_value: float, 
    bounties_dir: str
) -> None:
    """
    Generate a summary markdown file for README reference.
    
    Args:
        project_totals: Dictionary of project totals
        languages: Dictionary of languages and their bounties
        currencies_dict: Dictionary of currencies and their bounties
        orgs: Dictionary of organizations and their bounties
        conversion_rates: Dictionary of conversion rates
        total_bounties: Total number of bounties
        total_value: Total value of bounties
        bounties_dir: Bounties directory
    """
    logger.info("Generating summary file")
    
    summary_file = f'{bounties_dir}/summary.md'
    
    # Build content
    content = "## 📋 Open Bounties\n\n"
    content += f"**[View Current Open Bounties →](/{bounties_dir}/all.md)**\n\n"
    
    # Add navigation badges
    content += mt.generate_navigation_section(
        total_bounties, 
        len(languages), 
        len(currencies_dict), 
        len(orgs), 
        len(conversion_rates), 
        f"/{bounties_dir}/"
    )
    
    # Projects section
    content += "## Projects\n\n"
    content += "| Project | Count | Value |\n"
    content += "|----------|-------|-------|\n"
    
    # Add rows for major projects (those with more than 1 bounty)
    for owner, totals in sorted(project_totals.items(), key=lambda x: x[1]["value"], reverse=True):
        if totals["count"] > 0:
            # Add link to organization page
            org_link = f"[{owner}](/{bounties_dir}/by_org/{owner.lower()}.md)"
            content += f"| {org_link} | {totals['count']} | {totals['value']:,.2f} ERG |\n"
    
    # Add overall total
    content += f"| **Total** | **{total_bounties}** | **{total_value:,.2f} ERG** |\n\n"
    
    # Calculate totals by currency (excluding bounties with "Not specified" amounts)
    currency_totals = {}
    for currency, currency_bounties in currencies_dict.items():
        # Count only bounties with specified amounts (excluding "Ongoing" programs)
        specified_bounties = [b for b in currency_bounties if b["amount"] != "Not specified" and b["amount"] != "Ongoing"]
        currency_totals[currency] = {"count": len(specified_bounties), "value": 0.0}
        
        for bounty in specified_bounties:
            amount = bounty["amount"]
            currency_totals[currency]["value"] += calculate_erg_value(amount, currency, conversion_rates)
    
    # Add currency breakdown
    content += "## Currencies\n\n"
    content += "| Currency | Count | Total Value (ERG) |\n"
    content += "|----------|-------|------------------|\n"
    
    # Write currency rows
    for currency, totals in sorted(currency_totals.items(), key=lambda x: x[1]["value"], reverse=True)[:5]:  # Top 5 currencies
        # Format the currency name for the file link
        currency_file_name = mt.format_currency_filename(currency)
        
        # Add link to currency page
        currency_link = f"[{currency}](/{bounties_dir}/by_currency/{currency_file_name}.md)"
        
        content += f"| {currency_link} | {totals['count']} | {totals['value']:.2f} |\n"
    
    content += f"\n[View all currencies →](/{bounties_dir}/by_currency/)\n\n"
    
    # Add language breakdown
    content += "## Languages\n\n"
    content += "| Language | Count | Percentage |\n"
    content += "|----------|-------|------------|\n"
    
    # Write language rows
    for lang, lang_bounties in sorted(languages.items(), key=lambda x: len(x[1]), reverse=True)[:5]:  # Top 5 languages
        count = len(lang_bounties)
        percentage = (count / total_bounties) * 100 if total_bounties > 0 else 0
        content += f"| [{lang}](/{bounties_dir}/by_language/{lang.lower()}.md) | {count} | {percentage:.1f}% |\n"
    
    content += f"\n[View all languages →](/{bounties_dir}/by_language/)\n\n"
    
    content += "Open bounties are updated daily with values shown in ERG equivalent. Some bounties may be paid in other tokens as noted in the \"Paid in\" column of the bounty listings.\n"
    
    content += f"\n[View current currency prices →](/{bounties_dir}/currency_prices.md)\n"
    
    # Add footer with action buttons
    content += mt.add_footer_buttons()
    
    # Wrap the entire content with guardrails
    final_content = mt.wrap_with_full_guardrails(content, "# Summary of Bounties")
    
    # Write to file
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    logger.info("Generated summary file")

def update_ongoing_programs_table(
    bounty_data: List[Dict[str, Any]], 
    bounties_dir: str
) -> None:
    """
    Update the table in the ongoing programs markdown file.
    
    Args:
        bounty_data: List of bounty data
        bounties_dir: Bounties directory
    """
    logger.info("Updating ongoing programs table")
    
    # Filter for ongoing programs
    ongoing_programs = [b for b in bounty_data if b["amount"] == "Ongoing"]
    
    if not ongoing_programs:
        logger.info("No ongoing programs found, skipping table update")
        return
    
    # Generate the table content
    table_content = mt.generate_ongoing_programs_table(ongoing_programs)
    
    # Update the file with guardrails
    success = mt.update_partially_generated_file(
        'docs/ongoing-programs.md',
        "## Current Ongoing Programs",
        "## 📚 Educational Reward Program",
        table_content
    )
    
    if success:
        logger.info("Successfully updated ongoing programs table with guardrails")
    else:
        logger.error("Failed to update ongoing programs table with guardrails")

def generate_featured_bounties_file(
    bounty_data: List[Dict[str, Any]], 
    conversion_rates: Dict[str, float], 
    total_bounties: int, 
    total_value: float,
    languages: Dict[str, List[Dict[str, Any]]], 
    currencies_dict: Dict[str, List[Dict[str, Any]]], 
    orgs: Dict[str, List[Dict[str, Any]]], 
    bounties_dir: str
) -> None:
    """
    Generate a featured bounties markdown file.
    
    Args:
        bounty_data: List of bounty data
        conversion_rates: Dictionary of conversion rates
        total_bounties: Total number of bounties
        total_value: Total value of bounties
        languages: Dictionary of languages and their bounties
        currencies_dict: Dictionary of currencies and their bounties
        orgs: Dictionary of organizations and their bounties
        bounties_dir: Bounties directory
    """
    logger.info("Generating featured bounties file")
    
    featured_bounties_file = f'{bounties_dir}/featured_bounties.md'
    
    # Build content
    content = ""
    
    # Add navigation section
    content += mt.generate_navigation_section(
        total_bounties, 
        len(languages), 
        len(currencies_dict), 
        len(orgs), 
        len(conversion_rates)
    )
    
    # Get current date for the week row
    current_date = datetime.now().strftime("%b %d, %Y")
    
    # Find top 2 highest value bounties to feature
    top_bounties = []
    for bounty in bounty_data:
        amount = bounty["amount"]
        currency = bounty["currency"]
        title = bounty["title"]
        url = bounty["url"]
        owner = bounty["owner"]
        
        if amount != "Not specified" and amount != "Ongoing":
            try:
                # Convert to ERG equivalent
                value = calculate_erg_value(amount, currency, conversion_rates)
                
                top_bounties.append({
                    "title": title,
                    "value": value,
                    "amount": amount,
                    "currency": currency,
                    "url": url,
                    "owner": owner
                })
            except ValueError:
                pass
    
    # Sort by value and get top 2
    top_bounties.sort(key=lambda x: x["value"], reverse=True)
    top_bounties = top_bounties[:2]
    
    # Write the featured bounties table
    content += "## Top Bounties by Value\n\n"
    content += "| Bounty | Organization | Value | Currency |\n"
    content += "|--------|--------------|-------|----------|\n"
    
    # Add rows for featured bounties
    for bounty in top_bounties:
        # Format the currency name for the file link
        currency = bounty["currency"]
        currency_file_name = mt.format_currency_filename(currency)
        
        # Add links to organization and currency pages
        org_link = mt.format_organization_link(bounty['owner'])
        currency_link = mt.format_currency_link(currency)
        
        # Calculate ERG equivalent
        erg_equiv = bounty["value"]
        
        content += f"| [{bounty['title']}]({bounty['url']}) | {org_link} | {erg_equiv:.2f} ERG | {currency_link} |\n"
    
    content += "\n## Weekly Summary\n\n"
    content += "| Date | Open Bounties | Total Value |\n"
    content += "|------|--------------|-------------|\n"
    content += f"| {current_date} | {total_bounties} | {total_value:,.2f} ERG |\n\n"

    # Add footer with action buttons
    content += mt.add_footer_buttons()
    
    # Wrap the entire content with guardrails
    final_content = mt.wrap_with_full_guardrails(content, "# Featured Bounties")
    
    # Write to file
    with open(featured_bounties_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    logger.info("Generated featured bounties file")
