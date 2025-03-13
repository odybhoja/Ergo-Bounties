import requests
import json

def get_conversion_rates():
    """
    Test the updated get_conversion_rates function
    """
    # Default rates to use if we can't find them in the API
    default_rates = {
        "SigUSD": 1.5,
        "GORT": 0.01,
        "RSN": 20.0,
        "gGOLD": 5.0
    }
    
    try:
        print("Fetching markets from Spectrum API...")
        response = requests.get("https://api.spectrum.fi/v1/price-tracking/markets")
        if response.status_code != 200:
            print(f"Warning: Error fetching conversion rates: {response.status_code}")
            return default_rates
            
        markets = response.json()
        print(f"Successfully fetched {len(markets)} markets")
        
        # Initialize with default rates
        rates = default_rates.copy()
        
        # Find ERG/SigUSD pairs (where baseSymbol is ERG and quoteSymbol is SigUSD)
        sigusd_markets = [m for m in markets if m.get("quoteSymbol") == "SigUSD" and 
                         m.get("baseSymbol") == "ERG"]
        print(f"Found {len(sigusd_markets)} ERG/SigUSD markets")
        for i, market in enumerate(sigusd_markets):
            print(f"  Market {i+1}: {market.get('baseSymbol')}/{market.get('quoteSymbol')} - Price: {market.get('lastPrice')}")
            print(f"    Market ID: {market.get('id', 'N/A')}")
            print(f"    Base ID: {market.get('baseId', 'N/A')}")
        
        # We should only use one market for SigUSD/ERG, preferably the most liquid one
        if sigusd_markets:
            # Sort by volume if available, otherwise use the first market
            if 'baseVolume' in sigusd_markets[0]:
                sigusd_markets.sort(key=lambda m: float(m.get('baseVolume', {}).get('value', 0)), reverse=True)
                print(f"Sorted markets by volume, using the most liquid market")
            
            # Use the first (or most liquid) market
            rates["SigUSD"] = float(sigusd_markets[0].get("lastPrice", default_rates["SigUSD"]))
            print(f"Using SigUSD rate: {rates['SigUSD']} from market {sigusd_markets[0].get('baseSymbol')}/{sigusd_markets[0].get('quoteSymbol')}")
        else:
            print(f"No SigUSD markets found, using default: {default_rates['SigUSD']}")
        
        # Find ERG/GORT pairs
        gort_markets = [m for m in markets if m.get("quoteSymbol") == "GORT" and 
                       m.get("baseSymbol") == "ERG"]
        if gort_markets:
            # Use the first market's price
            rates["GORT"] = float(gort_markets[0].get("lastPrice", default_rates["GORT"]))
            print(f"Found GORT rate: {rates['GORT']}")
        else:
            print(f"No GORT markets found, using default: {default_rates['GORT']}")
        
        # Find ERG/RSN pairs
        rsn_markets = [m for m in markets if m.get("quoteSymbol") == "RSN" and 
                      m.get("baseSymbol") == "ERG"]
        if rsn_markets:
            # Use the first market's price
            rates["RSN"] = float(rsn_markets[0].get("lastPrice", default_rates["RSN"]))
            print(f"Found RSN rate: {rates['RSN']}")
        else:
            print(f"No RSN markets found, using default: {default_rates['RSN']}")
        
        # For gGOLD (listed as "GluonW GAU")
        gold_markets = [m for m in markets if m.get("quoteSymbol") == "GluonW GAU"]
        if gold_markets:
            rates["gGOLD"] = float(gold_markets[0].get("lastPrice", default_rates["gGOLD"]))
            print(f"Found gGOLD rate: {rates['gGOLD']}")
        else:
            # Try alternative symbols
            alt_gold_markets = [m for m in markets if 
                               (m.get("quoteSymbol") in ["GAU", "GAUC"] or 
                                "GluonW" in m.get("quoteSymbol", ""))]
            if alt_gold_markets:
                rates["gGOLD"] = float(alt_gold_markets[0].get("lastPrice", default_rates["gGOLD"]))
                print(f"Found gGOLD rate (alternative): {rates['gGOLD']}")
            else:
                print(f"No gGOLD markets found, using default: {default_rates['gGOLD']}")
        
        print(f"\nFinal conversion rates: {rates}")
        return rates
    except Exception as e:
        print(f"Warning: Exception fetching conversion rates: {e}")
        print("Using default rates")
        return default_rates

if __name__ == "__main__":
    get_conversion_rates()
