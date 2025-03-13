import requests
import datetime
import re
import json
import os
import sys
import subprocess
from decimal import Decimal

# Get GitHub token from environment variable
github_token = os.environ.get("GITHUB_TOKEN")
if not github_token:
    print("Error: GITHUB_TOKEN environment variable is required")
    sys.exit(1)

# Read repositories from bounties/tracked_repos.json
try:
    with open('bounties/tracked_repos.json', 'r') as f:
        repos_to_query = json.load(f)
except Exception as e:
    print(f"Error reading bounties/tracked_repos.json: {e}")
    sys.exit(1)

# Read organizations from bounties/tracked_orgs.json
try:
    with open('bounties/tracked_orgs.json', 'r') as f:
        orgs_to_query = json.load(f)
except Exception as e:
    print(f"Warning: Error reading bounties/tracked_orgs.json: {e}")
    orgs_to_query = []

# Function to get all repositories for an organization
def get_org_repos(org):
    headers = {"Authorization": f"token {github_token}"}
    url = f"https://api.github.com/orgs/{org}/repos?per_page=100"
    all_repos = []
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching repositories for organization {org}: {response.status_code}")
            return []
            
        repos = response.json()
        all_repos.extend(repos)
        url = response.links.get('next', {}).get('url')
    
    return all_repos

# Add repositories from tracked organizations
for org_entry in orgs_to_query:
    org = org_entry['org']
    print(f"Fetching repositories for organization: {org}")
    
    org_repos = get_org_repos(org)
    for repo in org_repos:
        # Skip archived repositories
        if repo.get('archived', False):
            continue
            
        # Skip forks if they don't have issues
        if repo.get('fork', False) and not repo.get('has_issues', False):
            continue
            
        # Add to repos_to_query if not already there
        repo_entry = {"owner": org, "repo": repo['name']}
        if repo_entry not in repos_to_query:
            print(f"Adding repository from organization: {org}/{repo['name']}")
            repos_to_query.append(repo_entry)

def get_repo_languages(owner, repo):
    headers = {"Authorization": f"token {github_token}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        languages = response.json()
        # Sort languages by bytes of code and get top 2
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:2]
        return [lang[0] for lang in sorted_languages]
    return []

def extract_bounty_from_labels(labels):
    label_patterns = [
        # Cryptocurrency patterns
        r'bounty\s*-?\s*(\d+)\s*(sigusd|rsn|bene|erg|gort)',
        r'b-(\d+)\s*(sigusd|rsn|bene|erg|gort)',
        r'(\d+)\s*(sigusd|rsn|bene|erg|gort)\s*bounty',
        # Precious metals patterns
        r'bounty\s*-?\s*(\d+(?:\.\d+)?)\s*(gram|g|oz|ounce)s?\s+(?:of\s+)?(gold|silver|platinum)',
        r'(\d+(?:\.\d+)?)\s*(gram|g|oz|ounce)s?\s+(?:of\s+)?(gold|silver|platinum)\s*bounty'
    ]
    
    for label in labels:
        label_name = label['name'].lower()
        for pattern in label_patterns:
            match = re.search(pattern, label_name, re.IGNORECASE)
            if match:
                if match.groups()[-1] in ['gold', 'silver', 'platinum']:
                    amount = match.group(1)
                    unit = match.group(2).lower()
                    metal = match.group(3).upper()
                    
                    unit = {
                        'gram': 'g',
                        'g': 'g',
                        'oz': 'oz',
                        'ounce': 'oz'
                    }.get(unit, unit)
                    
                    return amount, f"{unit} {metal}"
                else:
                    amount = match.group(1)
                    currency = match.group(2).upper()
                    if currency == 'SIGUSD':
                        currency = 'SigUSD'
                    return amount, currency
    return None, None

