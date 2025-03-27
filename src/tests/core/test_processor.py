"""
Unit tests for the BountyProcessor class.
"""

import pytest
from unittest.mock import MagicMock, patch

# Assuming BountyProcessor is importable like this
# Adjust the import path if necessary based on your project structure
from src.core.processor import BountyProcessor
from src.api.github_client import GitHubClient
from src.api.currency_client import CurrencyClient


# Example fixture for BountyProcessor instance
@pytest.fixture
def mock_rates():
    """Provides mock currency rates."""
    return {"SigUSD": 1.0, "ERG": 1.0, "gGOLD": 50.0}

@pytest.fixture
def mock_github_client(mocker):
    """Provides a mocked GitHubClient."""
    client = mocker.MagicMock(spec=GitHubClient)
    client.get_repository_languages.return_value = ["Python", "JavaScript"]
    client.get_repository_issues.return_value = [] # Default to no issues
    client.get_organization_repos.return_value = [] # Default to no org repos
    return client

@pytest.fixture
def mock_currency_client(mocker, mock_rates):
    """Provides a mocked CurrencyClient."""
    client = mocker.MagicMock(spec=CurrencyClient)
    client.rates = mock_rates
    client.calculate_erg_value.side_effect = lambda amount, currency: float(amount) * mock_rates.get(currency, 0) if amount not in ["Not specified", "Ongoing"] else 0.0
    return client

@pytest.fixture
def processor(mock_github_client, mock_currency_client, mock_rates):
    """Provides a BountyProcessor instance with mocked dependencies."""
    # We patch the clients within the scope of the fixture/test
    with patch('src.core.processor.GitHubClient', return_value=mock_github_client), \
         patch('src.core.processor.CurrencyClient', return_value=mock_currency_client):
        # The token doesn't matter here as the client is mocked
        proc = BountyProcessor(github_token="mock_token", rates=mock_rates)
        # Ensure the mocked clients are attached if needed by tests
        proc.github_client = mock_github_client
        proc.currency_client = mock_currency_client
        return proc

# --- Test Cases ---

def test_processor_initialization(processor, mock_rates):
    """Test that the processor initializes correctly."""
    assert processor is not None
    assert processor.bounty_data == []
    assert processor.project_totals == {}
    assert processor.currency_client.rates == mock_rates
    assert processor.github_client is not None

def test_placeholder_bounty_processing(processor):
    """A placeholder test to ensure the file runs."""
    # TODO: Add real tests for process_repositories, process_organizations, etc.
    assert True

def test_process_issue_marks_reserved_based_on_submission(processor, mock_github_client, mocker):
    """Test that an issue is marked as Reserved if a submission file exists."""
    repo_owner = "test-owner"
    repo_name = "test-repo"
    issue_number_reserved = 123
    issue_number_open = 456

    # Mock the _get_submitted_issue_numbers to simulate finding a submission
    mocker.patch.object(processor, '_get_submitted_issue_numbers', return_value={str(issue_number_reserved)})
    # Re-initialize the attribute based on the mocked method for this test instance
    processor.submitted_issue_numbers = processor._get_submitted_issue_numbers()

    # Mock GitHub API to return two issues: one matching the submission, one not
    mock_issues = [
        {
            "number": issue_number_reserved,
            "title": "Bounty: Reserved Issue",
            "state": "open", # Initially open
            "labels": [{"name": "bounty"}],
            "html_url": f"https://github.com/{repo_owner}/{repo_name}/issues/{issue_number_reserved}",
            "body": "Amount: 100 ERG",
            "user": {"login": "creator1"}
        },
        {
            "number": issue_number_open,
            "title": "Bounty: Open Issue",
            "state": "open",
            "labels": [{"name": "bounty"}],
            "html_url": f"https://github.com/{repo_owner}/{repo_name}/issues/{issue_number_open}",
            "body": "Amount: 50 ERG",
            "user": {"login": "creator2"}
        }
    ]
    mock_github_client.get_repository_issues.return_value = mock_issues

    # Define the repository to process
    repos_to_query = [{"owner": repo_owner, "repo": repo_name}]

    # Run the processing
    processor.process_repositories(repos_to_query)

    # Assertions
    assert processor.reserved_count == 1, "Should have counted one reserved bounty"
    assert len(processor.bounty_data) == 2, "Should have processed both issues"

    reserved_bounty = next((b for b in processor.bounty_data if b["issue_number"] == issue_number_reserved), None)
    open_bounty = next((b for b in processor.bounty_data if b["issue_number"] == issue_number_open), None)

    assert reserved_bounty is not None, "Reserved bounty should be in the data"
    assert reserved_bounty["status"] == "Reserved", "Status should be updated to Reserved"
    assert reserved_bounty["amount"] == "100", "Amount should be extracted correctly"
    assert reserved_bounty["currency"] == "ERG", "Currency should be extracted correctly"

    assert open_bounty is not None, "Open bounty should be in the data"
    assert open_bounty["status"] == "open", "Status should remain open"
    assert open_bounty["amount"] == "50", "Amount should be extracted correctly"
    assert open_bounty["currency"] == "ERG", "Currency should be extracted correctly"


# Add more tests here for different methods of BountyProcessor
# e.g., test_process_repositories_finds_bounty, test_add_extra_bounties,
# test_group_by_language, test_find_featured_bounties, etc.
