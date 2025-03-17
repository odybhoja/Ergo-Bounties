# 🤖 Ergo Bounties: How It Works

This document explains the technical details of how the Ergo Ecosystem Bounties repository automatically tracks, updates, and displays bounties across the Ergo blockchain ecosystem.

## Automated Bounty Tracking System

The repository uses GitHub Actions to automatically track and update the list of open bounties from various projects in the Ergo ecosystem.

### Automation Schedule

- **Daily Updates**: The bounty list is refreshed every day at midnight UTC
- **On-Demand Updates**: Triggered whenever `tracked_repos.json` is modified
- **Manual Trigger**: Maintainers can manually run the workflow when needed

### How It Works

The automation process follows these steps:

1. **Repository Scanning**: The system scans all repositories listed in `tracked_repos.json`
2. **Issue Identification**: It identifies issues with bounty tags or mentions in their title or description
3. **Bounty Extraction**: The system extracts bounty amounts and currencies using pattern matching
4. **Value Calculation**: Where possible, it converts different currencies to ERG equivalent values
5. **Report Generation**: It generates updated bounty reports in various formats and categories
6. **Automatic Commit**: Changes are committed back to the repository

## Adding Repositories to Tracking

To add a new repository to the tracking system:

1. Fork this repository
2. Edit the `tracked_repos.json` file to add the new repository
   ```json
   {"owner": "repo-owner", "repo": "repo-name"}
   ```
3. Submit a PR with title: `[ADD REPO] owner/repo-name`

Once merged, the automation will include the new repository's bounties in the next update.

## Adding Manual Bounties

For bounties that aren't in GitHub repositories or don't follow standard formats:

1. Fork this repository
2. Edit the `extra_bounties.json` file to add the new bounty:
   ```json
   {
     "timestamp": "YYYY-MM-DD HH:MM:SS",
     "owner": "organization-name",
     "repo": "project-name",
     "title": "Bounty Title",
     "url": "https://link-to-bounty-details",
     "amount": "100",
     "currency": "ERG",
     "primary_lang": "Language",
     "secondary_lang": "None",
     "labels": ["bounty", "manual-entry"],
     "issue_number": "ext-123",
     "creator": "your-username"
   }
   ```
3. Submit a PR with title: `[ADD MANUAL BOUNTY] Bounty Title`

The system will automatically include these manual bounties alongside GitHub-sourced bounties in all listings.

## Bounty Detection Logic

The system identifies bounties using several methods:

### Label-Based Detection

Issues with labels containing "bounty" or "b-" are automatically included. The system also extracts bounty amounts from labels with patterns like:
- `bounty-100-erg`
- `b-500-sigusd`
- `100-erg-bounty`

### Content-Based Detection

If no bounty information is found in labels, the system searches the issue title and body for patterns like:
- `bounty: 100 ERG`
- `$500 bounty`
- `200 SigUSD bounty`

### Currency Support