def extract_bounty_from_text(title, body):
    patterns = [
        r'bounty:?\s*[\$€£]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(sigusd|gort|rsn|bene|erg|usd|ergos?|dollars?|€|£|\$)?',
        r'[\$€£]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:sigusd|gort|rsn|bene|erg|usd|ergos?|bounty)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(sigusd|gort|rsn|bene|erg|usd|ergos?)\s*bounty',
        r'bounty:?\s*(\d+(?:\.\d+)?)\s*(gram|g|oz|ounce)s?\s+(?:of\s+)?(gold|silver|platinum)',
        r'(\d+(?:\.\d+)?)\s*(gram|g|oz|ounce)s?\s+(?:of\s+)?(gold|silver|platinum)\s*bounty'
    ]
    
    text = f"{title} {body}".lower()
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) == 3 and match.group(3) in ['gold', 'silver', 'platinum']:
                amount = match.group(1)
                unit = match.group(2).lower()
                metal = match.group(3).upper()
                
                unit = {
                    'gram': 'g',
                    'g': 'g',
                    'oz': 'oz',
                    'ounce': 'oz'
                }.get(unit, unit)
                
                return amount, f"{unit} {metal}"
            else:
                amount = match.group(1).replace(',', '')
                currency = match.group(2) if len(match.groups()) > 1 and match.group(2) else 'USD'
                
                currency = {
                    '$': 'USD',
                    '€': 'EUR',
                    '£': 'GBP',
                    'dollars': 'USD',
                    'erg': 'ERG',
                    'ergos': 'ERG',
                    'sigusd': 'SigUSD',
                    'rsn': 'RSN',
                    'bene': 'BENE',
                    'gort': 'GORT'
                }.get(currency.lower(), currency.upper())
                
                return amount, currency
    
    return None, None

def get_issues(owner, repo, state='open'):
    headers = {"Authorization": f"token {github_token}"}
    url = f'https://api.github.com/repos/{owner}/{repo}/issues?state={state}&per_page=100'
    all_issues = []
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching issues from {owner}/{repo}: {response.status_code}")
            return []
            
        issues = response.json()
        all_issues.extend(issues)
        url = response.links.get('next', {}).get('url')
    
    return all_issues

def check_bounty_labels(labels):
    return any("bounty" in label['name'].lower() or "b-" in label['name'].lower() for label in labels)

# Get conversion rates from Spectrum API
def get_conversion_rates():
    # Default rates to use if we can't find them in the API
    default_rates = {
        "SigUSD": 1.5,
        "GORT": 0.01,
        "RSN": 20.0,
        "gGOLD": 5.0
    }
    
    try:
        response = requests.get("https://api.spectrum.fi/v1/price-tracking/markets")
        if response.status_code != 200:
            print(f"Warning: Error fetching conversion rates: {response.status_code}")
            return default_rates
            
        markets = response.json()
        
        # Print the first few markets to help debug
        print(f"API returned {len(markets)} markets")
        
        # Initialize with default rates
        rates = default_rates.copy()
        
        # Find ERG/SigUSD pairs (where baseSymbol is ERG and quoteSymbol is SigUSD)
        sigusd_markets = [m for m in markets if m.get("quoteSymbol") == "SigUSD" and 
                         m.get("baseSymbol") == "ERG"]
        if sigusd_markets:
            # Sort by volume if available, otherwise use the first market
            if 'baseVolume' in sigusd_markets[0]:
                sigusd_markets.sort(key=lambda m: float(m.get('baseVolume', {}).get('value', 0)), reverse=True)
                print(f"Sorted SigUSD markets by volume, using the most liquid market")
            
            # Use the first (or most liquid) market
            rates["SigUSD"] = float(sigusd_markets[0].get("lastPrice", default_rates["SigUSD"]))
            print(f"Found SigUSD rate: {rates['SigUSD']} from market {sigusd_markets[0].get('baseSymbol')}/{sigusd_markets[0].get('quoteSymbol')}")
        else:
            print(f"No SigUSD markets found, using default: {default_rates['SigUSD']}")
        
        # Find ERG/GORT pairs
        gort_markets = [m for m in markets if m.get("quoteSymbol") == "GORT" and 
                       m.get("baseSymbol") == "ERG"]
        if gort_markets:
            # Use the first market's price
            rates["GORT"] = float(gort_markets[0].get("lastPrice", default_rates["GORT"]))
            print(f"Found GORT rate: {rates['GORT']}")
        else:
            print(f"No GORT markets found, using default: {default_rates['GORT']}")
        
        # Find ERG/RSN pairs
        rsn_markets = [m for m in markets if m.get("quoteSymbol") == "RSN" and 
                      m.get("baseSymbol") == "ERG"]
        if rsn_markets:
            # Use the first market's price
            rates["RSN"] = float(rsn_markets[0].get("lastPrice", default_rates["RSN"]))
            print(f"Found RSN rate: {rates['RSN']}")
        else:
            print(f"No RSN markets found, using default: {default_rates['RSN']}")
        
        # For gGOLD (listed as "GluonW GAU")
        # This is kept for backward compatibility
        gold_markets = [m for m in markets if m.get("quoteSymbol") == "GluonW GAU"]
        if gold_markets:
            rates["gGOLD"] = float(gold_markets[0].get("lastPrice", default_rates["gGOLD"]))
            print(f"Found gGOLD rate: {rates['gGOLD']}")
        else:
            # Try alternative symbols
            alt_gold_markets = [m for m in markets if 
                               (m.get("quoteSymbol") in ["GAU", "GAUC"] or 
                                "GluonW" in m.get("quoteSymbol", ""))]
            if alt_gold_markets:
                rates["gGOLD"] = float(alt_gold_markets[0].get("lastPrice", default_rates["gGOLD"]))
                print(f"Found gGOLD rate (alternative): {rates['gGOLD']}")
            else:
                print(f"No gGOLD markets found, using default: {default_rates['gGOLD']}")
        
        print(f"Using conversion rates: {rates}")
        return rates
    except Exception as e:
        print(f"Warning: Exception fetching conversion rates: {e}")
        print("Using default rates")
        return default_rates

