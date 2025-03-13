import os
import json
import urllib.parse
from datetime import datetime

def ensure_directory(directory):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory (str): Directory path
    """
    os.makedirs(directory, exist_ok=True)

def create_claim_url(owner, repo_name, issue_number, title, url, currency, amount, creator):
    """
    Create a URL for claiming a bounty.
    
    Args:
        owner (str): Repository owner
        repo_name (str): Repository name
        issue_number (int): Issue number
        title (str): Issue title
        url (str): Issue URL
        currency (str): Bounty currency
        amount (str): Bounty amount
        creator (str): Issue creator
        
    Returns:
        str: Claim URL
    """
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
        "bounty_value": 0 if amount == "Not specified" else float(amount) if amount.replace('.', '', 1).isdigit() else 0,
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
    claim_url = f"https://github.com/ErgoDevs/Ergo-Bounties/new/main?filename=submissions/{owner.lower()}-{repo_name.lower()}-{issue_number}.json&value={encoded_json}&message=Claim%20Bounty%20{owner}/{repo_name}%23{issue_number}&description=I%20want%20to%20claim%20this%20bounty%20posted%20by%20{creator}.%0A%0ABounty:%20{urllib.parse.quote(title)}"
    
    return claim_url

def get_current_timestamp():
    """
    Get current timestamp in a formatted string.
    
    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate_erg_value(amount, currency, conversion_rates):
    """
    Calculate ERG value from amount and currency.
    
    Args:
        amount (str): Amount
        currency (str): Currency
        conversion_rates (dict): Conversion rates
        
    Returns:
        float: ERG value or 0 if conversion not possible
    """
    if amount == "Not specified":
        return 0.0
        
    try:
        if currency == "ERG":
            return float(amount)
        elif currency == "SigUSD" and "SigUSD" in conversion_rates:
            return float(amount) * conversion_rates["SigUSD"]
        elif currency == "GORT" and "GORT" in conversion_rates:
            return float(amount) / conversion_rates["GORT"]
        elif currency == "RSN" and "RSN" in conversion_rates:
            return float(amount) / conversion_rates["RSN"]
        elif currency == "BENE" and "BENE" in conversion_rates:
            return 0.0  # BENE has no value
        elif currency == "g GOLD" and "gGOLD" in conversion_rates:
            return float(amount) * conversion_rates["gGOLD"]
        else:
            return 0.0  # For unknown currencies
    except ValueError:
        return 0.0

def format_navigation_badges(total_bounties, languages_count, currencies_count, orgs_count, conversion_rates_count, relative_path=""):
    """
    Format navigation badges for markdown files.
    
    Args:
        total_bounties (int): Total number of bounties
        languages_count (int): Number of languages
        currencies_count (int): Number of currencies
        orgs_count (int): Number of organizations
        conversion_rates_count (int): Number of conversion rates
        relative_path (str): Relative path for links
        
    Returns:
        str: Formatted navigation badges
    """
    badges = []
    badges.append(f"[![All Bounties](https://img.shields.io/badge/All_Bounties-{total_bounties}-blue)]({relative_path}all.md)")
    badges.append(f"[![By Language](https://img.shields.io/badge/By_Language-{languages_count}-green)]({relative_path}all.md#bounties-by-programming-language)")
    badges.append(f"[![By Currency](https://img.shields.io/badge/By_Currency-{currencies_count}-yellow)]({relative_path}all.md#bounties-by-currency)")
    badges.append(f"[![By Organization](https://img.shields.io/badge/By_Organization-{orgs_count}-orange)]({relative_path}all.md#bounties-by-organization)")
    
    if conversion_rates_count > 0:
        badges.append(f"[![Currency Prices](https://img.shields.io/badge/Currency_Prices-{conversion_rates_count}-purple)]({relative_path}currency_prices.md)")
    
    return " ".join(badges)
