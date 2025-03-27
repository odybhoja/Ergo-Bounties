#!/usr/bin/env python3
"""
Ergo Bounties Validation Tool

This script runs validation checks on the bounty finder outputs, providing
a clean table-based summary of the results. It also tracks changes between runs.
"""

import os
import sys
import json
import re
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import requests

# Add the parent directory to sys.path so we can import modules correctly
sys.path.append(str(Path(__file__).parent.parent))

def _install_and_import(module_name: str):
    """Install a module if it's not already installed and then import it."""
    try:
        return __import__(module_name)
    except ImportError:
        print(f"Installing {module_name}...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
        return __import__(module_name)

# Configure colorful output
try:
    colorama = _install_and_import("colorama")
    init = colorama.init
    Fore = colorama.Fore
    Style = colorama.Style
    init(autoreset=True)
    COLORED_OUTPUT = True
except ImportError:
    COLORED_OUTPUT = False

# Try to import tabulate for table formatting
try:
    tabulate = _install_and_import("tabulate")
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False

# Get paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
BOUNTIES_DIR = os.path.join(PROJECT_ROOT, 'data')
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'src')

# State file to track previous runs
STATE_FILE = os.path.join(SCRIPT_DIR, '.bounty_check_state.json')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=f"{Fore.CYAN}%(asctime)s{Style.RESET_ALL} - %(message)s" if COLORED_OUTPUT else "%(asctime)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger('bounty_check')

def print_header(title: str) -> None:
    """Print a formatted header."""
    width = 80
    if COLORED_OUTPUT:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'═' * width}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(width)}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'═' * width}{Style.RESET_ALL}\n")
    else:
        print(f"\n{'═' * width}")
        print(f"{title.center(width)}")
        print(f"{'═' * width}\n")

def print_status(message: str, status: bool, details: str = "") -> None:
    """Print a status message with colored status indicators."""
    status_str = f"{Fore.GREEN}✓ PASS{Style.RESET_ALL}" if status else f"{Fore.RED}✗ FAIL{Style.RESET_ALL}"
    
    if COLORED_OUTPUT:
        print(f"{Fore.WHITE}{message}:{' ' * (50 - len(message))}{status_str}  {details}")
    else:
        status_plain = "✓ PASS" if status else "✗ FAIL"
        print(f"{message}:{' ' * (50 - len(message))}{status_plain}  {details}")

