"""
Module for updating the README.md file with bounty information.
"""

import re
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger('readme_updater')

def update_readme_table(
    total_bounties: int, 
    total_value: float, 
    bounties_dir: str, 
    languages_count: int = 0, 
    currencies_count: int = 0, 
    orgs_count: int = 0, 
    conversion_rates_count: int = 0,
    languages: Dict[str, List[Dict[str, Any]]] = None,
    bounty_data: List[Dict[str, Any]] = None,
    conversion_rates: Dict[str, float] = None
) -> None:
    """
    Update the Featured Bounties table and badges in the README.md file.
    
    Args:
        total_bounties: Total number of bounties
        total_value: Total value of bounties in ERG
        bounties_dir: Bounties directory
        languages_count: Number of languages
        currencies_count: Number of currencies
        orgs_count: Number of organizations
        conversion_rates_count: Number of conversion rates
        languages: Dictionary of languages and their bounties (optional)
    """
    logger.info("Updating README.md table and badges")
    
    readme_file = 'README.md'
    
    try:
        # Read the current README.md file
        with open(readme_file, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # Load constants from constants.json
        constants_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'constants.json')
        try:
            with open(constants_path, 'r', encoding='utf-8') as f:
                constants = json.load(f)
                logger.info(f"Loaded constants from {constants_path}")
        except Exception as e:
            logger.error(f"Error loading constants from {constants_path}: {e}")
            raise
        
        # Get the current date
        current_date = datetime.now().strftime("%b %d, %Y")
        
        # Create the new table row for the current date
        new_row = f"| {current_date} | {total_bounties} | **{total_value:,.2f} ERG**|"
        
        # Get fixed bounties from constants
        fleet_sdk = constants["fixed_bounties"]["fleet_sdk"]
        keystone = constants["fixed_bounties"]["keystone"]
        
        # Calculate the new total (fixed values + dynamic value)
        total_count = total_bounties + fleet_sdk["count"] + keystone["count"]
        total_erg_value = total_value + keystone["amount"]  # Keystone is in ERG
        
        # Create the new total row
        new_total_row = f"| **Total**                   | **{total_count}**     | **{total_erg_value:,.2f} ERG**|"
        
        # Find the table in the README.md file and update the third row and total row
        table_pattern = r"\| Week\s*\|\s*(?:Count of Open Issues|Open Issues)\s*\|\s*(?:ERG Bounties|Rewards)\s*\|\s*\n\|[-\s|]*\n\|[^\n]*\n\|[^\n]*\n\|[^\n]*\n\|[^\n]*\n"
        
        # Create the replacement table using values from constants
        replacement_table = f"""| Week                        | Open Issues | Rewards         |
|-----------------------------|-------------|-----------------|
| Keystone Wallet Integration | [Last Update](https://discord.com/channels/668903786361651200/669989266478202917/1344310506277830697) | **{keystone["amount"]:,} {keystone["currency"]}**   |
| [Fleet SDK Tutorials](https://github.com/fleet-sdk/docs/issues/8) | {fleet_sdk["count"]}           | **{fleet_sdk["amount"]} {fleet_sdk["currency"]}**  |
| {current_date}                | {total_bounties}         | **{total_value:,.2f} ERG**|
| **Total**                   | **{total_count}**     | **{total_erg_value:,.2f} ERG**|"""
        
        # Instead of updating an existing README, we'll generate a completely new one
        # with the desired format, while preserving the dynamic badge updates
        
        # Get language colors from constants
        language_colors = constants["language_colors"]
        
        # Use the languages parameter to get language counts
        language_counts = {}
        if languages:
            language_counts = {lang: len(bounties) for lang, bounties in languages.items()}
        
        # Calculate high value bounty count if bounty_data and conversion_rates are provided
        high_value_count = 0
        if bounty_data and conversion_rates:
            from ..utils import calculate_erg_value
            
            # Count bounties with value over 1000 ERG
            for bounty in bounty_data:
                amount = bounty["amount"]
                currency = bounty["currency"]
                
                if amount != "Not specified":
                    try:
                        # Calculate ERG value
                        erg_value = calculate_erg_value(amount, currency, conversion_rates)
                        if erg_value >= 1000:
                            high_value_count += 1
                    except (ValueError, TypeError):
                        pass
            
            logger.info(f"Found {high_value_count} high value bounties (>= 1000 ERG)")
        
        # Calculate beginner friendly bounty count if bounty_data is provided
        beginner_friendly_count = 0
        if bounty_data:
            # Count bounties with "beginner" or "beginner-friendly" in labels
            for bounty in bounty_data:
                labels = bounty.get("labels", [])
                if any("beginner" in label.lower() for label in labels):
                    beginner_friendly_count += 1
            
            logger.info(f"Found {beginner_friendly_count} beginner-friendly bounties")
        
        # Generate language badges HTML
        language_badges = ""
        for lang, count in language_counts.items():
            color = language_colors.get(lang, "DC322F")
            language_badges += f'    <a href="/bounties/by_language/{lang.lower()}.md"><img src="https://img.shields.io/badge/{lang}-{count}-{color}"></a>\n'
        
        # Create the new README content with the desired format
        new_readme = f'''<div align="center">
  <h1>🏆 Ergo Ecosystem Bounties</h1>
  <p><strong>Your Central Hub for Tracking, Claiming, and Managing Bounties on Ergo</strong></p>

  <p>
    <a href="/bounties/all.md"><img src="https://img.shields.io/badge/Open%20Bounties-{total_bounties}%2B-brightgreen" alt="Open Bounties"></a>
    <a href="/bounties/all.md"><img src="https://img.shields.io/badge/💰%20Total%20Value-{total_erg_value:,.2f}%20ERG-success" alt="Total Value"></a>
    <a href="/bounties/all.md"><img src="https://img.shields.io/badge/🌟%20High%20Value-{high_value_count}%2B%20Over%201000%20ERG-gold" alt="High Value Bounties"></a>
   </p>
   
   <p>
    <a href="/bounties/all.md"><img src="https://img.shields.io/badge/📅%20Updated%20Daily-informational" alt="Updated Daily"></a>
    <a href="/docs/how-it-works.md"><img src="https://img.shields.io/badge/🔧%20How%20It%20Works-blue"></a>
    <a href="/docs/how-it-works.md"><img src="https://img.shields.io/badge/💎%20Donate-ff69b4"></a>
  </p>

  <p>
{language_badges.rstrip()}
    <a href="/bounties/by_language/"><img src="https://img.shields.io/badge/🌐%20All%20Languages-purple"></a>
  </p>

  <p>
    <a href="/bounties/all.md"><img src="https://img.shields.io/badge/✅%20Browse-blue"></a> | 
    <a href="/docs/submission-guide.md"><img src="https://img.shields.io/badge/🔒%20Reserve-green"></a> | 
    <a href="/docs/submission-guide.md"><img src="https://img.shields.io/badge/🚩%20Submit-orange"></a> | 
    <a href="/docs/add-missing-bounty-guide.md"><img src="https://img.shields.io/badge/➕%20Add%20Bounty-yellow"></a>
  </p>
</div>


'''
        
        # Use the new README content
        updated_readme = new_readme
        
        # Write the updated README.md file
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(updated_readme)
            
        logger.info("Updated README.md with new bounty counts, values, and badges")
    except Exception as e:
        logger.error(f"Error updating README.md: {e}")
