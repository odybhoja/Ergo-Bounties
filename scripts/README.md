# Ergo Bounties Scripts

This directory contains the scripts used to collect, process, and validate bounties for the Ergo ecosystem.

## Directory Structure

```
scripts/
├── bounty_finder.py        # Main script for finding and processing bounties
├── bounty_modules/         # Core modules for bounty processing
│   ├── config.py           # Configuration handling
│   ├── conversion_rates.py # Currency conversion utilities
│   ├── processors.py       # Bounty data processing
│   ├── utils.py            # Utility functions
│   └── generators/         # Markdown file generators
│       ├── language_generator.py
│       ├── organization_generator.py
│       ├── currency_generator.py
│       ├── summary_generator.py
│       └── ...
├── tests/                  # Test scripts
│   ├── test.py             # Legacy test script
│   └── run_bounty_check.py # New validation tool with better output
└── .env                    # Environment variables (locally only, not committed)
```

## Setup

1. Clone the repository
2. Create a `.env` file in the `scripts/` directory with your GitHub token:
   ```
   github_token=your_github_token
   ```
3. Install required dependencies:
   ```bash
   pip install requests colorama tabulate
   ```

## Usage

### Finding and Processing Bounties

To run the bounty finder script which collects and processes bounties from tracked GitHub repositories:

```bash
python scripts/bounty_finder.py
```

This will:
- Fetch current conversion rates for various currencies
- Process all tracked repositories and organizations
- Generate markdown files in the `bounties/` directory
- Update the main README with bounty statistics

### Validating Bounties

To validate the bounty data and get a summary report:

```bash
./test.sh
```

or directly:

```bash
python scripts/tests/run_bounty_check.py
```

This will:
- Validate your GitHub token
- Run the bounty finder
- Count and verify generated files
- Show statistics about found bounties
- Track changes since the previous run

## GitHub Actions Integration

The scripts are integrated into GitHub Actions workflows (see `.github/workflows/update-bounties.yml`), which automatically:

1. Run the bounty finder script every 12 hours
2. Commit any changes to the repository
3. Run the validation script to verify the results

## Improved Code Organization

The Python scripts have been moved from `.github/workflows/` to the dedicated `scripts/` directory. This follows best practices by:

1. Keeping workflow YAML files separate from executable scripts
2. Maintaining better organization of related code
3. Making testing and local development easier
4. Providing cleaner separation of concerns

## Import Structure

The scripts support two import patterns to work in both direct execution and module contexts:

```python
# When running scripts directly
from bounty_modules.some_module import SomeClass

# When imported as a module (e.g. in GitHub Actions)
from scripts.bounty_modules.some_module import SomeClass
```

This dual import pattern ensures the code works properly in all environments.