def validate_github_token() -> Tuple[bool, Dict[str, Any]]:
    """Validate the GitHub token from environment and return its details."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        # Also try to load from .env file like config.py does
        env_files = [
            Path(os.path.join('src', '.env')),
            Path(os.path.join(PROJECT_ROOT, '.env'))
        ]
        for env_file in env_files:
            if env_file.exists():
                try:
                    with open(env_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if line.startswith('github_token='):
                                    token = line.split('=', 1)[1].strip('"\'')
                                    print(f"DEBUG: Found token in {env_file}: {token[:4]}...{token[-4:]}")
                                    break
                        if token:
                            break
                except Exception as e:
                    print(f"ERROR reading {env_file}: {e}")
    
    if not token:
        return False, {"error": "No GITHUB_TOKEN environment variable or in .env file found"}
    
    print(f"DEBUG: Using token: {token[:4]}...{token[-4:]}")
    
    try:
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        print(f"DEBUG: Making GitHub API request to validate token")
        response = requests.get('https://api.github.com/user', headers=headers)
        print(f"DEBUG: GitHub API response status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            rate_limit = response.headers.get('X-RateLimit-Remaining', 'Unknown')
            
            return True, {
                "username": user_data.get('login'),
                "rate_limit": rate_limit
            }
        else:
            return False, {
                "status_code": response.status_code,
                "message": response.json().get('message', 'Unknown error')
            }
            
    except Exception as e:
        return False, {"error": str(e)}

def get_file_count(directory: str, pattern: str = "*") -> int:
    """Get the number of files matching a pattern in a directory."""
    from glob import glob
    
    # Ensure directory path is absolute
    abs_directory = os.path.abspath(directory)
    logger.info(f"Counting files matching '{pattern}' in '{abs_directory}'")
    
    # Get absolute file paths
    files = glob(os.path.join(abs_directory, pattern))
    
    # Log found files for debugging
    if len(files) > 0:
        logger.info(f"Found {len(files)} files")
        for file in files[:5]:  # Log first 5 files
            logger.info(f"  - {os.path.basename(file)}")
        if len(files) > 5:
            logger.info(f"  - ... and {len(files) - 5} more")
    else:
        logger.warning(f"No files found matching '{pattern}' in '{abs_directory}'")
    
    return len(files)

def count_markdown_files() -> Dict[str, int]:
    """Count the markdown files in the project."""
    result = {}
    
    # Log the bounties directory
    logger.info(f"Counting files in BOUNTIES_DIR: {BOUNTIES_DIR}")
    logger.info(f"Absolute path: {os.path.abspath(BOUNTIES_DIR)}")
    
    # Count main files
    main_files = [
        'all.md', 'summary.md', 'featured_bounties.md', 
        'currency_prices.md', 'high-value-bounties.md'
    ]
    main_found = [f for f in main_files if os.path.exists(os.path.join(BOUNTIES_DIR, f))]
    count = len(main_found)
    result["main_files"] = count
    logger.info(f"Found {count} main files: {', '.join(main_found)}")
    
    # Count language files
    lang_dir = os.path.join(BOUNTIES_DIR, 'by_language')
    if os.path.exists(lang_dir) and os.path.isdir(lang_dir):
        result["language_files"] = get_file_count(lang_dir, "*.md")
        logger.info(f"Found {result['language_files']} language files in {lang_dir}")
    else:
        result["language_files"] = 0
        logger.warning(f"Language directory {lang_dir} does not exist or is not a directory")
    
    # Count currency files
    currency_dir = os.path.join(BOUNTIES_DIR, 'by_currency')
    if os.path.exists(currency_dir) and os.path.isdir(currency_dir):
        result["currency_files"] = get_file_count(currency_dir, "*.md")
        logger.info(f"Found {result['currency_files']} currency files in {currency_dir}")
    else:
        result["currency_files"] = 0
        logger.warning(f"Currency directory {currency_dir} does not exist or is not a directory")
    
    # Count organization files
    org_dir = os.path.join(BOUNTIES_DIR, 'by_org')
    if os.path.exists(org_dir) and os.path.isdir(org_dir):
        result["org_files"] = get_file_count(org_dir, "*.md")
        logger.info(f"Found {result['org_files']} organization files in {org_dir}")
    else:
        result["org_files"] = 0
        logger.warning(f"Organization directory {org_dir} does not exist or is not a directory")
    
    result["total"] = (
        result["main_files"] + 
        result["language_files"] + 
        result["currency_files"] + 
        result["org_files"]
    )
    
    logger.info(f"Total files found: {result['total']}")
    return result

def validate_api_prices() -> Dict[str, Any]:
    """
    Validate currency prices from APIs by making actual requests.
    
    Returns:
        Dictionary with validation results for each price source
    """
    logger.info("Validating API price sources...")
    results = {}
    
    # Import the currency client
    try:
        from src.api.currency_client import CurrencyClient
        
        # Create client instance and get rates
        logger.info("Creating CurrencyClient instance...")
        client = CurrencyClient()
        rates = client.get_all_rates()
        
        logger.info(f"Retrieved rates: {rates}")
        
        # Check each expected currency rate
        expected_currencies = ['SigUSD', 'GORT', 'RSN', 'BENE', 'gGOLD']
        
        results["rates_retrieved"] = rates
        results["rates_complete"] = all(currency in rates for currency in expected_currencies)
        results["rates_valid"] = all(rates.get(currency, 0) > 0 for currency in expected_currencies)
        
        # Check specific API endpoints
        results["sources"] = {}
        
        # Check Spectrum API
        try:
            logger.info("Testing Spectrum API directly...")
            response = requests.get(CurrencyClient.SPECTRUM_API_URL, timeout=30)
            results["sources"]["spectrum_api"] = {
                "status": response.status_code,
                "valid": response.status_code == 200
            }
            logger.info(f"Spectrum API status: {response.status_code}")
        except Exception as e:
            results["sources"]["spectrum_api"] = {
                "status": "error",
                "error": str(e),
                "valid": False
            }
            logger.error(f"Error testing Spectrum API: {e}")
        
        # Check Ergo Explorer API for gold oracle
        try:
            logger.info("Testing Ergo Explorer API directly...")
            oracle_url = f"{CurrencyClient.ERGO_EXPLORER_API}/boxes/unspent/byTokenId/{CurrencyClient.XAU_ERG_ORACLE_NFT}"
            response = requests.get(oracle_url, timeout=60)
            results["sources"]["oracle_api"] = {
                "status": response.status_code,
                "valid": response.status_code == 200
            }
            logger.info(f"Oracle API status: {response.status_code}")
        except Exception as e:
            results["sources"]["oracle_api"] = {
                "status": "error",
                "error": str(e),
                "valid": False
            }
            logger.error(f"Error testing Oracle API: {e}")
            
    except Exception as e:
        logger.error(f"Failed to validate API prices: {e}")
        results["error"] = str(e)
        results["valid"] = False
    
    return results

def extract_info_from_files() -> Dict[str, Any]:
    """Extract useful information from output files."""
    info = {}
    
    # Try to get bounty count and value from summary.md
    summary_path = os.path.join(BOUNTIES_DIR, 'summary.md')
    if os.path.exists(summary_path):
        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract total bounties count
                total_match = re.search(r"\|\s+\*\*Total\*\*\s+\|\s+\*\*(\d+)\*\*\s+\|", content)
                if total_match:
                    info["total_bounties"] = int(total_match.group(1))
                
                # Extract total value
                value_match = re.search(r"\|\s+\*\*Total\*\*\s+\|\s+\*\*\d+\*\*\s+\|\s+\*\*([\d,\.]+)\s+ERG\*\*\s+\|", content)
                if value_match:
                    info["total_value"] = float(value_match.group(1).replace(',', ''))
        except Exception as e:
            logger.error(f"Error parsing summary.md: {e}")
    
    # Try to get conversion rates from currency_prices.md
    prices_path = os.path.join(BOUNTIES_DIR, 'currency_prices.md')
    if os.path.exists(prices_path):
        try:
            with open(prices_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Find all conversion rates
                rate_matches = re.findall(r"\|\s+\[\w+\]\([^)]+\)\s+\|\s+([\d\.]+)\s+\|", content)
                if rate_matches:
                    info["conversion_rates"] = {}
                    
                    # Also find currency names
                    currency_matches = re.findall(r"\|\s+\[(\w+)\]\([^)]+\)\s+\|", content)
                    
                    for i, rate in enumerate(rate_matches):
                        if i < len(currency_matches):
                            info["conversion_rates"][currency_matches[i]] = float(rate)
        except Exception as e:
            logger.error(f"Error parsing currency_prices.md: {e}")
    
    # Count bounties by currency from by_currency directory
    currency_dir = os.path.join(BOUNTIES_DIR, 'by_currency')
    if os.path.exists(currency_dir):
        info["bounties_by_currency"] = {}
        
        for file in os.listdir(currency_dir):
            if file.endswith('.md'):
                try:
                    with open(os.path.join(currency_dir, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Extract currency name and count
                        currency_match = re.search(r"# ([^B][^\n]+) Bounties", content)
                        count_match = re.search(r"Total [^\n]+ bounties: \*\*(\d+)\*\*", content)
                        
                        if currency_match and count_match:
                            currency = currency_match.group(1).strip()
                            count = int(count_match.group(1))
                            
                            info["bounties_by_currency"][currency] = count
                except Exception as e:
                    logger.error(f"Error parsing {file}: {e}")
    
    # Count repositories from by_org directory
    org_dir = os.path.join(BOUNTIES_DIR, 'by_org')
    if os.path.exists(org_dir):
        info["repositories_processed"] = len(os.listdir(org_dir))
    
    # Validate API prices
    api_prices = validate_api_prices()
    info["api_prices"] = api_prices
    
    return info

def load_previous_state() -> Dict[str, Any]:
    """Load the previous state from the state file."""
    if not os.path.exists(STATE_FILE):
        return {}
    
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_current_state(state: Dict[str, Any]) -> None:
    """Save the current state to the state file."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving state file: {e}")

