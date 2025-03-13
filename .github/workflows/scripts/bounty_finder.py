#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime

# Import modules
from bounty_modules.api_client import get_org_repos, get_repo_languages, get_issues
from bounty_modules.extractors import check_bounty_labels, extract_bounty_from_labels, extract_bounty_from_text
from bounty_modules.conversion_rates import get_conversion_rates, convert_to_erg
from bounty_modules.utils import ensure_directory, calculate_erg_value
from bounty_modules.generators import (
    generate_language_files,
    generate_organization_files,
    generate_currency_files,
    generate_price_table,
    generate_main_file,
    generate_summary_file,
    generate_featured_bounties_file,
    update_readme_table
)

def main():
    # Get GitHub token from environment variable
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable is required")
        sys.exit(1)

    # Define file paths
    bounties_dir = 'bounties'
    ensure_directory(bounties_dir)

    # Read repositories from bounties/tracked_repos.json
    try:
        with open(f'{bounties_dir}/tracked_repos.json', 'r') as f:
            repos_to_query = json.load(f)
    except Exception as e:
        print(f"Error reading bounties/tracked_repos.json: {e}")
        sys.exit(1)

    # Read organizations from bounties/tracked_orgs.json
    try:
        with open(f'{bounties_dir}/tracked_orgs.json', 'r') as f:
            orgs_to_query = json.load(f)
    except Exception as e:
        print(f"Warning: Error reading bounties/tracked_orgs.json: {e}")
        orgs_to_query = []

    # Add repositories from tracked organizations
    for org_entry in orgs_to_query:
        org = org_entry['org']
        print(f"Fetching repositories for organization: {org}")
        
        org_repos = get_org_repos(org, github_token)
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
        languages = get_repo_languages(owner, repo_name, github_token)
        primary_lang = languages[0] if languages else "Unknown"
        secondary_lang = languages[1] if len(languages) > 1 else "None"
        
        # Initialize project counter if not exists
        if owner not in project_totals:
            project_totals[owner] = {"count": 0, "value": 0.0}
        
        # Get issues
        issues = get_issues(owner, repo_name, github_token)
        
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
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
                    project_totals[owner]["value"] += calculate_erg_value(amount, currency, conversion_rates)

    # Calculate overall totals
    total_bounties = sum(project["count"] for project in project_totals.values())
    total_value = sum(project["value"] for project in project_totals.values())

    # Group bounties by language
    languages = {}
    for bounty in bounty_data:
        primary_lang = bounty["primary_lang"]
        if primary_lang not in languages:
            languages[primary_lang] = []
        languages[primary_lang].append(bounty)

    # Group bounties by organization
    orgs = {}
    for bounty in bounty_data:
        owner = bounty["owner"]
        if owner not in orgs:
            orgs[owner] = []
        orgs[owner].append(bounty)

    # Group bounties by currency
    currencies_dict = {}
    for bounty in bounty_data:
        currency = bounty["currency"]
        if currency not in currencies_dict:
            currencies_dict[currency] = []
        currencies_dict[currency].append(bounty)

    # Generate language-specific files
    generate_language_files(
        bounty_data, 
        languages, 
        conversion_rates, 
        total_bounties, 
        len(currencies_dict), 
        len(orgs), 
        bounties_dir
    )

    # Generate organization-specific files
    generate_organization_files(
        bounty_data, 
        orgs, 
        conversion_rates, 
        total_bounties, 
        languages, 
        len(currencies_dict), 
        bounties_dir
    )

    # Generate currency-specific files
    generate_currency_files(
        bounty_data, 
        currencies_dict, 
        conversion_rates, 
        total_bounties, 
        languages, 
        orgs, 
        bounties_dir
    )

    # Generate currency price table
    generate_price_table(
        conversion_rates, 
        total_bounties, 
        languages, 
        currencies_dict, 
        orgs, 
        bounties_dir
    )

    # Generate main file
    generate_main_file(
        bounty_data, 
        project_totals, 
        languages, 
        currencies_dict, 
        orgs, 
        conversion_rates, 
        total_bounties, 
        total_value, 
        bounties_dir
    )

    # Generate summary file
    generate_summary_file(
        project_totals, 
        languages, 
        currencies_dict, 
        orgs, 
        conversion_rates, 
        total_bounties, 
        total_value, 
        bounties_dir
    )

    # Generate featured bounties file
    generate_featured_bounties_file(
        bounty_data, 
        conversion_rates, 
        total_bounties, 
        total_value,
        languages, 
        currencies_dict, 
        orgs, 
        bounties_dir
    )
    
    # Update the README.md table with the latest bounty counts and values
    update_readme_table(
        total_bounties,
        total_value,
        bounties_dir
    )

    # Print summary
    print(f"Main bounty file written to: {bounties_dir}/all.md")
    print(f"Summary file written to: {bounties_dir}/summary.md")
    print(f"Language-specific files written to: {bounties_dir}/by_language/")
    print(f"Organization-specific files written to: {bounties_dir}/by_org/")
    print(f"Currency-specific files written to: {bounties_dir}/by_currency/")
    print(f"Currency price table written to: {bounties_dir}/currency_prices.md")
    print(f"Featured bounties file written to: {bounties_dir}/featured_bounties.md")
    print(f"README.md table updated with latest bounty counts and values")
    print(f"Total bounties found: {total_bounties}")
    print(f"Total ERG equivalent value: {total_value:.2f}")

if __name__ == "__main__":
    main()