# Define file paths
bounties_dir = 'bounties'
md_file = f'{bounties_dir}/all.md'

# Create bounties directory if it doesn't exist
os.makedirs(bounties_dir, exist_ok=True)

# Initialize data structure to store bounty information
bounty_data = []
project_totals = {}

# Fetch conversion rates
conversion_rates = get_conversion_rates()

# Process each repository
for repo in repos_to_query:
    owner = repo['owner']
    repo_name = repo['repo']
    
    print(f"Processing {owner}/{repo_name}...")
    
    # Get repository languages
    languages = get_repo_languages(owner, repo_name)
    primary_lang = languages[0] if languages else "Unknown"
    secondary_lang = languages[1] if len(languages) > 1 else "None"
    
    # Initialize project counter if not exists
    if owner not in project_totals:
        project_totals[owner] = {"count": 0, "value": 0.0}
    
    # Get issues
    issues = get_issues(owner, repo_name)
    
    # Process each issue
    for issue in issues:
        if issue['state'] == 'open':
            if ("bounty" in issue["title"].lower() or 
                "b-" in issue["title"].lower() or 
                check_bounty_labels(issue["labels"])):
                
                title = issue['title'].replace(",", " ")
                
                # First check labels for bounty amount
                amount, currency = extract_bounty_from_labels(issue["labels"])
                
                # If no bounty found in labels, check title and body
                if not amount:
                    amount, currency = extract_bounty_from_text(title, issue.get('body', ''))
                
                # If still no bounty found, mark as "Not specified"
                if not amount:
                    amount = "Not specified"
                    currency = "Not specified"
                
                # Store the bounty information
                bounty_info = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "owner": owner,
                    "repo": repo_name,
                    "title": title,
                    "url": issue['html_url'],
                    "amount": amount,
                    "currency": currency,
                    "primary_lang": primary_lang,
                    "secondary_lang": secondary_lang,
                    "labels": [label['name'] for label in issue['labels']],
                    "issue_number": issue['number'],
                    "creator": issue['user']['login']  # GitHub username of the issue creator
                }
                
                bounty_data.append(bounty_info)
                
                # Update project totals
                project_totals[owner]["count"] += 1
                
                # Try to convert amount to float for totals
                try:
                    if amount != "Not specified":
                        if currency == "ERG":
                            project_totals[owner]["value"] += float(amount)
                        elif currency == "SigUSD" and "SigUSD" in conversion_rates:
                            project_totals[owner]["value"] += float(amount) * conversion_rates["SigUSD"]
                        elif currency == "GORT" and "GORT" in conversion_rates:
                            project_totals[owner]["value"] += float(amount) * conversion_rates["GORT"]
                        elif currency == "g GOLD" and "gGOLD" in conversion_rates:
                            project_totals[owner]["value"] += float(amount) * conversion_rates["gGOLD"]
                except ValueError:
                    pass

