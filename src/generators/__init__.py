"""
Generators Package

This package contains modules for generating various markdown output files:
- Language-specific files
- Organization-specific files
- Currency-specific files
- Summary files
- Featured bounties
- High-value bounties
- Price tables

Each generator function follows a similar pattern: it takes input data,
processes it, formats markdown content, and writes output files.
"""

# Import all generator functions for easier access
from .main import (
    generate_language_files,
    generate_organization_files,
    generate_currency_files,
    generate_price_table,
    generate_main_file,
    generate_summary_file,
    generate_featured_bounties_file,
    update_ongoing_programs_table,
    generate_high_value_bounties_file,
    update_readme_badges
)
