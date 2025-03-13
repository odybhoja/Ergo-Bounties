import os
import re
from datetime import datetime
from .utils import ensure_directory, create_claim_url, format_navigation_badges, calculate_erg_value
from .conversion_rates import convert_to_erg

def generate_language_files(bounty_data, languages, conversion_rates, total_bounties, currencies_count, orgs_count, bounties_dir):
    """
    Generate language-specific markdown files.
    
    Args:
        bounty_data (list): List of bounty data
        languages (dict): Dictionary of languages and their bounties
        conversion_rates (dict): Dictionary of conversion rates
        total_bounties (int): Total number of bounties
        currencies_count (int): Number of currencies
        orgs_count (int): Number of organizations
        bounties_dir (str): Bounties directory
    """
    # Create a directory for language-specific files if it doesn't exist
    lang_dir = f'{bounties_dir}/by_language'
    ensure_directory(lang_dir)
    
    # Write language-specific Markdown files
    for lang, lang_bounties in languages.items():
        lang_file = f'{lang_dir}/{lang.lower()}.md'
        with open(lang_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# {lang} Bounties\n\n")
            f.write(f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*\n\n")
            f.write(f"Total {lang} bounties: **{len(lang_bounties)}**\n\n")
            
            # Add navigation badges
            f.write("## Navigation\n\n")
            f.write(format_navigation_badges(
                total_bounties, 
                len(languages), 
                currencies_count, 
                orgs_count, 
                len(conversion_rates), 
                "../"
            ))
            f.write("\n\n")
            
            f.write("|Owner|Title & Link|Bounty Amount|Paid in|Secondary Language|Claim|\n")
            f.write("|---|---|---|---|---|---|\n")
            
            # Sort bounties by owner
            lang_bounties.sort(key=lambda x: (x["owner"], x["title"]))
            
            # Add rows for each bounty
            for bounty in lang_bounties:
                owner = bounty["owner"]
                title = bounty["title"]
                url = bounty["url"]
                amount = bounty["amount"]
                currency = bounty["currency"]
                secondary_lang = bounty["secondary_lang"]
                
                # Try to convert to ERG equivalent
                erg_equiv = convert_to_erg(amount, currency, conversion_rates)
                
                # Create a claim link that opens a PR template
                issue_number = bounty["issue_number"]
                creator = bounty["creator"]
                repo_name = bounty["repo"]
                
                claim_url = create_claim_url(owner, repo_name, issue_number, title, url, currency, amount, creator)
                
                # Format the currency name for the file link
                currency_file_name = currency.lower()
                if currency == "g GOLD":
                    currency_file_name = "gold"
                elif currency == "Not specified":
                    currency_file_name = "not_specified"
                
                f.write(f"| {owner} | [{title}]({url}) | {erg_equiv} | [{currency}](../by_currency/{currency_file_name}.md) | {secondary_lang} | [Claim]({claim_url}) |\n")

def generate_organization_files(bounty_data, orgs, conversion_rates, total_bounties, languages, currencies_count, bounties_dir):
    """
    Generate organization-specific markdown files.
    
    Args:
        bounty_data (list): List of bounty data
        orgs (dict): Dictionary of organizations and their bounties
        conversion_rates (dict): Dictionary of conversion rates
        total_bounties (int): Total number of bounties
        languages (dict): Dictionary of languages and their bounties
        currencies_count (int): Number of currencies
        bounties_dir (str): Bounties directory
    """
    # Create a directory for organization-specific files if it doesn't exist
    org_dir = f'{bounties_dir}/by_org'
    ensure_directory(org_dir)
    
    # Write organization-specific Markdown files
    for org, org_bounties in orgs.items():
        org_file = f'{org_dir}/{org.lower()}.md'
        with open(org_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# {org} Bounties\n\n")
            f.write(f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*\n\n")
            f.write(f"Total {org} bounties: **{len(org_bounties)}**\n\n")
            
            # Add navigation badges
            f.write("## Navigation\n\n")
            f.write(format_navigation_badges(
                total_bounties, 
                len(languages), 
                currencies_count, 
                len(orgs), 
                len(conversion_rates), 
                "../"
            ))
            f.write("\n\n")
            
            f.write("|Title & Link|Bounty Amount|Paid in|Primary Language|Secondary Language|Claim|\n")
            f.write("|---|---|---|---|---|---|\n")
            
            # Sort bounties by title
            org_bounties.sort(key=lambda x: x["title"])
            
            # Add rows for each bounty
            for bounty in org_bounties:
                title = bounty["title"]
                url = bounty["url"]
                amount = bounty["amount"]
                currency = bounty["currency"]
                primary_lang = bounty["primary_lang"]
                secondary_lang = bounty["secondary_lang"]
                
                # Try to convert to ERG equivalent
                erg_equiv = convert_to_erg(amount, currency, conversion_rates)
                
                # Create a claim link that opens a PR template
                issue_number = bounty["issue_number"]
                creator = bounty["creator"]
                repo_name = bounty["repo"]
                
                claim_url = create_claim_url(bounty['owner'], repo_name, issue_number, title, url, currency, amount, creator)
                
                # Add language links
                primary_lang_link = f"[{primary_lang}](../by_language/{primary_lang.lower()}.md)"
                
                # Format the currency name for the file link
                currency_file_name = currency.lower()
                if currency == "g GOLD":
                    currency_file_name = "gold"
                elif currency == "Not specified":
                    currency_file_name = "not_specified"
                
                f.write(f"| [{title}]({url}) | {erg_equiv} | [{currency}](../by_currency/{currency_file_name}.md) | {primary_lang_link} | {secondary_lang} | [Claim]({claim_url}) |\n")

def generate_currency_files(bounty_data, currencies_dict, conversion_rates, total_bounties, languages, orgs, bounties_dir):
    """
    Generate currency-specific markdown files.
    
    Args:
        bounty_data (list): List of bounty data
        currencies_dict (dict): Dictionary of currencies and their bounties
        conversion_rates (dict): Dictionary of conversion rates
        total_bounties (int): Total number of bounties
        languages (dict): Dictionary of languages and their bounties
        orgs (dict): Dictionary of organizations and their bounties
        bounties_dir (str): Bounties directory
    """
    # Create a directory for currency-specific files if it doesn't exist
    currency_dir = f'{bounties_dir}/by_currency'
    ensure_directory(currency_dir)
    
    # Write currency-specific Markdown files
    for currency, currency_bounties in currencies_dict.items():
        # Format the currency name for the file
        if currency == "Not specified":
            currency_file_name = "not_specified"
        elif currency == "g GOLD":
            currency_file_name = "gold"
        else:
            currency_file_name = currency.lower()
        
        currency_file = f'{currency_dir}/{currency_file_name}.md'
        with open(currency_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# {currency} Bounties\n\n")
            f.write(f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*\n\n")
            f.write(f"Total {currency} bounties: **{len(currency_bounties)}**\n\n")
            
            # Add navigation badges
            f.write("## Navigation\n\n")
            f.write(format_navigation_badges(
                total_bounties, 
                len(languages), 
                len(currencies_dict), 
                len(orgs), 
                len(conversion_rates), 
                "../"
            ))
            f.write("\n\n")
            
            # Add conversion rate if available
            if currency in conversion_rates:
                f.write(f"## Current {currency} Rate\n\n")
                
                # Invert the rate to show ERG per token (except for gGOLD which is already in ERG per token)
                display_rate = conversion_rates[currency]
                if currency != "gGOLD":
                    display_rate = 1.0 / display_rate if display_rate > 0 else 0.0
                
                f.write(f"1 {currency} = {display_rate:.6f} ERG\n\n")
            
            f.write("|Owner|Title & Link|Bounty Amount|ERG Equivalent|Primary Language|Claim|\n")
            f.write("|---|---|---|---|---|---|\n")
            
            # Sort bounties by owner and title
            currency_bounties.sort(key=lambda x: (x["owner"], x["title"]))
            
            # Add rows for each bounty
            for bounty in currency_bounties:
                owner = bounty["owner"]
                title = bounty["title"]
                url = bounty["url"]
                amount = bounty["amount"]
                primary_lang = bounty["primary_lang"]
                
                # Try to convert to ERG equivalent
                erg_equiv = convert_to_erg(amount, currency, conversion_rates)
                
                # Create a claim link that opens a PR template
                issue_number = bounty["issue_number"]
                creator = bounty["creator"]
                repo_name = bounty["repo"]
                
                claim_url = create_claim_url(owner, repo_name, issue_number, title, url, currency, amount, creator)
                
                # Add organization and language links
                org_link = f"[{owner}](../by_org/{owner.lower()}.md)"
                primary_lang_link = f"[{primary_lang}](../by_language/{primary_lang.lower()}.md)"
                
                f.write(f"| {org_link} | [{title}]({url}) | {amount} | {erg_equiv} | {primary_lang_link} | [Claim]({claim_url}) |\n")

def generate_price_table(conversion_rates, total_bounties, languages, currencies_dict, orgs, bounties_dir):
    """
    Generate a currency price table markdown file.
    
    Args:
        conversion_rates (dict): Dictionary of conversion rates
        total_bounties (int): Total number of bounties
        languages (dict): Dictionary of languages and their bounties
        currencies_dict (dict): Dictionary of currencies and their bounties
        orgs (dict): Dictionary of organizations and their bounties
        bounties_dir (str): Bounties directory
    """
    price_table_file = f'{bounties_dir}/currency_prices.md'
    with open(price_table_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("# Currency Prices\n\n")
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
        
        # Write price table
        f.write("## Current Prices\n\n")
        f.write("| Currency | ERG Equivalent | Notes |\n")
        f.write("|----------|----------------|-------|\n")
        
        # Add rows for each currency with known conversion rates
        for currency, rate in sorted(conversion_rates.items()):
            notes = ""
            if currency == "SigUSD":
                notes = "Stablecoin pegged to USD"
            elif currency == "BENE":
                notes = "No market value"
            elif currency == "gGOLD":
                notes = "Price per gram of gold"
            
            # Format the currency name for display
            display_currency = currency
            if currency == "gGOLD":
                display_currency = "g GOLD"
            
            # Add link to currency page if it exists
            # Format the currency name for the file link
            file_currency = display_currency
            if display_currency == "g GOLD":
                file_currency = "gold"
            
            currency_link = f"[{display_currency}](by_currency/{file_currency.lower()}.md)"
            
            # Invert the rate to show ERG per token (except for gGOLD which is already in ERG per token)
            display_rate = rate
            if currency != "gGOLD":
                display_rate = 1.0 / rate if rate > 0 else 0.0
            
            f.write(f"| {currency_link} | {display_rate:.6f} | {notes} |\n")
        
        f.write("\n*Note: These prices are used to calculate ERG equivalents for bounties paid in different currencies.*\n")

def generate_main_file(bounty_data, project_totals, languages, currencies_dict, orgs, conversion_rates, total_bounties, total_value, bounties_dir):
    """
    Generate the main markdown file.
    
    Args:
        bounty_data (list): List of bounty data
        project_totals (dict): Dictionary of project totals
        languages (dict): Dictionary of languages and their bounties
        currencies_dict (dict): Dictionary of currencies and their bounties
        orgs (dict): Dictionary of organizations and their bounties
        conversion_rates (dict): Dictionary of conversion rates
        total_bounties (int): Total number of bounties
        total_value (float): Total value of bounties
        bounties_dir (str): Bounties directory
    """
    md_file = f'{bounties_dir}/all.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("# Open Bounties\n\n")
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
        
        # Write summary section
        f.write("## Summary\n\n")
        f.write("| Project | Count | ERG Equivalent |\n")
        f.write("|---------|-------|---------------|\n")
        
        for owner, totals in sorted(project_totals.items(), key=lambda x: x[1]["count"], reverse=True):
            if totals["count"] > 0:
                # Add link to organization page
                org_link = f"[{owner}](by_org/{owner.lower()}.md)"
                f.write(f"| {org_link} | {totals['count']} | {totals['value']:.2f} |\n")
        
        f.write(f"| **Overall Total** | **{total_bounties}** | **{total_value:.2f}** |\n\n")
        
        # Write language breakdown section
        f.write("## Bounties by Programming Language\n\n")
        f.write("| Language | Count | Percentage |\n")
        f.write("|----------|-------|------------|\n")
        
        for lang, lang_bounties in sorted(languages.items(), key=lambda x: len(x[1]), reverse=True):
            count = len(lang_bounties)
            percentage = (count / total_bounties) * 100 if total_bounties > 0 else 0
            f.write(f"| [{lang}](by_language/{lang.lower()}.md) | {count} | {percentage:.1f}% |\n")
        
        # Write currency breakdown section
        f.write("\n## Bounties by Currency\n\n")
        f.write("| Currency | Count | Total Value (ERG) |\n")
        f.write("|----------|-------|------------------|\n")
        
        # Calculate totals by currency
        currency_totals = {}
        for bounty in bounty_data:
            currency = bounty["currency"]
            amount = bounty["amount"]
            
            if currency not in currency_totals:
                currency_totals[currency] = {"count": 0, "value": 0.0}
            
            currency_totals[currency]["count"] += 1
            
            # Try to convert to ERG equivalent for total
            currency_totals[currency]["value"] += calculate_erg_value(amount, currency, conversion_rates)
        
        # Write currency rows
        for currency, totals in sorted(currency_totals.items(), key=lambda x: x[1]["count"], reverse=True):
            # Format the currency name for the file link
            if currency == "Not specified":
                currency_file_name = "not_specified"
            elif currency == "g GOLD":
                currency_file_name = "gold"
            else:
                currency_file_name = currency.lower()
            
            # Add link to currency page
            currency_link = f"[{currency}](by_currency/{currency_file_name}.md)"
            
            f.write(f"| {currency_link} | {totals['count']} | {totals['value']:.2f} |\n")
        
        # Write organization breakdown section
        f.write("\n## Bounties by Organization\n\n")
        f.write("| Organization | Count | Total Value (ERG) |\n")
        f.write("|--------------|-------|------------------|\n")
        
        for owner, totals in sorted(project_totals.items(), key=lambda x: x[1]["count"], reverse=True):
            if totals["count"] > 0:
                # Add link to organization page
                org_link = f"[{owner}](by_org/{owner.lower()}.md)"
                f.write(f"| {org_link} | {totals['count']} | {totals['value']:.2f} |\n")
        
        f.write("\n## Detailed Bounties\n\n")
        f.write("|Owner|Title & Link|Bounty ERG Equiv|Paid in|Original Value|Claim|\n")
        f.write("|---|---|---|---|---|---|\n")
        
        # Group bounties by owner
        owners = {}
        for bounty in bounty_data:
            owner = bounty["owner"]
            if owner not in owners:
                owners[owner] = []
            owners[owner].append(bounty)
        
        # Add rows for each bounty, grouped by owner
        for owner, owner_bounties in owners.items():
            for bounty in owner_bounties:
                title = bounty["title"]
                url = bounty["url"]
                amount = bounty["amount"]
                currency = bounty["currency"]
                
                # Try to convert to ERG equivalent
                erg_equiv = convert_to_erg(amount, currency, conversion_rates)
                
                # Create a claim link that opens a PR template
                issue_number = bounty["issue_number"]
                creator = bounty["creator"]
                repo_name = bounty["repo"]
                
                claim_url = create_claim_url(owner, repo_name, issue_number, title, url, currency, amount, creator)
                
                f.write(f"| {owner} | [{title}]({url}) | {erg_equiv} | {currency} | {amount} {currency} | [Claim]({claim_url}) |\n")

def generate_summary_file(project_totals, languages, currencies_dict, orgs, conversion_rates, total_bounties, total_value, bounties_dir):
    """
    Generate a summary markdown file for README reference.
    
    Args:
        project_totals (dict): Dictionary of project totals
        languages (dict): Dictionary of languages and their bounties
        currencies_dict (dict): Dictionary of currencies and their bounties
        orgs (dict): Dictionary of organizations and their bounties
        conversion_rates (dict): Dictionary of conversion rates
        total_bounties (int): Total number of bounties
        total_value (float): Total value of bounties
        bounties_dir (str): Bounties directory
    """
    summary_file = f'{bounties_dir}/summary.md'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("## 📋 Open Bounties\n\n")
        f.write(f"**[View Current Open Bounties →](/{bounties_dir}/all.md)**\n\n")
        
        # Add navigation badges
        f.write("## Navigation\n\n")
        f.write(format_navigation_badges(
            total_bounties, 
            len(languages), 
            len(currencies_dict), 
            len(orgs), 
            len(conversion_rates), 
            f"/{bounties_dir}/"
        ))
        f.write("\n\n")
        
        f.write("## Projects\n\n")
        f.write("| Project | Count | Value |\n")
        f.write("|----------|-------|-------|\n")
        
        # Add rows for major projects (those with more than 1 bounty)
        for owner, totals in sorted(project_totals.items(), key=lambda x: x[1]["value"], reverse=True):
            if totals["count"] > 0:
                # Add link to organization page
                org_link = f"[{owner}](/{bounties_dir}/by_org/{owner.lower()}.md)"
                f.write(f"| {org_link} | {totals['count']} | {totals['value']:,.2f} ERG |\n")
        
        # Add overall total
        f.write(f"| **Total** | **{total_bounties}** | **{total_value:,.2f} ERG** |\n\n")
        
        # Calculate totals by currency
        currency_totals = {}
        for currency, currency_bounties in currencies_dict.items():
            currency_totals[currency] = {"count": len(currency_bounties), "value": 0.0}
            
            for bounty in currency_bounties:
                amount = bounty["amount"]
                currency_totals[currency]["value"] += calculate_erg_value(amount, currency, conversion_rates)
        
        # Add currency breakdown
        f.write("## Currencies\n\n")
        f.write("| Currency | Count | Total Value (ERG) |\n")
        f.write("|----------|-------|------------------|\n")
        
        # Write currency rows
        for currency, totals in sorted(currency_totals.items(), key=lambda x: x[1]["count"], reverse=True)[:5]:  # Top 5 currencies
            # Format the currency name for the file link
            if currency == "Not specified":
                currency_file_name = "not_specified"
            elif currency == "g GOLD":
                currency_file_name = "gold"
            else:
                currency_file_name = currency.lower()
            
            # Add link to currency page
            currency_link = f"[{currency}](/{bounties_dir}/by_currency/{currency_file_name}.md)"
            
            f.write(f"| {currency_link} | {totals['count']} | {totals['value']:.2f} |\n")
        
        f.write(f"\n[View all currencies →](/{bounties_dir}/all.md#bounties-by-currency)\n\n")
        
        # Add language breakdown
        f.write("## Languages\n\n")
        f.write("| Language | Count | Percentage |\n")
        f.write("|----------|-------|------------|\n")
        
        # Write language rows
        for lang, lang_bounties in sorted(languages.items(), key=lambda x: len(x[1]), reverse=True)[:5]:  # Top 5 languages
            count = len(lang_bounties)
            percentage = (count / total_bounties) * 100 if total_bounties > 0 else 0
            f.write(f"| [{lang}](/{bounties_dir}/by_language/{lang.lower()}.md) | {count} | {percentage:.1f}% |\n")
        
        f.write(f"\n[View all languages →](/{bounties_dir}/all.md#bounties-by-programming-language)\n\n")
        
        f.write("Open bounties are updated daily with values shown in ERG equivalent. Some bounties may be paid in other tokens as noted in the \"Paid in\" column of the bounty listings.\n")
        
        f.write(f"\n[View current currency prices →](/{bounties_dir}/currency_prices.md)\n")

def update_readme_table(total_bounties, total_value, bounties_dir):
    """
    Update the Featured Bounties table in the README.md file.
    
    Args:
        total_bounties (int): Total number of bounties
        total_value (float): Total value of bounties in ERG
        bounties_dir (str): Bounties directory
    """
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
        # We need to convert 775 SigUSD to ERG
        total_count = total_bounties + 7 + 1  # 7 Fleet SDK + 1 Keystone
        total_erg_value = total_value + 3000  # 3000 ERG for Keystone
        
        # Create the new total row
        new_total_row = f"| *Total* | *{total_count}* | *{total_erg_value:,.2f} ERG* |"
        
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
        
        # Write the updated README.md file
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(updated_readme)
            
        print(f"Updated README.md with new bounty counts and values")
    except Exception as e:
        print(f"Error updating README.md: {e}")

def generate_featured_bounties_file(bounty_data, conversion_rates, total_bounties, total_value, languages, currencies_dict, orgs, bounties_dir):
    """
    Generate a featured bounties markdown file.
    
    Args:
        bounty_data (list): List of bounty data
        conversion_rates (dict): Dictionary of conversion rates
        total_bounties (int): Total number of bounties
        total_value (float): Total value of bounties
        languages (dict): Dictionary of languages and their bounties
        currencies_dict (dict): Dictionary of currencies and their bounties
        orgs (dict): Dictionary of organizations and their bounties
        bounties_dir (str): Bounties directory
    """
    featured_bounties_file = f'{bounties_dir}/featured_bounties.md'
    with open(featured_bounties_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("# Featured Bounties\n\n")
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
            
            if amount != "Not specified":
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
        f.write("## Top Bounties by Value\n\n")
        f.write("| Bounty | Organization | Value | Currency |\n")
        f.write("|--------|--------------|-------|----------|\n")
        
        # Add rows for featured bounties
        for bounty in top_bounties:
            # Format the currency name for the file link
            currency = bounty["currency"]
            if currency == "Not specified":
                currency_file_name = "not_specified"
            elif currency == "g GOLD":
                currency_file_name = "gold"
            else:
                currency_file_name = currency.lower()
            
            # Add links to organization and currency pages
            org_link = f"[{bounty['owner']}](by_org/{bounty['owner'].lower()}.md)"
            currency_link = f"[{currency}](by_currency/{currency_file_name}.md)"
            
            # Calculate ERG equivalent
            erg_equiv = bounty["value"]
            
            f.write(f"| [{bounty['title']}]({bounty['url']}) | {org_link} | {erg_equiv:.2f} ERG | {currency_link} |\n")
        
        f.write("\n## Weekly Summary\n\n")
        f.write("| Date | Open Bounties | Total Value |\n")
        f.write("|------|--------------|-------------|\n")
        f.write(f"| {current_date} | {total_bounties} | {total_value:,.2f} ERG |\n")
