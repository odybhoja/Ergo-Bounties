# ⚙️ How Ergo Ecosystem Bounties Works

This document explains the technical details of how the Ergo Ecosystem Bounties repository automatically tracks and updates bounties across the Ergo blockchain ecosystem.

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
5. **Report Generation**: It generates updated `bounty_issues.md` and CSV reports
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
- Summary statistics including total counts and values

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

## For Developers

If you want to contribute to improving the bounty tracking system:

1. Review the Python script to understand the current implementation
2. Test changes locally before submitting PRs
3. Ensure backward compatibility with existing data formats
4. Consider edge cases in bounty descriptions and formats

For questions or suggestions about the bounty tracking system, please open an issue in the repository.
