#!/usr/bin/env python3
"""
Ergo Bounties Test Runner

This script provides a simpler way to test the bounty finder functionality.
It runs the bounty finder and performs basic validation checks on the output.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add the parent directory to sys.path so we can import modules correctly
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.core.config import BountyConfig
from scripts.api.currency_client import CurrencyClient
from scripts.core.processor import BountyProcessor
from scripts.utils.common import ensure_directory
from scripts.generators.main import (
    generate_language_files,
    generate_organization_files,
    generate_currency_files,
    generate_price_table,
    generate_main_file,
    generate_summary_file,
    generate_featured_bounties_file,
    update_readme_badges,
    update_ongoing_programs_table,
    generate_high_value_bounties_file
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_runner')

def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description='Test the bounty finder functionality')
    parser.add_argument('--validate-only', action='store_true', help='Only validate output files without running full bounty finder')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting test runner")
    
    # Initialize configuration
    bounties_dir = 'bounties'
    config = BountyConfig(bounties_dir)
    
    # Check if configuration is valid
    if not config.is_valid():
        logger.error("Invalid configuration: Missing GitHub token or tracked repositories")
        sys.exit(1)
    
    # Validate existing output files if requested
    if args.validate_only:
        validate_output_files(bounties_dir)
        return
    
    # Run a minimal bounty finder for testing
    run_minimal_bounty_finder(config, bounties_dir)
    
    logger.info("Test completed successfully")

def validate_output_files(bounties_dir: str):
    """
    Validate that expected output files exist and have content.
    
    Args:
        bounties_dir: Bounties directory
    """
    logger.info("Validating output files")
    
    # List of key files to check
    key_files = [
        'all.md',
        'summary.md',
        'featured_bounties.md',
        'currency_prices.md',
        'high-value-bounties.md'
    ]
    
    success = True
    
    # Check main files
    for file in key_files:
        file_path = os.path.join(bounties_dir, file)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            logger.info(f"✓ Found {file}")
        else:
            logger.error(f"✗ Missing or empty: {file}")
            success = False
    
    # Check subdirectories
    subdirs = ['by_language', 'by_currency', 'by_org']
    for subdir in subdirs:
        dir_path = os.path.join(bounties_dir, subdir)
        if os.path.isdir(dir_path):
            files = os.listdir(dir_path)
            if files:
                logger.info(f"✓ Found {len(files)} files in {subdir}/")
            else:
                logger.warning(f"! No files in {subdir}/")
                success = False
        else:
            logger.error(f"✗ Missing directory: {subdir}/")
            success = False
    
    if success:
        logger.info("All required output files validated successfully")
    else:
        logger.error("Some output files are missing or empty")
        sys.exit(1)

def run_minimal_bounty_finder(config: BountyConfig, bounties_dir: str):
    """
    Run a minimal version of the bounty finder for testing.
    
    Args:
        config: Bounty configuration
        bounties_dir: Bounties directory
    """
    logger.info("Running minimal bounty finder for testing")
    
    # Ensure bounties directory exists
    ensure_directory(bounties_dir)
    
    # Load repositories and organizations
    repos_to_query = config.load_tracked_repos()
    orgs_to_query = config.load_tracked_orgs()
    
    # Use all repositories for full testing (not just the first one)
    if repos_to_query:
        logger.info(f"Testing with {len(repos_to_query)} repositories")
    else:
        logger.warning("No repositories configured for testing")
    
    # Fetch conversion rates
    logger.info("Fetching conversion rates")
    currency_client = CurrencyClient()
    conversion_rates = currency_client.get_all_rates()
    
    # Initialize processor
    processor = BountyProcessor(config.github_token, conversion_rates)
    
    # Process repositories
    if repos_to_query:
        logger.info(f"Processing {len(repos_to_query)} repositories")
        processor.process_repositories(repos_to_query)
    
    # Load and add all extra bounties
    extra_bounties = config.load_extra_bounties()
    if extra_bounties:
        # Use all extra bounties
        logger.info(f"Adding {len(extra_bounties)} extra bounties")
        processor.add_extra_bounties(extra_bounties)
    
    # Get processed data
    bounty_data = processor.get_bounty_data()
    project_totals = processor.get_project_totals()
    total_bounties, total_value = processor.get_total_stats()
    
    # Group data for file generation
    languages = processor.group_by_language()
    orgs = processor.group_by_organization()
    currencies_dict = processor.group_by_currency()
    
    # Generate output files
    logger.info("Generating output files")
    
    # Ensure bounties directory and subdirectories exist
    config.ensure_directories()
    
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
    
    # Update ongoing programs table
    update_ongoing_programs_table(
        bounty_data,
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
    
    # Generate high-value bounties file
    high_value_bounties = processor.find_high_value_bounties(threshold=1000)
    generate_high_value_bounties_file(
        bounty_data,
        conversion_rates,
        total_bounties,
        total_value,
        languages,
        currencies_dict,
        orgs,
        bounties_dir,
        high_value_threshold=1000
    )
    
    # Update README badges
    logger.info("Updating README badges")
    update_readme_badges(
        total_bounties,
        total_value,
        len(high_value_bounties)
    )
    
    # Verify files were actually generated with current timestamps
    logger.info("Verifying file generation with current timestamps...")
    main_files = ['all.md', 'summary.md', 'featured_bounties.md', 'currency_prices.md', 'high-value-bounties.md']
    
    import time
    current_time = time.time()
    
    for file in main_files:
        file_path = os.path.join(bounties_dir, file)
        if os.path.exists(file_path):
            file_timestamp = os.path.getmtime(file_path)
            time_diff = current_time - file_timestamp
            logger.info(f"File {file} timestamp: {file_timestamp}, age: {time_diff:.2f} seconds ago")
            if time_diff < 5:  # File modified in the last 5 seconds
                logger.info(f"✅ File {file} was just generated/updated")
            else:
                logger.warning(f"⚠️ File {file} might be stale (last modified {time_diff:.2f} seconds ago)")
        else:
            logger.error(f"❌ File {file} does not exist!")
    
    # Print summary
    logger.info(f"Found {total_bounties} bounties in test run")
    logger.info(f"Total ERG equivalent value: {total_value:.2f}")
    
    # More detailed output in verbose mode
    if logger.level == logging.DEBUG and bounty_data:
        logger.debug("First bounty details:")
        for key, value in bounty_data[0].items():
            logger.debug(f"  {key}: {value}")

if __name__ == "__main__":
    main()
