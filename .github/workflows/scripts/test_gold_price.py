#!/usr/bin/env python3
import requests
import json

def test_gold_oracle():
    print("Testing gold price from Ergo oracle pool...")
    
    # Try different API endpoints
    print("\nTrying alternative API endpoints...")
    
    # First try the explorer v1 API
    print("\nQuerying explorer v1 API...")
    oracle_response = requests.get("https://api.ergoplatform.com/api/v1/boxes/unspent/byAddress/E61k6zqzJbBVMwXhS8JBtqwxfLfCjR3mp2Bpoz6CQBtKQaJZsRVa")
    
    if oracle_response.status_code != 200:
        print(f"Error: Explorer v1 API returned status code {oracle_response.status_code}")
        
        # Try the explorer v0 API as fallback
        print("\nTrying explorer v0 API...")
        oracle_response = requests.get("https://api.ergoplatform.com/api/v0/transactions/boxes/byAddress/unspent/E61k6zqzJbBVMwXhS8JBtqwxfLfCjR3mp2Bpoz6CQBtKQaJZsRVa")
        
        if oracle_response.status_code != 200:
            print(f"Error: Explorer v0 API returned status code {oracle_response.status_code}")
            
            # Try the Ergo node API as another fallback
            print("\nTrying direct curl command...")
            print("For reference, you can try this curl command directly:")
            print("curl -s 'https://api.ergoplatform.com/api/v1/boxes/unspent/byAddress/E61k6zqzJbBVMwXhS8JBtqwxfLfCjR3mp2Bpoz6CQBtKQaJZsRVa' | jq '.items[0].additionalRegisters.R4.renderedValue'")
            
            # Try a hardcoded value for testing
            print("\nUsing hardcoded test value for demonstration...")
            test_r4_value = 8154910.0  # Example value
            print(f"Test R4 value: {test_r4_value}")
            
            gold_price_per_gram_erg = (10**18) / test_r4_value
            print("\nGold price calculation with test value:")
            print(f"Formula: 10^18 / R4_value = 10^18 / {test_r4_value}")
            print(f"Result: {gold_price_per_gram_erg:.6f} ERG per gram")
            print(f"Result: {gold_price_per_gram_erg/1000:.6f} ERG per milligram")
            print(f"Result: {gold_price_per_gram_erg*1000:.6f} ERG per kilogram")
            
            return
    
    oracle_data = oracle_response.json()
    
    # Check if we got any boxes
    if not oracle_data.get('items') or len(oracle_data['items']) == 0:
        print("Error: No boxes found in oracle pool data")
        return
    
    # Get the most recent box (usually the first one)
    latest_box = oracle_data['items'][0]
    
    # Print box details for debugging
    print("\nLatest oracle pool box details:")
    print(f"Box ID: {latest_box.get('boxId')}")
    print(f"Creation height: {latest_box.get('creationHeight')}")
    
    # Print all registers
    print("\nBox registers:")
    registers = latest_box.get('additionalRegisters', {})
    for reg_name, reg_value in registers.items():
        print(f"{reg_name}: {reg_value}")
    
    # Get the R4 register value
    r4_value = latest_box.get('additionalRegisters', {}).get('R4', {}).get('renderedValue')
    
    if not r4_value:
        print("Error: R4 register not found in oracle pool data")
        return
    
    print(f"\nR4 value: {r4_value}")
    
    try:
        r4_value = float(r4_value)
        
        # Calculate gold price using the formula: 10^18 / R4_value
        gold_price_per_gram_erg = (10**18) / r4_value
        
        print("\nGold price calculation:")
        print(f"Formula: 10^18 / R4_value = 10^18 / {r4_value}")
        print(f"Result: {gold_price_per_gram_erg:.6f} ERG per gram")
        print(f"Result: {gold_price_per_gram_erg/1000:.6f} ERG per milligram")
        print(f"Result: {gold_price_per_gram_erg*1000:.6f} ERG per kilogram")
        
    except (ValueError, ZeroDivisionError) as e:
        print(f"Error calculating gold price: {e}")

def test_sigusd_rate():
    print("\nTesting SigUSD rate from Spectrum API...")
    
    # Get Spectrum API data for crypto rates
    spectrum_response = requests.get("https://api.spectrum.fi/v1/price-tracking/markets")
    
    if spectrum_response.status_code != 200:
        print(f"Error: API returned status code {spectrum_response.status_code}")
        return
    
    markets = spectrum_response.json()
    print(f"Spectrum API returned {len(markets)} markets")
    
    # Find ERG/SigUSD pairs (where baseSymbol is ERG and quoteSymbol is SigUSD)
    sigusd_markets = [m for m in markets if m.get("quoteSymbol") == "SigUSD" and 
                     m.get("baseSymbol") == "ERG"]
    
    if not sigusd_markets:
        print("Error: No SigUSD markets found")
        return
    
    # Sort by volume if available, otherwise use the first market
    if 'baseVolume' in sigusd_markets[0]:
        sigusd_markets.sort(key=lambda m: float(m.get('baseVolume', {}).get('value', 0)), reverse=True)
        print(f"Sorted SigUSD markets by volume, using the most liquid market")
    
    # Use the first (or most liquid) market
    sigusd_rate = float(sigusd_markets[0].get("lastPrice"))
    print(f"SigUSD rate: {sigusd_rate} (1 ERG = {sigusd_rate} SigUSD)")
    print(f"Inverse rate: {1/sigusd_rate:.6f} (1 SigUSD = {1/sigusd_rate:.6f} ERG)")

if __name__ == "__main__":
    test_gold_oracle()
    test_sigusd_rate()