# Calculate overall totals
total_bounties = sum(project["count"] for project in project_totals.values())
total_value = sum(project["value"] for project in project_totals.values())

# Calculate additional statistics
if total_bounties > 0:
    avg_bounty_value = total_value / total_bounties
else:
    avg_bounty_value = 0

# Find highest value bounty
highest_bounty = {"value": 0, "title": "", "url": ""}
for bounty in bounty_data:
    amount = bounty["amount"]
    currency = bounty["currency"]
    
    if amount != "Not specified":
        try:
            # Convert to ERG equivalent
            if currency == "ERG":
                value = float(amount)
            elif currency == "SigUSD" and "SigUSD" in conversion_rates:
                value = float(amount) * conversion_rates["SigUSD"]
            elif currency == "GORT" and "GORT" in conversion_rates:
                value = float(amount) * conversion_rates["GORT"]
            elif currency == "g GOLD" and "gGOLD" in conversion_rates:
                value = float(amount) * conversion_rates["gGOLD"]
            else:
                # For other currencies, use the amount as is
                value = float(amount)
                
            if value > highest_bounty["value"]:
                highest_bounty["value"] = value
                highest_bounty["title"] = bounty["title"]
                highest_bounty["url"] = bounty["url"]
        except ValueError:
            pass

# Count currencies
currencies = set()
for bounty in bounty_data:
    if bounty["currency"] != "Not specified":
        currencies.add(bounty["currency"])

# Group bounties by language
languages = {}
for bounty in bounty_data:
    primary_lang = bounty["primary_lang"]
    if primary_lang not in languages:
        languages[primary_lang] = []
    languages[primary_lang].append(bounty)

# Create a directory for language-specific files if it doesn't exist
lang_dir = f'{bounties_dir}/by_language'
os.makedirs(lang_dir, exist_ok=True)

# Write language-specific Markdown files
for lang, lang_bounties in languages.items():
    lang_file = f'{lang_dir}/{lang.lower()}.md'
    with open(lang_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"# {lang} Bounties\n\n")
        f.write(f"*Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*\n\n")
        f.write(f"Total {lang} bounties: **{len(lang_bounties)}**\n\n")
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
            erg_equiv = amount
            if amount != "Not specified":
                try:
                    if currency == "ERG":
                        erg_equiv = amount
                    elif currency == "SigUSD" and "SigUSD" in conversion_rates:
                        erg_equiv = f"{float(amount) * conversion_rates['SigUSD']:.2f}"
                    elif currency == "GORT" and "GORT" in conversion_rates:
                        erg_equiv = f"{float(amount) * conversion_rates['GORT']:.2f}"
                    elif currency == "g GOLD" and "gGOLD" in conversion_rates:
                        erg_equiv = f"{float(amount) * conversion_rates['gGOLD']:.2f}"
                    else:
                        erg_equiv = amount  # For other currencies, just use the amount
                except ValueError:
                    erg_equiv = amount
            
            # Create a claim link that opens a PR template
            issue_number = bounty["issue_number"]
            creator = bounty["creator"]
            repo_name = bounty["repo"]
            
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
            import urllib.parse
            json_content = json.dumps(template_data, indent=2)
            encoded_json = urllib.parse.quote(json_content)
            
            # Create the claim URL
            claim_url = f"https://github.com/ErgoDevs/Ergo-Bounties/new/main?filename=submissions/{owner.lower()}-{repo_name.lower()}-{issue_number}.json&value={encoded_json}&message=Claim%20Bounty%20{owner}/{repo_name}%23{issue_number}&description=I%20want%20to%20claim%20this%20bounty%20posted%20by%20{creator}.%0A%0ABounty:%20{urllib.parse.quote(title)}"
            
            f.write(f"| {owner} | [{title}]({url}) | {erg_equiv} | {currency} | {secondary_lang} | [Claim]({claim_url}) |\n")

