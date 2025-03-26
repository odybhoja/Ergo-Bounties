"""
Unit tests for the main generator functions.
"""

import pytest
from unittest.mock import patch, mock_open, MagicMock
import os

# Assuming generator functions are importable like this
# Adjust the import path if necessary based on your project structure
from src.generators.main import (
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

# --- Mock Data ---

@pytest.fixture
def mock_bounty_data():
    """Provides sample bounty data."""
    return [
        {
            "timestamp": "2025-03-26 10:00:00", "owner": "org1", "repo": "repo1",
            "title": "Test Bounty 1", "url": "http://example.com/1", "amount": "100",
            "currency": "SigUSD", "primary_lang": "Python", "secondary_lang": "None",
            "labels": ["bounty", "easy"], "issue_number": 1, "creator": "user1", "status": "open",
            "value": 100.0 # Assuming pre-calculated value for simplicity in generator tests
        },
        {
            "timestamp": "2025-03-26 11:00:00", "owner": "org2", "repo": "repo2",
            "title": "Test Bounty 2", "url": "http://example.com/2", "amount": "50",
            "currency": "ERG", "primary_lang": "Rust", "secondary_lang": "None",
            "labels": ["bounty"], "issue_number": 2, "creator": "user2", "status": "open",
            "value": 50.0
        },
        {
            "timestamp": "2025-03-26 12:00:00", "owner": "org1", "repo": "repo3",
            "title": "Ongoing Program", "url": "http://example.com/3", "amount": "Ongoing",
            "currency": "Not specified", "primary_lang": "Python", "secondary_lang": "None",
            "labels": ["rewards"], "issue_number": 3, "creator": "user3", "status": "open",
            "value": 0.0
        }
    ]

@pytest.fixture
def mock_conversion_rates():
    """Provides sample conversion rates."""
    return {"SigUSD": 1.0, "ERG": 1.0, "gGOLD": 50.0}

@pytest.fixture
def mock_languages(mock_bounty_data):
    """Provides sample grouped languages."""
    # Simplified grouping for testing generators
    langs = {}
    for b in mock_bounty_data:
        lang = b['primary_lang']
        if lang not in langs: langs[lang] = []
        langs[lang].append(b)
    return langs

@pytest.fixture
def mock_orgs(mock_bounty_data):
    """Provides sample grouped orgs."""
    orgs_data = {}
    for b in mock_bounty_data:
        org = b['owner']
        if org not in orgs_data: orgs_data[org] = []
        orgs_data[org].append(b)
    return orgs_data

@pytest.fixture
def mock_currencies(mock_bounty_data):
    """Provides sample grouped currencies."""
    currencies_data = {}
    for b in mock_bounty_data:
        curr = b['currency']
        if curr == "Not specified": continue
        if curr not in currencies_data: currencies_data[curr] = []
        currencies_data[curr].append(b)
    return currencies_data


# --- Test Cases ---

# We use mock_open to simulate file writing without touching the disk
@patch("builtins.open", new_callable=mock_open)
@patch("src.generators.main.ensure_directory")
@patch("src.utils.common.get_current_timestamp", return_value="2025-03-26 14:00:00")
def test_generate_main_file(mock_ts, mock_ensure_dir, mock_file_open, mock_bounty_data, mock_languages, mock_currencies, mock_orgs, mock_conversion_rates):
    """Test the generate_main_file function."""
    project_totals = {"org1": {"count": 2, "value": 100.0}, "org2": {"count": 1, "value": 50.0}}
    total_bounties = 3
    total_value = 150.0
    bounties_dir = "temp_bounties"

    generate_main_file(
        mock_bounty_data, project_totals, mock_languages, mock_currencies, mock_orgs,
        mock_conversion_rates, total_bounties, total_value, bounties_dir
    )

    # Check if ensure_directory was called (it should be called implicitly via wrap_with_full_guardrails -> add_footer_buttons -> etc)
    # Check if open was called correctly
    expected_file_path = os.path.join(bounties_dir, 'all.md')
    mock_file_open.assert_called_once_with(expected_file_path, 'w', encoding='utf-8')

    # Check if some expected content is in the written data
    # handle() gives access to the mock file object
    handle = mock_file_open()
    written_content = handle.write.call_args[0][0]
    assert "# All Open Bounties" in written_content
    assert "Test Bounty 1" in written_content
    assert "Test Bounty 2" in written_content
    assert "Ongoing Program" in written_content # Check if ongoing programs are included
    assert "Total Bounties: 3" in written_content # Check navigation badge
    assert "2025-03-26 14:00:00 UTC" in written_content # Check timestamp

# Add more tests here for other generator functions
# e.g., test_generate_language_files, test_generate_summary_file, etc.
# Remember to mock file operations (open, os.path.exists, os.listdir) and dependencies like ensure_directory

def test_placeholder_generator(mock_bounty_data):
    """A placeholder test to ensure the file runs."""
    # TODO: Add real tests for other generator functions
    assert len(mock_bounty_data) == 3
