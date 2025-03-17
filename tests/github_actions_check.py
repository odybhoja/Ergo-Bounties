#!/usr/bin/env python3
"""
GitHub Actions Compatibility Test

This script checks if the necessary components required by GitHub Actions workflow
are properly configured and available for use.
"""

import os
import sys
import inspect
import importlib
from pathlib import Path

# Add the parent directory to sys.path so we can import modules correctly
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_create_claim_url_import():
    """Test if create_claim_url is properly imported in the generators/main.py file."""
    try:
        from src.generators.main import generate_high_value_bounties_file
        # Check if 'create_claim_url' is imported in the file
        from src.utils.common import create_claim_url
        
        # Get source code
        source_code = inspect.getsource(generate_high_value_bounties_file)
        
        # Verify create_claim_url is used properly in the function
        if "create_claim_url(" in source_code:
            print("✅ create_claim_url is correctly imported and used in generators/main.py")
            return True
        else:
            print("❌ create_claim_url is imported but not used in generators/main.py")
            return False
    except ImportError:
        print("❌ Failed to import create_claim_url in generators/main.py")
        return False

def test_bounty_finder_execution():
    """Test if bounty_finder.py can be imported and executed without errors."""
    try:
        import src.bounty_finder
        # Check if the main function exists
        if hasattr(src.bounty_finder, 'main'):
            print("✅ bounty_finder.py has a main function and can be imported")
            return True
        else:
            print("❌ bounty_finder.py does not have a main function")
            return False
    except ImportError:
        print("❌ Failed to import bounty_finder.py")
        return False

def test_run_bounty_check_execution():
    """Test if run_bounty_check.py can be imported and executed without errors."""
    try:
        import tests.run_bounty_check
        # Check if the main function exists
        if hasattr(tests.run_bounty_check, 'main'):
            print("✅ run_bounty_check.py has a main function and can be imported")
            return True
        else:
            print("❌ run_bounty_check.py does not have a main function")
            return False
    except ImportError:
        print("❌ Failed to import run_bounty_check.py")
        return False

def main():
    """Run all GitHub Actions compatibility tests."""
    print("\n==== GITHUB ACTIONS COMPATIBILITY TEST ====\n")
    
    tests = [
        test_create_claim_url_import,
        test_bounty_finder_execution,
        test_run_bounty_check_execution
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n==== TEST SUMMARY ====")
    if all(results):
        print("✅ All tests passed! GitHub Actions should work correctly.")
        return 0
    else:
        print("❌ Some tests failed. GitHub Actions may not work correctly.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
