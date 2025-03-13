"""
Module for updating the README.md file with bounty information.
"""

import re
import logging
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
        
        # Get the current date
        current_date = datetime.now().strftime("%b %d, %Y")
        
        # Create the new table row for the current date
        new_row = f"| {current_date} | {total_bounties} | **{total_value:,.2f} ERG**|"
        
        # Calculate the new total (fixed values + dynamic value)
        # Fixed values: 3,000 ERG (Keystone) + 775 SigUSD (Fleet SDK)
        total_count = total_bounties + 7 + 1  # 7 Fleet SDK + 1 Keystone
        total_erg_value = total_value + 3000  # 3000 ERG for Keystone
        
        # Create the new total row
        new_total_row = f"| **Total**                   | **{total_count}**     | **{total_erg_value:,.2f} ERG**|"
        
        # Find the table in the README.md file and update the third row and total row
        table_pattern = r"\| Week\s*\|\s*(?:Count of Open Issues|Open Issues)\s*\|\s*(?:ERG Bounties|Rewards)\s*\|\s*\n\|[-\s|]*\n\|[^\n]*\n\|[^\n]*\n\|[^\n]*\n\|[^\n]*\n"
        
        # Create the replacement table
        replacement_table = f"""| Week                        | Open Issues | Rewards         |
|-----------------------------|-------------|-----------------|
| Keystone Wallet Integration | [Last Update](https://discord.com/channels/668903786361651200/669989266478202917/1344310506277830697) | **3,000 ERG**   |
| [Fleet SDK Tutorials](https://github.com/fleet-sdk/docs/issues/8) | 7           | **775 SigUSD**  |
| {current_date}                | {total_bounties}         | **{total_value:,.2f} ERG**|
| **Total**                   | **{total_count}**     | **{total_erg_value:,.2f} ERG**|"""
        
        # Replace the table in the README.md file
        updated_readme = re.sub(table_pattern, replacement_table, readme_content)
        
        # Update the badges in the README.md file
        # Update the Open Bounties badge
        open_bounties_pattern = r'<a href="/bounties/all\.md"><img src="https://img\.shields\.io/badge/Open%20Bounties-\d+%2B-brightgreen" alt="Open Bounties"></a>'
        open_bounties_replacement = f'<a href="/bounties/all.md"><img src="https://img.shields.io/badge/Open%20Bounties-{total_bounties}%2B-brightgreen" alt="Open Bounties"></a>'
        updated_readme = re.sub(open_bounties_pattern, open_bounties_replacement, updated_readme)
        
        # Update the High Value badge - calculate from actual bounty data if available
        high_value_pattern = r'<a href="/bounties/all\.md"><img src="https://img\.shields\.io/badge/🌟%20High%20Value-\d+%2B%20Over%201000%20ERG-gold" alt="High Value Bounties"></a>'
        
        # Calculate high value bounty count if bounty_data and conversion_rates are provided
        high_value_count = 3  # Default value
        if bounty_data and conversion_rates:
            from ..utils import calculate_erg_value
            
            # Count bounties with value over 1000 ERG
            high_value_count = 0
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
        
        high_value_replacement = f'<a href="/bounties/all.md"><img src="https://img.shields.io/badge/🌟%20High%20Value-{high_value_count}%2B%20Over%201000%20ERG-gold" alt="High Value Bounties"></a>'
        updated_readme = re.sub(high_value_pattern, high_value_replacement, updated_readme)
        
        # Update the Beginner Friendly badge - calculate from actual bounty data if available
        beginner_friendly_pattern = r'<a href="/bounties/all\.md"><img src="https://img\.shields\.io/badge/🚀%20Beginner%20Friendly-\d+%2B%20Bounties-success" alt="Beginner Friendly"></a>'
        
        # Calculate beginner friendly bounty count if bounty_data is provided
        beginner_friendly_count = 15  # Default value
        if bounty_data:
            # Count bounties with "beginner" or "beginner-friendly" in labels
            beginner_friendly_count = 0
            for bounty in bounty_data:
                labels = bounty.get("labels", [])
                if any("beginner" in label.lower() for label in labels):
                    beginner_friendly_count += 1
            
            logger.info(f"Found {beginner_friendly_count} beginner-friendly bounties")
        
        beginner_friendly_replacement = f'<a href="/bounties/all.md"><img src="https://img.shields.io/badge/🚀%20Beginner%20Friendly-{beginner_friendly_count}%2B%20Bounties-success" alt="Beginner Friendly"></a>'
        updated_readme = re.sub(beginner_friendly_pattern, beginner_friendly_replacement, updated_readme)
        
        # Update the language badges based on actual language counts
        language_colors = {
            "Scala": "DC322F",
            "Rust": "B7410E",
            "JavaScript": "F7DF1E",
            "TypeScript": "3178C6",
            "Python": "3776AB",
            "Java": "007396"
        }
        
        # If languages data is provided, use it to update the badges
        if languages:
            # Calculate language counts from the provided data
            language_counts = {lang: len(bounties) for lang, bounties in languages.items()}
            
            # Update badges for each language
            for lang, count in language_counts.items():
                lang_pattern = rf'<a href="/bounties/by_language/{lang.lower()}\.md"><img src="https://img\.shields\.io/badge/{lang}-\d+%20Bounties-[0-9A-F]{{6}}" alt="{lang}"></a>'
                lang_color = language_colors.get(lang, "DC322F")
                lang_replacement = f'<a href="/bounties/by_language/{lang.lower()}.md"><img src="https://img.shields.io/badge/{lang}-{count}%20Bounties-{lang_color}" alt="{lang}"></a>'
                updated_readme = re.sub(lang_pattern, lang_replacement, updated_readme)
        
        # Write the updated README.md file
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(updated_readme)
            
        logger.info("Updated README.md with new bounty counts, values, and badges")
    except Exception as e:
        logger.error(f"Error updating README.md: {e}")
