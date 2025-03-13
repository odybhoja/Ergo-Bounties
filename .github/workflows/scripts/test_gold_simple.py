#!/usr/bin/env python3
import requests

def test_gold_price():
    print("Testing gold price calculation...")
    
    # Oracle pool NFT ID for ERG/XAU
    xau_erg_oracle_nft = "3c45f29a5165b030fdb5eaf5d81f8108f9d8f507b31487dd51f4ae08fe07cf4a"
    
    # Direct API call to get boxes containing the oracle pool NFT
    try:
        # Using the explorer API to get boxes containing the oracle pool NFT
        oracle_url = f"https://api.ergoplatform.com/api/v1/boxes/unspent/byTokenId/{xau_erg_oracle_nft}"
        print(f"Querying oracle pool at: {oracle_url}")
        
        response = requests.get(oracle_url, timeout=60)  # Increase timeout to 60 seconds
        if response.status_code != 200:
            print(f"Error: Oracle API returned status code {response.status_code}")
            return
            
        oracle_data = response.json()
        if not oracle_data.get('items') or len(oracle_data['items']) == 0:
            print("Error: No oracle pool boxes found")
            return
            
        # Get the most recent box (usually the first one)
        latest_box = oracle_data['items'][0]
        
        # Print box details for debugging
        print("\nLatest oracle pool box details:")
        print(f"Box ID: {latest_box.get('boxId')}")
        
        # Extract the R4 register value
        if 'additionalRegisters' not in latest_box or 'R4' not in latest_box['additionalRegisters']:
            print("Error: R4 register not found in oracle pool box")
            return
            
        r4_register = latest_box['additionalRegisters']['R4']
        r4_value = None
        
        if 'renderedValue' in r4_register:
            r4_value = r4_register['renderedValue']
        elif 'value' in r4_register:
            r4_value = r4_register['value']
            
        if not r4_value:
            print("Error: Could not extract R4 value from register")
            return
            
        print(f"\nRaw R4 value from oracle: {r4_value}")
        
        # Convert R4 value to float
        r4_value = float(r4_value)
        
        # Try different scaling factors to find the correct one
        scaling_factors = [1, 10, 100, 1000, 10**6, 10**9, 10**12]
        
        print("\nTrying different scaling factors:")
        for factor in scaling_factors:
            # Calculate gold price using the formula: 10^18 / (R4_value * factor)
            gold_price = (10**18) / (r4_value * factor)
            print(f"Factor {factor}: {gold_price:.6f} ERG per gram")
            
            # Check if this is close to the expected value
            if 100 <= gold_price <= 150:
                print(f"  This factor gives a reasonable price (100-150 ERG per gram)")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gold_price()
