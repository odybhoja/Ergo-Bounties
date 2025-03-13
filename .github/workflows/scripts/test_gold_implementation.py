#!/usr/bin/env python3
import sys
import os
import json
from bounty_modules.conversion_rates import get_conversion_rates

def test_gold_implementation():
    """
    Test the gold price implementation in conversion_rates.py
    """
    print("Testing gold price implementation...")
    print("=" * 80)
    
    # Get conversion rates
    try:
        rates = get_conversion_rates()
        
        # Check if gGOLD rate was successfully retrieved
        if "gGOLD" in rates:
            gold_price = rates["gGOLD"]
            print("\nSUCCESS: Gold price retrieved successfully!")
            print(f"Gold price: {gold_price:.6f} ERG per gram")
            
            # Validate the gold price is reasonable
            if 50 <= gold_price <= 500:
                print("Gold price is within expected range (50-500 ERG per gram)")
            else:
                print(f"WARNING: Gold price {gold_price:.6f} ERG per gram is outside expected range")
        else:
            print("\nERROR: Failed to retrieve gold price")
            
        # Print all rates for reference
        print("\nAll conversion rates:")
        for currency, rate in rates.items():
            print(f"{currency}: {rate}")
            
    except Exception as e:
        print(f"\nERROR: Exception during test: {e}")
        
    print("\n" + "=" * 80)
    print("Test completed")

if __name__ == "__main__":
    test_gold_implementation()