def calculate_changes(previous: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate changes between previous and current runs."""
    changes = {}
    
    # Compare bounty counts
    if "total_bounties" in previous and "total_bounties" in current:
        prev_count = previous["total_bounties"]
        curr_count = current["total_bounties"]
        changes["bounty_count_diff"] = curr_count - prev_count
    
    # Compare total value
    if "total_value" in previous and "total_value" in current:
        prev_value = previous["total_value"]
        curr_value = current["total_value"]
        changes["total_value_diff"] = curr_value - prev_value
    
    # Compare file counts
    if "file_counts" in previous and "file_counts" in current:
        prev_files = previous["file_counts"]["total"]
        curr_files = current["file_counts"]["total"]
        changes["files_diff"] = curr_files - prev_files
    
    # Compare currency distribution
    if "bounties_by_currency" in previous and "bounties_by_currency" in current:
        changes["currency_changes"] = {}
        
        # Find new or modified currencies
        for currency, count in current["bounties_by_currency"].items():
            if currency in previous["bounties_by_currency"]:
                prev_count = previous["bounties_by_currency"][currency]
                diff = count - prev_count
                if diff != 0:
                    changes["currency_changes"][currency] = diff
            else:
                changes["currency_changes"][currency] = count
        
        # Find removed currencies
        for currency in previous["bounties_by_currency"]:
            if currency not in current["bounties_by_currency"]:
                changes["currency_changes"][currency] = -previous["bounties_by_currency"][currency]
    
    return changes

def format_table(data: List[List[Any]], headers: List[str]) -> str:
    """Format a table using tabulate or manual formatting."""
    if TABULATE_AVAILABLE:
        return tabulate(data, headers=headers, tablefmt="grid")
    else:
        # Manual table formatting as fallback
        result = []
        
        # Add headers
        header_row = "| " + " | ".join(headers) + " |"
        result.append(header_row)
        
        # Add separator
        separator = "|-" + "-|-".join(["-" * len(h) for h in headers]) + "-|"
        result.append(separator)
        
        # Add data rows
        for row in data:
            data_row = "| " + " | ".join(str(cell) for cell in row) + " |"
            result.append(data_row)
        
        return "\n".join(result)

def print_summary_table(results: Dict[str, Any]) -> None:
    """Print a summary table of the results."""
    print_header("Ergo Bounties Validation Summary")
    
    # Generate Authentication section
    auth_data = []
    if "github_token" in results:
        status = "✓" if results["github_token"]["valid"] else "✗"
        if results["github_token"]["valid"]:
            username = results["github_token"]["details"]["username"]
            rate_limit = results["github_token"]["details"]["rate_limit"]
            auth_data.append([
                "GitHub Token", 
                f"{Fore.GREEN}{status}{Style.RESET_ALL}" if COLORED_OUTPUT else status, 
                f"Authenticated as {username}, Rate limit: {rate_limit}"
            ])
        else:
            error = results["github_token"]["details"].get("message", "Invalid token")
            auth_data.append([
                "GitHub Token", 
                f"{Fore.RED}{status}{Style.RESET_ALL}" if COLORED_OUTPUT else status, 
                f"Error: {error}"
            ])
    
    # Generate API Validation section
    api_data = []
    if "api_prices" in results:
        api_prices = results["api_prices"]
        
        # Check Spectrum API
        if "sources" in api_prices and "spectrum_api" in api_prices["sources"]:
            spectrum = api_prices["sources"]["spectrum_api"]
            status = "✓" if spectrum.get("valid", False) else "✗"
            status_code = spectrum.get("status", "unknown")
            api_data.append([
                "Spectrum API (Crypto rates)", 
                f"{Fore.GREEN}{status}{Style.RESET_ALL}" if COLORED_OUTPUT and spectrum.get("valid", False) else f"{Fore.RED}{status}{Style.RESET_ALL}" if COLORED_OUTPUT else status, 
                f"Status: {status_code}"
            ])
        
        # Check Oracle API
        if "sources" in api_prices and "oracle_api" in api_prices["sources"]:
            oracle = api_prices["sources"]["oracle_api"]
            status = "✓" if oracle.get("valid", False) else "✗"
            status_code = oracle.get("status", "unknown")
            api_data.append([
                "Oracle API (Gold price)", 
                f"{Fore.GREEN}{status}{Style.RESET_ALL}" if COLORED_OUTPUT and oracle.get("valid", False) else f"{Fore.RED}{status}{Style.RESET_ALL}" if COLORED_OUTPUT else status, 
                f"Status: {status_code}"
            ])
    
    # Generate Currency Rates section
    rates_data = []
    if "conversion_rates" in results:
        for currency, rate in results["conversion_rates"].items():
            if currency == "gGOLD":
                currency_display = "Gold (per gram)"
            else:
                currency_display = currency
                
            rates_data.append([
                currency_display, 
                f"{Fore.GREEN}✓{Style.RESET_ALL}" if COLORED_OUTPUT else "✓", 
                f"{rate} ERG"
            ])
    
    # Generate Bounty Data section
    bounty_data = []
    if "total_bounties" in results:
        bounty_data.append([
            "Total Bounties", 
            f"{Fore.GREEN}✓{Style.RESET_ALL}" if COLORED_OUTPUT else "✓", 
            f"{results['total_bounties']} bounties"
        ])
    
    if "total_value" in results:
        bounty_data.append([
            "Total ERG Value", 
            f"{Fore.GREEN}✓{Style.RESET_ALL}" if COLORED_OUTPUT else "✓", 
            f"{results['total_value']:,.2f} ERG"
        ])
    
    if "repositories_processed" in results:
        bounty_data.append([
            "Repositories Processed", 
            f"{Fore.GREEN}✓{Style.RESET_ALL}" if COLORED_OUTPUT else "✓", 
            f"{results['repositories_processed']} repos"
        ])
    
    # Generate Files section
    files_data = []
    if "file_counts" in results:
        counts = results["file_counts"]
        
        files_data.append([
            "Generated Files (Total)", 
            f"{Fore.GREEN}✓{Style.RESET_ALL}" if COLORED_OUTPUT and counts['total'] > 0 else f"{Fore.RED}✗{Style.RESET_ALL}" if COLORED_OUTPUT else "✓" if counts['total'] > 0 else "✗", 
            f"{counts['total']} files"
        ])
        
        files_data.append(["Main Files", "", f"{counts['main_files']} files"])
        files_data.append(["Language Files", "", f"{counts['language_files']} files"])
        files_data.append(["Currency Files", "", f"{counts['currency_files']} files"])
        files_data.append(["Organization Files", "", f"{counts['org_files']} files"])
    
    # Print tables
    if auth_data:
        print(f"\n{Fore.CYAN}AUTHENTICATION{Style.RESET_ALL}" if COLORED_OUTPUT else "\nAUTHENTICATION")
        print(format_table(auth_data, ["Check", "Status", "Details"]))
    
    if api_data:
        print(f"\n{Fore.CYAN}API PRICE SOURCES{Style.RESET_ALL}" if COLORED_OUTPUT else "\nAPI PRICE SOURCES")
        print(format_table(api_data, ["API Endpoint", "Status", "Details"]))
    
    if rates_data:
        print(f"\n{Fore.CYAN}CURRENCY RATES{Style.RESET_ALL}" if COLORED_OUTPUT else "\nCURRENCY RATES")
        print(format_table(rates_data, ["Currency", "Status", "Rate"]))
    
    if bounty_data:
        print(f"\n{Fore.CYAN}BOUNTY INFORMATION{Style.RESET_ALL}" if COLORED_OUTPUT else "\nBOUNTY INFORMATION")
        print(format_table(bounty_data, ["Metric", "Status", "Value"]))
    
    if files_data:
        print(f"\n{Fore.CYAN}GENERATED FILES{Style.RESET_ALL}" if COLORED_OUTPUT else "\nGENERATED FILES")
        print(format_table(files_data, ["File Type", "Status", "Count"]))

def print_changes_table(changes: Dict[str, Any], previous_run_time: str) -> None:
    """Print a table showing changes from the previous run."""
    if not changes:
        return
    
    print_header(f"Changes Since Previous Run ({previous_run_time})")
    
    data = []
    
    # Bounty count changes
    if "bounty_count_diff" in changes:
        diff = changes["bounty_count_diff"]
        if diff > 0:
            status = f"{Fore.GREEN}+{diff}{Style.RESET_ALL}" if COLORED_OUTPUT else f"+{diff}"
        elif diff < 0:
            status = f"{Fore.RED}{diff}{Style.RESET_ALL}" if COLORED_OUTPUT else f"{diff}"
        else:
            status = "No change"
        
        data.append(["Total Bounties", status, ""])
    
    # Value changes
    if "total_value_diff" in changes:
        diff = changes["total_value_diff"]
        if abs(diff) > 0.01:  # Only show if change is meaningful
            if diff > 0:
                status = f"{Fore.GREEN}+{diff:.2f} ERG{Style.RESET_ALL}" if COLORED_OUTPUT else f"+{diff:.2f} ERG"
            else:
                status = f"{Fore.RED}{diff:.2f} ERG{Style.RESET_ALL}" if COLORED_OUTPUT else f"{diff:.2f} ERG"
            
            data.append(["Total ERG Value", status, ""])
    
    # Files changes
    if "files_diff" in changes:
        diff = changes["files_diff"]
        if diff > 0:
            status = f"{Fore.GREEN}+{diff} files{Style.RESET_ALL}" if COLORED_OUTPUT else f"+{diff} files"
        elif diff < 0:
            status = f"{Fore.RED}{diff} files{Style.RESET_ALL}" if COLORED_OUTPUT else f"{diff} files"
        else:
            status = "No change"
        
        data.append(["Generated Files", status, ""])
    
    # Currency distribution changes
    if "currency_changes" in changes and changes["currency_changes"]:
        data.append(["", "", ""])
        data.append(["CURRENCY CHANGES", "", ""])
        
        for currency, diff in sorted(changes["currency_changes"].items(), key=lambda x: abs(x[1]), reverse=True):
            if diff > 0:
                status = f"{Fore.GREEN}+{diff}{Style.RESET_ALL}" if COLORED_OUTPUT else f"+{diff}"
            else:
                status = f"{Fore.RED}{diff}{Style.RESET_ALL}" if COLORED_OUTPUT else f"{diff}"
            
            data.append([f"{currency} Bounties", status, ""])
    
    if data:
        print(format_table(data, ["Metric", "Change", "Notes"]))
    else:
        print("No significant changes detected")

def main() -> int:
    """Main function to run the bounty check."""
    print_header("Ergo Bounties Validation")
    
    # Load previous state
    previous_state = load_previous_state()
    previous_run_time = previous_state.get("run_time", "Never")
    
    # Current run time
    current_run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Starting validation at {current_run_time}")
    
    # Prepare results dictionary
    results = {
        "run_time": current_run_time
    }
    
    # 1. Validate GitHub token
    logger.info("Validating GitHub token...")
    valid_token, token_details = validate_github_token()
    
    results["github_token"] = {
        "valid": valid_token,
        "details": token_details
    }
    
    # 2. Count generated files
    logger.info("Counting generated files...")
    file_counts = count_markdown_files()
    results["file_counts"] = file_counts
    
    # 3. Extract information from files
    logger.info("Extracting information from output files...")
    file_info = extract_info_from_files()
    results.update(file_info)
    
    # 4. Calculate changes from previous run
    if previous_state:
        logger.info(f"Calculating changes since previous run ({previous_run_time})...")
        changes = calculate_changes(previous_state, results)
        results["changes"] = changes
    
    # 5. Save current state for next run
    save_current_state(results)
    
    # 6. Dynamically update dashboard by re-reading file counts to simulate real-time updates
    import time
    for i in range(5):
        # Simulate dynamic changes by updating file counts
        dynamic_counts = count_markdown_files()  # Re-read file counts from current state of BOUNTIES_DIR
        results["file_counts"] = dynamic_counts
        # Also re-extract info, if needed (optional, uncomment next line if dynamic content is expected)
        # results.update(extract_info_from_files())
        # Clear screen using ANSI escape codes
        print("\033c", end="")
        print_header("Dynamic Dashboard [Test Environment]")
        print_summary_table(results)
        if "changes" in results:
            print_changes_table(results["changes"], previous_run_time)
        time.sleep(2)
    
    # Final static display of the summary after dynamic updates
    print("\033c", end="")
    print_header("Ergo Bounties Final Validation Summary")
    print_summary_table(results)
    if "changes" in results:
        print_changes_table(results["changes"], previous_run_time)
    
    # Return exit code based on validation
    # Check files, token validity, total bounties and API rates
    success = (
        # GitHub token not required for successful tests
        # results["github_token"]["valid"] and
        results["file_counts"]["total"] > 0 and
        "total_bounties" in results and 
        "api_prices" in results and
        results["api_prices"].get("rates_valid", False)
    )
    
    return 0 if success else 1
