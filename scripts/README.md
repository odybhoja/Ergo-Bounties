# Ergo Bounties Scripts

This directory contains the scripts and modules used to collect, process, and validate bounties for the Ergo ecosystem.

## Directory Structure

The codebase is organized into a logical package structure:

```
scripts/
├── __init__.py             # Main package initialization
├── api/                    # API clients
│   ├── __init__.py
│   ├── github_client.py    # GitHub API client
│   └── currency_client.py  # Currency rates client
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── processor.py        # Bounty data processing
│   └── extractors.py       # Bounty info extraction
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── common.py           # Common utility functions
│   └── markdown.py         # Markdown generation utilities
├── generators/             # File generators
│   ├── __init__.py
│   └── main.py             # All generator functions
├── tests/                  # Test scripts
│   ├── __init__.py
│   ├── test_runner.py      # Simple test runner
│   └── run_bounty_check.py # Validation tool with detailed output
├── bounty_finder.py        # Main entry point script
└── constants.json          # Application constants
```

## Setup

1. Clone the repository
2. Install required dependencies:
   ```bash
   pip install requests colorama tabulate pathlib
   ```
3. Set the GITHUB_TOKEN environment variable:
   ```bash
   export GITHUB_TOKEN=your_github_token
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
- Update the README with bounty statistics

### Testing and Validation

For quick testing, you can run:

```bash
python scripts/tests/test_runner.py
```

For comprehensive validation with detailed reports:

```bash
python scripts/tests/run_bounty_check.py
```

This will:
- Validate your GitHub token
- Count and verify generated files
- Show statistics about found bounties
- Track changes since the previous run

## GitHub Actions Integration

The scripts are integrated into GitHub Actions workflows (see `.github/workflows/update-bounties.yml`), which automatically:

1. Run the bounty finder script every 12 hours
2. Commit any changes to the repository
3. Run the validation script to verify the results

## Code Organization

The code has been refactored to follow these principles:

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Dependency Injection**: Components receive their dependencies (like GitHub client, etc.)
3. **Clear Documentation**: Every module, class, and function is documented
4. **Consistent Error Handling**: Structured approach to handling and reporting errors
5. **Type Annotations**: All functions use type hints for better IDE support and maintainability
6. **Testability**: Code is structured to be easily testable

## Module Responsibilities

- **api/**: Contains API clients for external services
- **core/**: Contains the core application logic
- **utils/**: Contains utility functions used throughout the application
- **generators/**: Contains code for generating output files
- **tests/**: Contains testing utilities and validation tools