The system recognizes multiple currencies:
- ERG (Ergo's native token)
- SigUSD (Ergo's stablecoin)
- RSN (Rosen Bridge token)
- BENE (Benefaction token)
- GORT (Governance token)
- Precious metals (g GOLD, etc.)

## Technical Implementation

The bounty tracking is implemented in Python using the GitHub API. The main components are:

- **GitHub Actions Workflow**: Defined in `.github/workflows/update-bounties.yml`
- **Python Script**: Located at `scrape/bounty_finder_github_action.py`
- **Repository List**: Maintained in `tracked_repos.json`

### GitHub API Usage

The script uses the GitHub API to:
- Fetch repository language information
- Retrieve open issues from tracked repositories
- Extract issue details including labels, title, and body

### Output Files

The system generates:
- A Markdown file (`bounty_issues.md`) with a formatted table of all bounties
- A CSV file (`scrape/bounty_issues_TIMESTAMP.csv`) with detailed bounty data
- Language-specific Markdown files in the `bounties/by_language/` directory
- Currency-specific Markdown files in the `bounties/by_currency/` directory
- Organization-specific Markdown files in the `bounties/by_org/` directory
- Summary statistics including total counts and values

## For Developers

This section provides information for developers who want to contribute to the Ergo Bounties codebase.

### Code Organization

The repository code is structured as follows:

```
.
├── src/                  # Source code
│   ├── api/              # API clients (GitHub, Currency)
│   ├── config/           # Configuration files
│   │   ├── constants.json    # Application constants
│   │   ├── extra_bounties.json    # Manually added bounties
│   │   ├── tracked_orgs.json      # Organizations to track
│   │   └── tracked_repos.json     # Repositories to track
│   ├── core/             # Core application logic
│   ├── generators/       # Markdown file generators
│   ├── tests/            # Test scripts
│   │   ├── github_actions_check.py  # CI/CD validation
│   │   ├── run_bounty_check.py      # Data validation
│   │   └── test_runner.py           # Test framework
│   ├── utils/            # Utility functions
│   └── bounty_finder.py  # Main application entry point
├── data/                 # Generated data files
│   ├── by_currency/      # Bounties grouped by currency
│   ├── by_language/      # Bounties grouped by programming language
│   ├── by_org/           # Bounties grouped by organization
│   └── *.md              # Summary and index files
├── docs/                 # Documentation
├── submissions/          # Bounty submissions from users
└── test.sh               # Test runner script
```

### Key Components for Developers

#### 1. README Generator (`readme_updater.py`)

This module is responsible for updating the main README.md. Its key features include:

- Loading configurations from `config.json` and `constants.json`
- Generating language badges based on current bounty counts
- Calculating statistics (high-value bounties, beginner-friendly counts)
- Formatting dynamic sections based on current data
- Robust error handling with fallbacks

#### 2. Configuration System

Two main configuration files control the system behavior:

##### `constants.json`
Contains project-wide constants like:
```json
{
  "language_colors": { "Scala": "DC322F", "Rust": "DEA584" },
  "fixed_bounties": {
    "fleet_sdk": { "count": 7, "currency": "SigUSD", "amount": 775 },
    "keystone": { "count": 1, "currency": "ERG", "amount": 3000 }
  }
}
```

##### `config.json`
Controls the README generator specifically:
```json
{
  "readme": {
    "section_order": ["header", "stats_badges", "get_started"],
    "display_beginner_friendly": true,
    "high_value_threshold_erg": 1000
  },
  "badges": {
    "colors": { "open_bounties": "4CAF50", "total_value": "2196F3" }
  }
}
```

### Development Best Practices

When modifying the codebase, follow these guidelines:

1. **Error Handling**: Always include robust error handling with fallbacks for missing data
2. **Configuration-Driven**: Make features configurable rather than hardcoded
3. **Type Annotations**: Use proper Python type hints for better maintainability
4. **Modular Design**: Keep functions focused and modular for easier testing
5. **Backward Compatibility**: Ensure changes don't break existing functionality

### Testing Changes

To test changes to the scripts:

1. Run the scripts locally with appropriate test data
2. Check that generated files match expected formats
3. Verify error handling by deliberately introducing bad input
4. Test with various configurations to ensure flexibility
5. Run the test.py script to validate full system functionality

## Limitations and Edge Cases

- **Currency Conversion**: The system uses approximate conversion rates for non-ERG currencies
- **Manual Bounties**: Some bounties may not follow standard formats and require manual addition
- **API Rate Limits**: The GitHub API has rate limits that may affect large scans
- **Pattern Matching**: Complex or unusual bounty descriptions may not be correctly parsed

## Future Improvements

Planned enhancements to the system include:
- More accurate currency conversion rates
- Better categorization of bounties by type or difficulty
- Enhanced statistics and visualizations
- Integration with other Ergo ecosystem tools

## Donations

The Ergo ecosystem bounty program is supported by donations. Your contributions help:

- Fund Ergo core development
- Improve ecosystem tooling
- Promote Ergo technology among developers
- Increase bounty rewards

For donation wallet addresses and more information, please see the [donation page](/docs/donate.md).

All donations are used to support the Ergo ecosystem bounty program and help grow the Ergo blockchain ecosystem.
