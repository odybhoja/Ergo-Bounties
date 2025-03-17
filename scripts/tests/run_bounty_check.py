#!/usr/bin/env python3
"""
Ergo Bounties Validation Tool

This script runs the bounty finder directly and validates the outputs, providing
a clean table-based summary of the results. It also tracks changes between runs.
"""

import os
import sys
import json
import subprocess
import re
import time
import logging
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, Any, List, Tuple, Optional

# Add colorful output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORED_OUTPUT = True
except ImportError:
    print("Installing colorama for colored output...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORED_OUTPUT = True

# Try to import tabulate for table formatting
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    print("Installing tabulate for table formatting...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
    from tabulate import tabulate
    TABULATE_AVAILABLE = True

# Get the absolute path to the project root directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
BOUNTIES_DIR = os.path.join(PROJECT_ROOT, 'bounties')
ENV_FILE = os.path.join(SCRIPTS_DIR, '.env')
BOUNTY_FINDER = os.path.join(SCRIPTS_DIR, 'bounty_finder.py')

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

def load_github_token() -> Optional[str]:
    """Load the GitHub token from the .env file."""
    try:
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    if key.strip() == 'github_token':
                        return value.strip('"\'')
        return None
    except Exception as e:
        logger.error(f"Error reading .env file: {e}")
        return None

def validate_github_token(token: Optional[str]) -> Tuple[bool, Dict[str, Any]]:
    """Validate the GitHub token and return its details."""
    if not token:
        return False, {"error": "No GitHub token found in .env file"}
    
    try:
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get('https://api.github.com/user', headers=headers)
        
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
    return len(glob(os.path.join(directory, pattern)))

def get_most_recent_file_time(directory: str, pattern: str = "*") -> float:
    """Get the most recent modification time of files matching a pattern."""
    from glob import glob
    files = glob(os.path.join(directory, pattern))
    if not files:
        return 0
    return max(os.path.getmtime(f) for f in files)

def count_markdown_files() -> Dict[str, int]:
    """Count the markdown files in the project."""
    result = {}
    
    # Count main files
    main_files = [
        'all.md', 'summary.md', 'featured_bounties.md', 
        'currency_prices.md', 'high-value-bounties.md'
    ]
    count = sum(1 for f in main_files if os.path.exists(os.path.join(BOUNTIES_DIR, f)))
    result["main_files"] = count
    
    # Count language files
    lang_dir = os.path.join(BOUNTIES_DIR, 'by_language')
    if os.path.exists(lang_dir):
        result["language_files"] = get_file_count(lang_dir, "*.md")
    else:
        result["language_files"] = 0
    
    # Count currency files
    currency_dir = os.path.join(BOUNTIES_DIR, 'by_currency')
    if os.path.exists(currency_dir):
        result["currency_files"] = get_file_count(currency_dir, "*.md")
    else:
        result["currency_files"] = 0
    
    # Count organization files
    org_dir = os.path.join(BOUNTIES_DIR, 'by_org')
    if os.path.exists(org_dir):
        result["org_files"] = get_file_count(org_dir, "*.md")
    else:
        result["org_files"] = 0
    
    result["total"] = (
        result["main_files"] + 
        result["language_files"] + 
        result["currency_files"] + 
        result["org_files"]
    )
    
    return result

def extract_info_from_output(output: str) -> Dict[str, Any]:
    """Extract useful information from the bounty finder output."""
    info = {}
    
    # Extract bounty count
    bounty_count_match = re.search(r"Total bounties found: (\d+)", output)
    if bounty_count_match:
        info["total_bounties"] = int(bounty_count_match.group(1))
    
    # Extract total value
    value_match = re.search(r"Total ERG equivalent value: ([\d\.]+)", output)
    if value_match:
        info["total_value"] = float(value_match.group(1))
    
    # Extract conversion rates
    rates_match = re.search(r"Using conversion rates: ({[^}]+})", output)
    if rates_match:
        rates_str = rates_match.group(1).replace("'", '"')
        try:
            # Clean up the string for JSON parsing
            rates_str = re.sub(r"(\w+):", r'"\1":', rates_str)
            rates = json.loads(rates_str)
            info["conversion_rates"] = rates
        except json.JSONDecodeError:
            # If parsing fails, just store the raw string
            info["conversion_rates_raw"] = rates_str
    
    # Count repositories processed
    repo_match = re.search(r"Processing (\d+) repositories", output)
    if repo_match:
        info["repositories_processed"] = int(repo_match.group(1))
    
    # Extract bounties by label
    bounty_labels = re.findall(r"Found bounty in label: ([\w\s]+)", output)
    if bounty_labels:
        # Group by currency
        bounty_groups = {}
        for label in bounty_labels:
            parts = label.split()
            if len(parts) >= 2:
                amount = parts[0]
                currency = parts[1]
                key = currency
                if key not in bounty_groups:
                    bounty_groups[key] = []
                bounty_groups[key].append(amount)
        
        info["bounties_by_currency"] = {}
        for currency, amounts in bounty_groups.items():
            info["bounties_by_currency"][currency] = len(amounts)
    
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
            f"{Fore.GREEN}✓{Style.RESET_ALL}" if COLORED_OUTPUT else "✓", 
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

def run_bounty_finder(token: Optional[str] = None) -> Dict[str, Any]:
    """Run the bounty finder script and capture its output."""
    results = {}
    
    start_time = time.time()
    try:
        # Check if the bounty finder exists
        if not os.path.exists(BOUNTY_FINDER):
            return {
                "success": False,
                "error": f"Bounty finder script not found at {BOUNTY_FINDER}"
            }
        
        # Run the bounty finder
        logger.info(f"Running bounty finder at {BOUNTY_FINDER}")
        
        # Set up environment variables
        env = os.environ.copy()
        
        # Add the project root directory to PYTHONPATH
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{PROJECT_ROOT}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = PROJECT_ROOT
            
        # Set the GitHub token in the environment
        if token:
            env['GITHUB_TOKEN'] = token
            logger.info("Set GITHUB_TOKEN environment variable")
        
        process = subprocess.run(
            [sys.executable, BOUNTY_FINDER],
            capture_output=True,
            text=True,
            env=env
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Process the result
        if process.returncode == 0:
            logger.info(f"Bounty finder completed successfully in {execution_time:.2f} seconds")
            results["success"] = True
            results["execution_time"] = execution_time
            
            # Extract useful information from the output
            results.update(extract_info_from_output(process.stderr))
        else:
            logger.error(f"Bounty finder failed with return code {process.returncode}")
            logger.error(f"Stderr: {process.stderr}")
            results["success"] = False
            results["error"] = process.stderr
            results["returncode"] = process.returncode
        
        return results
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger.error(f"Error running bounty finder: {e}")
        return {
            "success": False,
            "error": str(e),
            "execution_time": execution_time
        }

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
    token = load_github_token()
    valid_token, token_details = validate_github_token(token)
    
    results["github_token"] = {
        "valid": valid_token,
        "details": token_details
    }
    
    # 2. Run the bounty finder
    if valid_token:
        logger.info("Running bounty finder...")
        finder_results = run_bounty_finder(token)
        results.update(finder_results)
        
        # 3. Count generated files
        if finder_results.get("success", False):
            logger.info("Counting generated files...")
            file_counts = count_markdown_files()
            results["file_counts"] = file_counts
            
            # 4. Calculate changes from previous run
            if previous_state:
                logger.info(f"Calculating changes since previous run ({previous_run_time})...")
                changes = calculate_changes(previous_state, results)
                results["changes"] = changes
            
            # 5. Save current state for next run
            save_current_state(results)
    
    # 6. Print summary tables
    print_summary_table(results)
    
    # 7. Print changes if available
    if "changes" in results:
        print_changes_table(results["changes"], previous_run_time)
    
    # Return exit code based on success
    return 0 if results.get("success", False) else 1

if __name__ == "__main__":
    sys.exit(main())
