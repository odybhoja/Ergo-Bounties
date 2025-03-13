import requests
import json

def test_spectrum_api():
    """
    Test the Spectrum Finance API for token prices
    """
    print("Testing Spectrum Finance API for token prices...\n")
    
    # Fetch all markets
    print("Fetching all markets...")
    response = requests.get("https://api.spectrum.fi/v1/price-tracking/markets")
    
    if response.status_code != 200:
        print(f"Error: API returned status code {response.status_code}")
        return
    
    markets = response.json()
    print(f"Successfully fetched {len(markets)} markets\n")
    
    # Print all markets with SigUSD, GORT, or RSN in their symbols
    print("Looking for markets with SigUSD, GORT, or RSN...")
    tokens_of_interest = ["SigUSD", "GORT", "RSN"]
    
    for token in tokens_of_interest:
        print(f"\nMarkets related to {token}:")
        count = 0
        
        for market in markets:
            base_symbol = market.get("baseSymbol", "")
            quote_symbol = market.get("quoteSymbol", "")
            base_id = market.get("baseId", "")
            
            if token.lower() in base_symbol.lower() or token.lower() in quote_symbol.lower():
                count += 1
                print(f"Market {count}:")
                print(f"  Base: {base_symbol} (ID: {base_id})")
                print(f"  Quote: {quote_symbol}")
                print(f"  Last Price: {market.get('lastPrice')}")
                
                # Check if this is an ERG pair
                erg_id = "0000000000000000000000000000000000000000000000000000000000000001"
                if base_id == erg_id:
                    print(f"  ** This is an ERG/{token} pair **")
                elif "ERG" in base_symbol:
                    print(f"  ** This might be an ERG/{token} pair (based on symbol) **")
        
        if count == 0:
            print(f"No markets found for {token}")
    
    # Print all markets with ERG as base
    print("\nMarkets with ERG as base:")
    erg_id = "0000000000000000000000000000000000000000000000000000000000000001"
    erg_markets = [m for m in markets if m.get("baseId") == erg_id]
    
    if erg_markets:
        print(f"Found {len(erg_markets)} markets with ERG as base")
        print("First 10 ERG markets:")
        for i, market in enumerate(erg_markets[:10]):
            print(f"  {i+1}. ERG/{market.get('quoteSymbol')} - Price: {market.get('lastPrice')}")
    else:
        print("No markets found with ERG as base")
        
        # Try with symbol instead of ID
        erg_symbol_markets = [m for m in markets if "ERG" in m.get("baseSymbol", "")]
        if erg_symbol_markets:
            print(f"Found {len(erg_symbol_markets)} markets with ERG in base symbol")
            print("First 10 ERG symbol markets:")
            for i, market in enumerate(erg_symbol_markets[:10]):
                print(f"  {i+1}. {market.get('baseSymbol')}/{market.get('quoteSymbol')} - Price: {market.get('lastPrice')}")
    
    # Try the user's curl command approach
    print("\nTrying the approach from user's curl commands...")
    
    # For SigUSD
    sigusd_markets = [m for m in markets if m.get("quoteSymbol") == "SigUSD"]
    if sigusd_markets:
        print(f"Found {len(sigusd_markets)} markets with SigUSD as quote")
        for i, market in enumerate(sigusd_markets):
            print(f"  {i+1}. {market.get('baseSymbol')}/SigUSD - Price: {market.get('lastPrice')}")
    else:
        print("No markets found with SigUSD as quote")
    
    # For GORT
    gort_markets = [m for m in markets if m.get("quoteSymbol") == "GORT"]
    if gort_markets:
        print(f"Found {len(gort_markets)} markets with GORT as quote")
        for i, market in enumerate(gort_markets):
            print(f"  {i+1}. {market.get('baseSymbol')}/GORT - Price: {market.get('lastPrice')}")
    else:
        print("No markets found with GORT as quote")
    
    # For multiple tokens at once
    print("\nLooking for multiple tokens at once...")
    for token in tokens_of_interest:
        token_markets = [m for m in markets if m.get("quoteSymbol") == token]
        if token_markets:
            print(f"Found {len(token_markets)} markets with {token} as quote")
            for i, market in enumerate(token_markets[:3]):  # Show just the first 3
                print(f"  {i+1}. {market.get('baseSymbol')}/{token} - Price: {market.get('lastPrice')}")
        else:
            print(f"No markets found with {token} as quote")

if __name__ == "__main__":
    test_spectrum_api()
