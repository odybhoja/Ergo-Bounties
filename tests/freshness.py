#!/usr/bin/env python3
"""
File Freshness Check

This script checks if generated markdown files are fresh (recently generated)
and is intended to be used as part of the test suite.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt="%H:%M:%S"
)
logger = logging.getLogger('freshness_check')

def check_freshness(directory_path, max_age_minutes=1):
    """
    Check if files in the directory are fresh (modified within max_age_minutes).
    
    Args:
        directory_path: Path to directory containing files to check
        max_age_minutes: Maximum age in minutes for files to be considered "fresh"
        
    Returns:
        Tuple of (bool, list): Whether all files are fresh, and list of stale files
    """
    # Convert minutes to seconds
    max_age_seconds = max_age_minutes * 60
    
    # Get current time
    current_time = time.time()
    
    # List of key files to check
    key_files = [
        'all.md',
        'summary.md',
        'featured_bounties.md',
        'currency_prices.md',
        'high-value-bounties.md'
    ]
    
    all_fresh = True
    all_populated = True
    stale_files = []
    empty_files = []
    
    # Check main files
    for file in key_files:
        file_path = os.path.join(directory_path, file)
        if os.path.exists(file_path):
            # Check file timestamp
            file_timestamp = os.path.getmtime(file_path)
            time_diff = current_time - file_timestamp
            
            # Check file is properly populated
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                is_populated = len(content) > 1000 and "Empty" not in content
                
                # Verify file has bounty content if it's all.md
                if file == 'all.md' and "| ERG |" not in content:
                    is_populated = False
                
                if not is_populated:
                    logger.error(f"❌ File {file} exists but has no/incomplete content!")
                    all_populated = False
                    empty_files.append(file)
            
            # Check freshness
            if time_diff < max_age_seconds:
                logger.info(f"✅ File {file} is fresh (modified {time_diff:.2f} seconds ago)")
            else:
                minutes_old = time_diff / 60
                logger.warning(f"⚠️ File {file} is stale (last modified {minutes_old:.1f} minutes ago)")
                all_fresh = False
                stale_files.append((file, time_diff))
        else:
            logger.error(f"❌ File {file} does not exist!")
            all_fresh = False
            all_populated = False
    
    # Print summary
    if all_fresh and all_populated:
        print("\n✅ All files are fresh (modified within the last", 
              f"{max_age_minutes} minutes) and properly populated")
    else:
        if not all_fresh:
            print(f"\n⚠️ STALE FILES DETECTED! The following files haven't been updated recently:")
            for file, time_diff in stale_files:
                minutes_old = time_diff / 60
                print(f"- {file}: last modified {minutes_old:.1f} minutes ago")
            print(f"\nFiles should be modified within the last {max_age_minutes} minutes.")
        
        if not all_populated:
            print(f"\n❌ EMPTY FILES DETECTED! The following files have no or incomplete content:")
            for file in empty_files:
                print(f"- {file}")
            print("\nFiles should contain proper bounty data.")
        
        print("\nTo generate fresh files with proper content, run the bounty finder script.")
    
    return all_fresh and all_populated, stale_files

if __name__ == "__main__":
    # Get data directory path
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        # Default to 'data' in the current project
        project_root = Path(__file__).parent.parent
        data_dir = os.path.join(project_root, 'data')
    
    # Set max age in minutes (default: 1 minutes)
    max_age = 1
    if len(sys.argv) > 2:
        try:
            max_age = float(sys.argv[2])
        except ValueError:
            pass
    
    # Check freshness and content
    print(f"Checking file freshness and content in: {data_dir}")
    print(f"Maximum age for files to be considered fresh: {max_age} minutes")
    fresh_and_populated, _ = check_freshness(data_dir, max_age)
    
    # Exit with appropriate status code
    sys.exit(0 if fresh_and_populated else 1)
