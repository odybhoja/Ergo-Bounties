#!/usr/bin/env python3
"""
Wrapper script to run the bounty finder.
This script imports and runs the main bounty_finder.py script.
"""

import sys
import os

# Add the parent directory to the path so we can import the bounty_finder module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main function from bounty_finder
from scripts.bounty_finder import main

if __name__ == "__main__":
    main()
