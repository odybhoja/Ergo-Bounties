#!/usr/bin/env python3
"""
Output Generators Module

This module contains functions for generating various markdown output files:
- Language-specific files
- Organization-specific files
- Currency-specific files
- Summary files
- Featured bounties
- High-value bounties
- Price tables

Each generator function follows a similar pattern: it takes input data, processes it, 
formats markdown content, and writes output files.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any

from ..utils.common import ensure_directory, get_current_timestamp, create_claim_url
from ..utils.markdown import (
    generate_navigation_section,
    generate_filter_section,
    generate_standard_bounty_table,
    generate_ongoing_programs_table,
    update_readme_badges,
    update_partially_generated_file,
    wrap_with_full_guardrails,
    add_footer_buttons,
    format_currency_filename,
    format_currency_link,
    format_organization_link,
    format_language_link
)
from ..api.currency_client import CurrencyClient

# Configure logging
logger = logging.getLogger(__name__)

def generate_language_files(
    bounty_data: List[Dict[str, Any]], 
    languages: Dict[str, List[Dict[str, Any]]], 
    conversion_rates: Dict[str, float], 
    total_bounties: int, 
    currencies_count: int, 
    orgs_count: int, 
    bounties_dir: str
) -> None:
    """
    Generate language-specific markdown files.
    
    Args:
        bounty_data: List of bounty data
        languages: Dictionary of languages and their bounties
        conversion_rates: Dictionary of conversion rates
        total_bounties: Total number of bounties
        currencies_count: Number of currencies
        orgs_count: Number of organizations
        bounties_dir: Bounties directory
    """
    logger.info(f"Generating language-specific files for {len(languages)} languages")
    
    # Create a directory for language-specific files if it doesn't exist
    language_dir = f'{bounties_dir}/by_language'
    ensure_directory(language_dir)
    
    # Set up currency client for value calculations
    currency_client = CurrencyClient()
    currency_client.rates = conversion_rates
    
    # Write language-specific Markdown files
    for language, language_bounties in languages.items():
        language_file = f'{language_dir}/{language.lower()}.md'
        logger.debug(f"Writing language file: {language_file}")
        
        # Calculate total value for this language
        language_value = sum(
            currency_client.calculate_erg_value(b["amount"], b["currency"])
            for b in language_bounties 
            if b["amount"] != "Not specified" and b["amount"] != "Ongoing"
        )
        
        # Build content
        content = ""
        
        # Add timestamp and stats
        content += f"# {language} Bounties\n\n"
        content += f"*Report generated: {get_current_timestamp()} UTC*\n\n"
        content += f"Total {language} bounties: **{len(language_bounties)}**\n\n"
        content += f"Total value: **{language_value:.2f} ERG**\n\n"
        
        # Add navigation badges
        content += generate_navigation_section(
            total_bounties, 
            len(languages), 
            currencies_count, 
            orgs_count, 
            len(conversion_rates), 
            "../"
        )
        
        # Add filter section based on parent categories
        content += "## Filter by Category\n\n"
        
        # Group by org for this language
        orgs_in_language = {}
        for bounty in language_bounties:
            org = bounty["owner"]
            if org not in orgs_in_language:
                orgs_in_language[org] = []
            orgs_in_language[org].append(bounty)
        
        # Organizations
        content += "**Organizations using {language}:** ".format(language=language)
        org_links = []
        for org_name, org_bounties_list in orgs_in_language.items():
            org_links.append(f"[{org_name} ({len(org_bounties_list)})](../by_org/{org_name.lower()}.md)")
        content += " • ".join(org_links)
        content += "\n\n"
        
        # Group by currency for this language
        currencies_in_language = {}
        for bounty in language_bounties:
            currency = bounty["currency"]
            if currency not in currencies_in_language:
                currencies_in_language[currency] = []
            currencies_in_language[currency].append(bounty)
        
        # Currencies
        content += "**Currencies for {language} bounties:** ".format(language=language)
        currency_links = []
        for currency_name, currency_bounties_list in currencies_in_language.items():
            currency_file_name = format_currency_filename(currency_name)
            currency_links.append(f"[{currency_name} ({len(currency_bounties_list)})](../by_currency/{currency_file_name}.md)")
        content += " • ".join(currency_links)
        content += "\n\n"
        
        # Add bounties table
        content += "## {language} Bounties\n\n".format(language=language)
        content += generate_standard_bounty_table(language_bounties, conversion_rates)
        
        # Add footer with action buttons
        content += add_footer_buttons("../")
        
        # Wrap with guardrails
        final_content = wrap_with_full_guardrails(content, f"# {language} Bounties")
        
        # Write to file
        with open(language_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
    
    logger.info(f"Generated {len(languages)} language-specific files")

def generate_organization_files(
    bounty_data: List[Dict[str, Any]], 
    orgs: Dict[str, List[Dict[str, Any]]], 
    conversion_rates: Dict[str, float], 
    total_bounties: int, 
    languages: Dict[str, List[Dict[str, Any]]], 
    currencies_count: int, 
    bounties_dir: str
) -> None:
    """
    Generate organization-specific markdown files.
    
    Args:
        bounty_data: List of bounty data
        orgs: Dictionary of organizations and their bounties
        conversion_rates: Dictionary of conversion rates
        total_bounties: Total number of bounties
        languages: Dictionary of languages and their bounties
        currencies_count: Number of currencies
        bounties_dir: Bounties directory
    """
    logger.info(f"Generating organization-specific files for {len(orgs)} organizations")
    
    # Create a directory for organization-specific files if it doesn't exist
    org_dir = f'{bounties_dir}/by_org'
    ensure_directory(org_dir)
    
    # Set up currency client for value calculations
    currency_client = CurrencyClient()
    currency_client.rates = conversion_rates
    
    # Write organization-specific Markdown files
    for org, org_bounties in orgs.items():
        org_file = f'{org_dir}/{org.lower()}.md'
        logger.debug(f"Writing organization file: {org_file}")
        
        # Calculate total value for this organization
        org_value = sum(
            currency_client.calculate_erg_value(b["amount"], b["currency"])
            for b in org_bounties 
            if b["amount"] != "Not specified" and b["amount"] != "Ongoing"
        )
        
        # Build content
        content = ""
        
        # Add timestamp and stats
        content += f"# {org} Bounties\n\n"
        content += f"*Report generated: {get_current_timestamp()} UTC*\n\n"
        content += f"Total {org} bounties: **{len(org_bounties)}**\n\n"
        content += f"Total value: **{org_value:.2f} ERG**\n\n"
        
        # Add navigation badges
        content += generate_navigation_section(
            total_bounties, 
            len(languages), 
            currencies_count, 
            len(orgs), 
            len(conversion_rates), 
            "../"
        )
        
        # Add filter section based on parent categories
        content += "## Filter by Category\n\n"
        
        # Group by language for this org
        languages_in_org = {}
        for bounty in org_bounties:
            lang = bounty["primary_lang"]
            if lang not in languages_in_org:
                languages_in_org[lang] = []
            languages_in_org[lang].append(bounty)
        
        # Languages
        content += "**Languages used by {org}:** ".format(org=org)
        lang_links = []
        for lang_name, lang_bounties_list in languages_in_org.items():
            lang_links.append(f"[{lang_name} ({len(lang_bounties_list)})](../by_language/{lang_name.lower()}.md)")
        content += " • ".join(lang_links)
        content += "\n\n"
        
        # Group by currency for this org
        currencies_in_org = {}
        for bounty in org_bounties:
            currency = bounty["currency"]
            if currency not in currencies_in_org:
                currencies_in_org[currency] = []
            currencies_in_org[currency].append(bounty)
        
        # Currencies
        content += "**Currencies offered by {org}:** ".format(org=org)
        currency_links = []
        for currency_name, currency_bounties_list in currencies_in_org.items():
            currency_file_name = format_currency_filename(currency_name)
            currency_links.append(f"[{currency_name} ({len(currency_bounties_list)})](../by_currency/{currency_file_name}.md)")
        content += " • ".join(currency_links)
        content += "\n\n"
        
        # Add bounties table
        content += "## {org} Bounties\n\n".format(org=org)
        content += generate_standard_bounty_table(org_bounties, conversion_rates)
        
        # Add footer with action buttons
        content += add_footer_buttons("../")
        
        # Wrap with guardrails
        final_content = wrap_with_full_guardrails(content, f"# {org} Bounties")
        
        # Write to file
        with open(org_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
    
    logger.info(f"Generated {len(orgs)} organization-specific files")

def generate_currency_files(
    bounty_data: List[Dict[str, Any]], 
    currencies_dict: Dict[str, List[Dict[str, Any]]], 
    conversion_rates: Dict[str, float], 
    total_bounties: int, 
    languages: Dict[str, List[Dict[str, Any]]], 
    orgs: Dict[str, List[Dict[str, Any]]], 
    bounties_dir: str
) -> None:
    """
    Generate currency-specific markdown files.
    
    Args:
        bounty_data: List of bounty data
        currencies_dict: Dictionary of currencies and their bounties
        conversion_rates: Dictionary of conversion rates
        total_bounties: Total number of bounties
        languages: Dictionary of languages and their bounties
        orgs: Dictionary of organizations and their bounties
        bounties_dir: Bounties directory
    """
    logger.info(f"Generating currency-specific files for {len(currencies_dict)} currencies")
    
    # Create a directory for currency-specific files if it doesn't exist
    currency_dir = f'{bounties_dir}/by_currency'
    ensure_directory(currency_dir)
    
    # Set up currency client for value calculations
    currency_client = CurrencyClient()
    currency_client.rates = conversion_rates
    
    # Write currency-specific Markdown files
    for currency, currency_bounties in currencies_dict.items():
        # Skip "Not specified" currency if present
        if currency == "Not specified":
            logger.info("Skipping 'Not specified' currency")
            continue
            
        # Format the currency name for the file
        currency_file_name = format_currency_filename(currency)
        currency_file = f'{currency_dir}/{currency_file_name}.md'
        logger.debug(f"Writing currency file: {currency_file}")
        
        # Calculate total value for this currency
        currency_value = sum(
            currency_client.calculate_erg_value(b["amount"], currency)
            for b in currency_bounties 
            if b["amount"] != "Not specified" and b["amount"] != "Ongoing"
        )
        
        # Build content
        content = ""
        
        # Add timestamp and stats
        content += f"# {currency} Bounties\n\n"
        content += f"*Report generated: {get_current_timestamp()} UTC*\n\n"
        content += f"Total {currency} bounties: **{len(currency_bounties)}**\n\n"
        content += f"Total value: **{currency_value:.2f} ERG**\n\n"
        
        # Add navigation badges
        content += generate_navigation_section(
            total_bounties, 
            len(languages), 
            len(currencies_dict), 
            len(orgs), 
            len(conversion_rates), 
            "../"
        )
        
        # Add filter section based on parent categories
        content += "## Filter by Category\n\n"
        
        # Group by language for this currency
        languages_in_currency = {}
        for bounty in currency_bounties:
            lang = bounty["primary_lang"]
            if lang not in languages_in_currency:
                languages_in_currency[lang] = []
            languages_in_currency[lang].append(bounty)
        
        # Languages
        content += "**Languages for {currency} bounties:** ".format(currency=currency)
        lang_links = []
        for lang_name, lang_bounties_list in languages_in_currency.items():
            lang_links.append(f"[{lang_name} ({len(lang_bounties_list)})](../by_language/{lang_name.lower()}.md)")
        content += " • ".join(lang_links)
        content += "\n\n"
        
        # Group by org for this currency
        orgs_in_currency = {}
        for bounty in currency_bounties:
            org = bounty["owner"]
            if org not in orgs_in_currency:
                orgs_in_currency[org] = []
            orgs_in_currency[org].append(bounty)
        
        # Organizations
        content += "**Organizations offering {currency}:** ".format(currency=currency)
        org_links = []
        for org_name, org_bounties_list in orgs_in_currency.items():
            org_links.append(f"[{org_name} ({len(org_bounties_list)})](../by_org/{org_name.lower()}.md)")
        content += " • ".join(org_links)
        content += "\n\n"
        
        # Add conversion rate if available
        if currency in conversion_rates:
            content += f"## Current {currency} Rate\n\n"
            
            # Get list of currencies that don't need rate inversion
            no_rate_inversion = ["gGOLD"]
            
            # Invert the rate to show ERG per token (except for currencies in no_rate_inversion)
            display_rate = conversion_rates[currency]
            if currency not in no_rate_inversion:
                display_rate = 1.0 / display_rate if display_rate > 0 else 0.0
            
            content += f"1 {currency} = {display_rate:.6f} ERG\n\n"
        
        # Add bounties table
        content += "## {currency} Bounties\n\n".format(currency=currency)
        content += generate_standard_bounty_table(currency_bounties, conversion_rates)
        
        # Add footer with action buttons
        content += add_footer_buttons("../")
        
        # Wrap with guardrails
        final_content = wrap_with_full_guardrails(content, f"# {currency} Bounties")
        
        # Write to file
        with open(currency_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
    
    # Don't forget the "Not specified" currency
    not_specified_bounties = [
        b for b in bounty_data if b["currency"] == "Not specified"
    ]
    
    if not_specified_bounties:
        not_specified_file = f'{currency_dir}/not_specified.md'
        logger.debug(f"Writing not specified currency file: {not_specified_file}")
        
        # Build content
        content = ""
        
        # Add timestamp and stats
        content += "# Bounties with Unspecified Value\n\n"
        content += f"*Report generated: {get_current_timestamp()} UTC*\n\n"
        content += f"Total unspecified value bounties: **{len(not_specified_bounties)}**\n\n"
        
        # Add navigation badges
        content += generate_navigation_section(
            total_bounties, 
            len(languages), 
            len(currencies_dict) + 1,  # +1 for "Not specified"
            len(orgs), 
            len(conversion_rates), 
            "../"
        )
        
        # Add bounties table
        content += "## Bounties with Unspecified Value\n\n"
        content += generate_standard_bounty_table(not_specified_bounties, conversion_rates)
        
        # Add footer with action buttons
        content += add_footer_buttons("../")
        
        # Wrap with guardrails
        final_content = wrap_with_full_guardrails(content, "# Bounties with Unspecified Value")
        
        # Write to file
        with open(not_specified_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
    
    logger.info(f"Generated {len(currencies_dict)} currency-specific files")

def generate_price_table(
    conversion_rates: Dict[str, float], 
    total_bounties: int, 
    languages: Dict[str, List[Dict[str, Any]]], 
    currencies_dict: Dict[str, List[Dict[str, Any]]], 
    orgs: Dict[str, List[Dict[str, Any]]], 
    bounties_dir: str
) -> None:
    """
    Generate a currency price table markdown file.
    
    Args:
        conversion_rates: Dictionary of conversion rates
        total_bounties: Total number of bounties
        languages: Dictionary of languages and their bounties
        currencies_dict: Dictionary of currencies and their bounties
        orgs: Dictionary of organizations and their bounties
        bounties_dir: Bounties directory
    """
    logger.info("Generating currency price table")
    
    price_table_file = f'{bounties_dir}/currency_prices.md'
    
    # Build content
    content = ""
    
    # Add timestamp
    content += "# Currency Prices\n\n"
    content += f"*Report generated: {get_current_timestamp()} UTC*\n\n"
    
    # Add navigation badges
    content += generate_navigation_section(
        total_bounties, 
        len(languages), 
        len(currencies_dict), 
        len(orgs), 
        len(conversion_rates)
    )
    
    # Add filter section
    content += generate_filter_section(
        languages, 
        currencies_dict, 
        orgs
    )
    
    # Currency notes mapping
    currency_notes = {
        "SigUSD": "Stablecoin pegged to USD",
        "gGOLD": "Price per gram of gold in ERG",
        "BENE": "Each BENE is worth $1 in ERG",
        "GORT": "Governance token for ErgoDEX",
        "RSN": "Governance token for Rosen Bridge"
    }
    
    # Write price table
    content += "## Current Prices\n\n"
    content += "| Currency | ERG Equivalent | Notes |\n"
    content += "|----------|----------------|-------|\n"
    
    # Add rows for each currency with known conversion rates
    for currency, rate in sorted(conversion_rates.items()):
        # Get notes
        notes = currency_notes.get(currency, "")
        
        # Create currency link
        currency_link = format_currency_link(currency)
        
        # Get list of currencies that don't need rate inversion
        no_rate_inversion = ["gGOLD"]
        
        # Invert the rate to show ERG per token (except for currencies in no_rate_inversion)
        display_rate = rate
        if currency not in no_rate_inversion:
            display_rate = 1.0 / rate if rate > 0 else 0.0
        
        content += f"| {currency_link} | {display_rate:.6f} | {notes} |\n"
    
    content += "\n*Note: These prices are used to calculate ERG equivalents for bounties paid in different currencies.*\n"
    
    # Add section explaining how prices are retrieved
    content += "\n## How Prices are Retrieved\n\n"
    content += "The currency prices are retrieved using different APIs:\n\n"
    
    # SigUSD, GORT, RSN
    content += "### Spectrum API\n\n"
    content += "SigUSD, GORT, and RSN prices are retrieved from the [Spectrum.fi](https://spectrum.fi/) API:\n\n"
    content += "```\n"
    content += "GET https://api.spectrum.fi/v1/price-tracking/markets\n"
    content += "```\n\n"
    content += "The API returns market data for various trading pairs. We filter this data to find specific currency pairs:\n\n"
    content += "- For SigUSD: We look for markets where `quoteSymbol=SigUSD` and `baseSymbol=ERG`\n"
    content += "- For GORT: We look for markets where `quoteSymbol=GORT` and `baseSymbol=ERG`\n"
    content += "- For RSN: We look for markets where `quoteSymbol=RSN` and `baseSymbol=ERG`\n\n"
    
    # BENE
    content += "### BENE\n\n"
    content += "BENE price is set to be equivalent to SigUSD (which is pegged to USD), making 1 BENE equal to $1 worth of ERG.\n\n"
    
    # g GOLD
    content += "### Gold Price from Oracle Pool\n\n"
    content += "The price of gold (g GOLD) is retrieved from the XAU/ERG oracle pool using the Ergo Explorer API:\n\n"
    content += "```\n"
    content += "GET https://api.ergoplatform.com/api/v1/boxes/unspent/byTokenId/3c45f29a5165b030fdb5eaf5d81f8108f9d8f507b31487dd51f4ae08fe07cf4a\n"
    content += "```\n\n"
    content += "This queries for unspent boxes containing the oracle pool NFT. The price is extracted from the R4 register of the latest box.\n\n"
    
    # Add footer with action buttons
    content += add_footer_buttons()
    
    # Wrap with guardrails
    final_content = wrap_with_full_guardrails(content, "# Currency Prices")
    
    # Write to file
    with open(price_table_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    logger.info("Generated currency price table")

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
    
    # Build content
    content = ""
    
    # Add navigation section
    content += generate_navigation_section(
        total_bounties, 
        len(languages), 
        len(currencies_dict), 
        len(orgs), 
        len(conversion_rates)
    )
    
    # Add filter section
    content += generate_filter_section(
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
    content += generate_standard_bounty_table(bounty_data, conversion_rates)
    
    # Add footer with action buttons
    content += add_footer_buttons()
    
    # Wrap the entire content with guardrails
    final_content = wrap_with_full_guardrails(content, "# All Open Bounties")
    
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
    content += generate_navigation_section(
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
    
    # Set up currency client for calculations
    currency_client = CurrencyClient()
    currency_client.rates = conversion_rates
    
    # Calculate totals by currency (excluding bounties with "Not specified" amounts)
    currency_totals = {}
    for currency, currency_bounties in currencies_dict.items():
        # Count only bounties with specified amounts (excluding "Ongoing" programs)
        specified_bounties = [
            b for b in currency_bounties 
            if b["amount"] != "Not specified" and b["amount"] != "Ongoing"
        ]
        
        if specified_bounties:
            currency_totals[currency] = {
                "count": len(specified_bounties),
                "value": sum(
                    currency_client.calculate_erg_value(b["amount"], b["currency"])
                    for b in specified_bounties
                )
            }
    
    # Add currency breakdown
    content += "## Currencies\n\n"
    content += "| Currency | Count | Total Value (ERG) |\n"
    content += "|----------|-------|------------------|\n"
    
    # Write currency rows (top 5 by value)
    for currency, totals in sorted(currency_totals.items(), key=lambda x: x[1]["value"], reverse=True)[:5]:
        # Format the currency name for the file link
        currency_file_name = format_currency_filename(currency)
        
        # Add link to currency page
        currency_link = f"[{currency}](/{bounties_dir}/by_currency/{currency_file_name}.md)"
        
        content += f"| {currency_link} | {totals['count']} | {totals['value']:.2f} |\n"
    
    content += f"\n[View all currencies →](/{bounties_dir}/by_currency/)\n\n"
    
    # Add language breakdown
    content += "## Languages\n\n"
    content += "| Language | Count | Percentage |\n"
    content += "|----------|-------|------------|\n"
    
    # Write language rows (top 5 by count)
    for lang, lang_bounties in sorted(languages.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        count = len(lang_bounties)
        percentage = (count / total_bounties) * 100 if total_bounties > 0 else 0
        content += f"| [{lang}](/{bounties_dir}/by_language/{lang.lower()}.md) | {count} | {percentage:.1f}% |\n"
    
    content += f"\n[View all languages →](/{bounties_dir}/by_language/)\n\n"
    
    content += "Open bounties are updated daily with values shown in ERG equivalent. Some bounties may be paid in other tokens as noted in the \"Paid in\" column of the bounty listings.\n"
    
    content += f"\n[View current currency prices →](/{bounties_dir}/currency_prices.md)\n"
    
    # Add footer with action buttons
    content += add_footer_buttons()
    
    # Wrap with guardrails
    final_content = wrap_with_full_guardrails(content, "# Summary of Bounties")
    
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
    table_content = generate_ongoing_programs_table(ongoing_programs)
    
    # Update the file with guardrails
    success = update_partially_generated_file(
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
    
    from ..core.processor import BountyProcessor
    
    # Set up processor for finding high-value bounties
    processor = BountyProcessor("", conversion_rates)
    processor.bounty_data = bounty_data
    
    # Find top bounties
    featured_bounties = processor.find_featured_bounties(count=2)
    
    featured_bounties_file = f'{bounties_dir}/featured_bounties.md'
    
    # Build content
    content = ""
    
    # Add navigation section
    content += generate_navigation_section(
        total_bounties, 
        len(languages), 
        len(currencies_dict), 
        len(orgs), 
        len(conversion_rates)
    )
    
    # Get current date for the week row
    current_date = datetime.now().strftime("%b %d, %Y")
    
    # Write the featured bounties table
    content += "## Top Bounties by Value\n\n"
    content += "| Bounty | Organization | Value | Currency |\n"
    content += "|--------|--------------|-------|----------|\n"
    
    # Add rows for featured bounties
    for bounty in featured_bounties:
        # Format links
        org_link = format_organization_link(bounty['owner'])
        currency_link = format_currency_link(bounty['currency'])
        
        # Calculate ERG equivalent
        erg_equiv = bounty["value"]
        
        content += f"| [{bounty['title']}]({bounty['url']}) | {org_link} | {erg_equiv:.2f} ERG | {currency_link} |\n"
    
    content += "\n## Weekly Summary\n\n"
    content += "| Date | Open Bounties | Total Value |\n"
    content += "|------|--------------|-------------|\n"
    content += f"| {current_date} | {total_bounties} | {total_value:,.2f} ERG |\n\n"

    # Add footer with action buttons
    content += add_footer_buttons()
    
    # Wrap with guardrails
    final_content = wrap_with_full_guardrails(content, "# Featured Bounties")
    
    # Write to file
    with open(featured_bounties_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    logger.info("Generated featured bounties file")

def generate_high_value_bounties_file(
    bounty_data: List[Dict[str, Any]],
    conversion_rates: Dict[str, float],
    total_bounties: int,
    total_value: float,
    languages: Dict[str, List[Dict[str, Any]]],
    currencies_dict: Dict[str, List[Dict[str, Any]]],
    orgs: Dict[str, List[Dict[str, Any]]],
    bounties_dir: str,
    high_value_threshold: float = 1000.0
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
        high_value_threshold: Minimum ERG value to be considered high-value
    """
    logger.info(f"Generating high-value bounties file (threshold: {high_value_threshold} ERG)")
    
    from ..core.processor import BountyProcessor
    
    # Set up processor for finding high-value bounties
    processor = BountyProcessor("", conversion_rates)
    processor.bounty_data = bounty_data
    
    # Find high-value bounties
    high_value_bounties = processor.find_high_value_bounties(threshold=high_value_threshold)
    
    high_value_file = f'{bounties_dir}/high-value-bounties.md'
    
    # Build content
    content = ""
    
    # Add timestamp and stats
    content += f"# High-Value Bounties (Over {high_value_threshold:,.0f} ERG)\n\n"
    content += f"*Report generated: {get_current_timestamp()} UTC*\n\n"
    content += f"Total high-value bounties: **{len(high_value_bounties)}**\n\n"
    
    # Add navigation badges
    content += generate_navigation_section(
        total_bounties, 
        len(languages), 
        len(currencies_dict), 
        len(orgs), 
        len(conversion_rates)
    )
    
    # Add filter section
    content += generate_filter_section(
        languages, 
        currencies_dict, 
        orgs
    )
    
    # Add high-value bounties table
    content += "## High-Value Bounties\n\n"
    content += "| Bounty | Organization | Value | Currency | Primary Language | Reserve |\n"
    content += "|--------|--------------|-------|----------|------------------|--------|\n"
    
    # Add rows for each high-value bounty
    for bounty in high_value_bounties:
        owner = bounty["owner"]
        repo_name = bounty["repo"]
        title = bounty["title"]
        url = bounty["url"]
        currency = bounty["currency"]
        primary_lang = bounty["primary_lang"]
        issue_number = bounty["issue_number"]
        creator = bounty["creator"]
        amount = bounty["amount"]
        
        # Calculate ERG value
        erg_value = bounty["value"]
        
        # Create a claim link that opens a PR template
        claim_url = create_claim_url(owner, repo_name, issue_number, title, url, currency, amount, creator)
        
        # Add organization, language and currency links
        org_link = format_organization_link(owner)
        primary_lang_link = format_language_link(primary_lang)
        currency_link = format_currency_link(currency)
        
        # Create a reserve button
        reserve_button = f"[<kbd>Reserve</kbd>]({claim_url})"
        
        content += f"| [{title}]({url}) | {org_link} | {erg_value:.2f} ERG | {currency_link} | {primary_lang_link} | {reserve_button} |\n"
    
    # Add footer with action buttons
    content += add_footer_buttons()
    
    # Wrap with guardrails
    final_content = wrap_with_full_guardrails(content, f"# High-Value Bounties (Over {high_value_threshold:,.0f} ERG)")
    
    # Write to file
    with open(high_value_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    logger.info(f"Generated high-value bounties file with {len(high_value_bounties)} bounties")