# Write main Markdown file
with open(md_file, 'w', encoding='utf-8') as f:
    # Write header
    f.write("# Open Bounties\n\n")
    f.write(f"*Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*\n\n")
    
    # Write summary section
    f.write("## Summary\n\n")
    f.write("| Project | Count | ERG Equivalent |\n")
    f.write("|---------|-------|---------------|\n")
    
    for owner, totals in sorted(project_totals.items(), key=lambda x: x[1]["count"], reverse=True):
        if totals["count"] > 0:
            f.write(f"| {owner} | {totals['count']} | {totals['value']:.2f} |\n")
    
    f.write(f"| **Overall Total** | **{total_bounties}** | **{total_value:.2f}** |\n\n")
    
    # Write language breakdown section
    f.write("## Bounties by Programming Language\n\n")
    f.write("| Language | Count | Percentage |\n")
    f.write("|----------|-------|------------|\n")
    
    for lang, lang_bounties in sorted(languages.items(), key=lambda x: len(x[1]), reverse=True):
        count = len(lang_bounties)
        percentage = (count / total_bounties) * 100
        f.write(f"| [{lang}](by_language/{lang.lower()}.md) | {count} | {percentage:.1f}% |\n")
    
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
    global_count = 1
    for owner, owner_bounties in owners.items():
        owner_count = 1
        for bounty in owner_bounties:
            title = bounty["title"]
            url = bounty["url"]
            amount = bounty["amount"]
            currency = bounty["currency"]
            
            # Try to convert to ERG equivalent
            erg_equiv = amount
            if amount != "Not specified":
                try:
                    if currency == "ERG":
                        erg_equiv = amount
                    elif currency == "SigUSD" and "SigUSD" in conversion_rates:
                        erg_equiv = f"{float(amount) * conversion_rates['SigUSD']:.2f}"
                    elif currency == "GORT" and "GORT" in conversion_rates:
                        erg_equiv = f"{float(amount) * conversion_rates['GORT']:.2f}"
                    elif currency == "g GOLD" and "gGOLD" in conversion_rates:
                        erg_equiv = f"{float(amount) * conversion_rates['gGOLD']:.2f}"
                    else:
                        erg_equiv = amount  # For other currencies, just use the amount
                except ValueError:
                    erg_equiv = amount
            
            # Create a claim link that opens a PR template
            issue_number = bounty["issue_number"]
            creator = bounty["creator"]
            repo_name = bounty["repo"]
            
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
            import urllib.parse
            json_content = json.dumps(template_data, indent=2)
            encoded_json = urllib.parse.quote(json_content)
            
            # Create the claim URL
            claim_url = f"https://github.com/ErgoDevs/Ergo-Bounties/new/main?filename=submissions/{owner.lower()}-{repo_name.lower()}-{issue_number}.json&value={encoded_json}&message=Claim%20Bounty%20{owner}/{repo_name}%23{issue_number}&description=I%20want%20to%20claim%20this%20bounty%20posted%20by%20{creator}.%0A%0ABounty:%20{urllib.parse.quote(title)}"
            
            f.write(f"| {owner} | [{title}]({url}) | {erg_equiv} | {currency} | {amount} {currency} | [Claim]({claim_url}) |\n")
            owner_count += 1
            global_count += 1
    
    # Write repository and organization information
    f.write("\n## Tracked Repositories and Organizations\n")
    
    # List individual repositories
    f.write("\n### Individually Tracked Repositories\n")
    f.write("|Owner|Repo|\n")
    f.write("|---|---|\n")
    
    for repo in repos_to_query:
        # Skip repos that were added from tracked organizations
        if any(org_entry['org'] == repo['owner'] for org_entry in orgs_to_query):
            continue
        f.write(f"|{repo['owner']}|{repo['repo']}|\n")
    
    # List tracked organizations
    if orgs_to_query:
        f.write("\n### Tracked Organizations\n")
        f.write("|Organization|Description|\n")
        f.write("|---|---|\n")
        
        for org_entry in orgs_to_query:
            org = org_entry['org']
            f.write(f"|{org}|All repositories in this organization are automatically tracked|\n")

