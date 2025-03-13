# Bounty Finder

This script finds and processes bounties from GitHub repositories and organizations, generating various markdown files with bounty information.

## Code Structure

The code has been modularized for better maintainability:

- `bounty_finder.py`: Main script that orchestrates the process
- `run_bounty_finder.py`: Wrapper script to run the bounty finder
- `bounty_modules/`: Directory containing the modules
  - `api_client.py`: Functions for GitHub API interactions
  - `extractors.py`: Functions for extracting bounty information from issues
  - `conversion_rates.py`: Functions for fetching and handling currency conversion rates
  - `generators.py`: Functions for generating the various markdown files
  - `utils.py`: Utility functions used across the codebase

## Generated Files

The script generates the following files:

- `bounties/all.md`: Main file with summary and detailed bounties
- `bounties/summary.md`: Summary file for README reference
- `bounties/featured_bounties.md`: Featured bounties for README
- `bounties/currency_prices.md`: Table of currency prices
- `bounties/by_language/`: Directory with language-specific files
- `bounties/by_org/`: Directory with organization-specific files
- `bounties/by_currency/`: Directory with currency-specific files

## Running the Script

To run the script:

```bash
cd .github/workflows
python scripts/run_bounty_finder.py
```

The script requires a GitHub token to be set as an environment variable:

```bash
export GITHUB_TOKEN=your_github_token
```

## Configuration

The script reads configuration from:

- `bounties/tracked_repos.json`: List of repositories to track
- `bounties/tracked_orgs.json`: List of organizations to track