# Write a summary file for README reference
summary_file = f'{bounties_dir}/summary.md'
with open(summary_file, 'w', encoding='utf-8') as f:
    f.write("## 📋 Open Bounties\n\n")
    f.write(f"**[View Current Open Bounties →](/{bounties_dir}/all.md)**\n\n")
    f.write("| Project | Count | Value |\n")
    f.write("|----------|-------|-------|\n")
    
    # Add rows for major projects (those with more than 1 bounty)
    for owner, totals in sorted(project_totals.items(), key=lambda x: x[1]["value"], reverse=True):
        if totals["count"] > 0:
            f.write(f"| {owner} | {totals['count']} | {totals['value']:,.2f} ERG |\n")
    
    # Add overall total
    f.write(f"| **Total** | **{total_bounties}** | **{total_value:,.2f} ERG** |\n\n")
    
    f.write("Open bounties are updated daily with values shown in ERG equivalent. Some bounties may be paid in other tokens as noted in the \"Paid in\" column of the bounty listings.\n")

# Create a featured bounties table for the README
featured_bounties_file = f'{bounties_dir}/featured_bounties.md'
with open(featured_bounties_file, 'w', encoding='utf-8') as f:
    # Get current date for the week row
    current_date = datetime.datetime.now().strftime("%b %d, %Y")
    
    # Find top 2 highest value bounties to feature
    top_bounties = []
    for bounty in bounty_data:
        amount = bounty["amount"]
        currency = bounty["currency"]
        title = bounty["title"]
        
        if amount != "Not specified":
            try:
                # Convert to ERG equivalent
                if currency == "ERG":
                    value = float(amount)
                elif currency == "SigUSD" and "SigUSD" in conversion_rates:
                    value = float(amount) * conversion_rates["SigUSD"]
                elif currency == "GORT" and "GORT" in conversion_rates:
                    value = float(amount) * conversion_rates["GORT"]
                elif currency == "g GOLD" and "gGOLD" in conversion_rates:
                    value = float(amount) * conversion_rates["gGOLD"]
                else:
                    # For other currencies, use the amount as is
                    value = float(amount)
                    
                top_bounties.append({
                    "title": title,
                    "value": value,
                    "amount": amount,
                    "currency": currency,
                    "last_update": "Last Update"  # Placeholder, could be replaced with actual date if available
                })
            except ValueError:
                pass
    
    # Sort by value and get top 2
    top_bounties.sort(key=lambda x: x["value"], reverse=True)
    top_bounties = top_bounties[:2]
    
    # Write the featured bounties table
    f.write("| Week | Count of Open Issues | ERG Bounties |\n")
    f.write("|------|---------------------|-------------|\n")
    
    # Add rows for featured bounties
    for bounty in top_bounties:
        f.write(f"| {bounty['title']} | {bounty['last_update']} | {bounty['amount']} {bounty['currency']} |\n")
    
    # Add row for current week with total counts
    f.write(f"| {current_date} | {total_bounties} | {total_value:,.2f} ERG |\n")
    
    # Add total row
    f.write(f"| **Total** | **{total_bounties}** | **{total_value:,.2f} ERG** |\n")

print(f"Main bounty file written to: {md_file}")
print(f"Summary file written to: {summary_file}")
print(f"Language-specific files written to: {lang_dir}/")
print(f"Total bounties found: {total_bounties}")
print(f"Total ERG equivalent value: {total_value:.2f}")
