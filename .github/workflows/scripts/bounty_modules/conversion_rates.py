import requests

def get_conversion_rates():
    """
    Get conversion rates for various currencies to ERG.
    
    Returns:
        dict: Dictionary of currency rates
    """
    # Initialize rates dictionary
    rates = {}
    
    try:
        # Get Spectrum API data for crypto rates
        spectrum_response = requests.get("https://api.spectrum.fi/v1/price-tracking/markets")
        if spectrum_response.status_code != 200:
            print(f"Warning: Error fetching Spectrum API conversion rates: {spectrum_response.status_code}")
            raise Exception("Failed to fetch Spectrum API data")
            
        markets = spectrum_response.json()
        print(f"Spectrum API returned {len(markets)} markets")
        
        # Find ERG/SigUSD pairs (where baseSymbol is ERG and quoteSymbol is SigUSD)
        sigusd_markets = [m for m in markets if m.get("quoteSymbol") == "SigUSD" and 
                         m.get("baseSymbol") == "ERG"]
        if sigusd_markets:
            # Sort by volume if available, otherwise use the first market
            if 'baseVolume' in sigusd_markets[0]:
                sigusd_markets.sort(key=lambda m: float(m.get('baseVolume', {}).get('value', 0)), reverse=True)
                print(f"Sorted SigUSD markets by volume, using the most liquid market")
            
            # Use the first (or most liquid) market
            rates["SigUSD"] = float(sigusd_markets[0].get("lastPrice"))
            print(f"Found SigUSD rate: {rates['SigUSD']} from market {sigusd_markets[0].get('baseSymbol')}/{sigusd_markets[0].get('quoteSymbol')}")
        else:
            print(f"No SigUSD markets found, cannot proceed without SigUSD rate")
            raise Exception("SigUSD rate not found in API data")
        
        # Find ERG/GORT pairs
        gort_markets = [m for m in markets if m.get("quoteSymbol") == "GORT" and 
                       m.get("baseSymbol") == "ERG"]
        if gort_markets:
            # Use the first market's price
            rates["GORT"] = float(gort_markets[0].get("lastPrice"))
            print(f"Found GORT rate: {rates['GORT']}")
        else:
            print(f"No GORT markets found in API data")
            raise Exception("GORT rate not found in API data")
        
        # Find ERG/RSN pairs
        rsn_markets = [m for m in markets if m.get("quoteSymbol") == "RSN" and 
                      m.get("baseSymbol") == "ERG"]
        if rsn_markets:
            # Use the first market's price
            rates["RSN"] = float(rsn_markets[0].get("lastPrice"))
            print(f"Found RSN rate: {rates['RSN']}")
        else:
            print(f"No RSN markets found in API data")
            raise Exception("RSN rate not found in API data")
        
        # Set BENE to $1 worth of ERG
        if "SigUSD" in rates:
            rates["BENE"] = rates["SigUSD"]
            print(f"Setting BENE rate to {rates['BENE']} (equivalent to $1 worth of ERG)")
        else:
            rates["BENE"] = 0.0
            print(f"Warning: SigUSD rate not available, setting BENE to 0")
        
        # Get gold price from XAU/ERG oracle pool
        print("Getting gold price from XAU/ERG oracle pool...")
        
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
                raise Exception(f"Failed to access oracle API: {response.status_code}")
                
            oracle_data = response.json()
            if not oracle_data.get('items') or len(oracle_data['items']) == 0:
                print("Error: No oracle pool boxes found")
                raise Exception("No oracle pool boxes found")
                
            # Get the most recent box (usually the first one)
            latest_box = oracle_data['items'][0]
            
            # Extract the R4 register value
            if 'additionalRegisters' not in latest_box or 'R4' not in latest_box['additionalRegisters']:
                print("Error: R4 register not found in oracle pool box")
                raise Exception("R4 register not found")
                
            r4_register = latest_box['additionalRegisters']['R4']
            r4_value = None
            
            if 'renderedValue' in r4_register:
                r4_value = r4_register['renderedValue']
            elif 'value' in r4_register:
                r4_value = r4_register['value']
                
            if not r4_value:
                print("Error: Could not extract R4 value from register")
                raise Exception("R4 value not found")
                
            print(f"Raw R4 value from oracle: {r4_value}")
            
            # Convert R4 value to float
            r4_value = float(r4_value)
            
            # For XAU/ERG oracle, the R4 value needs to be properly scaled
            # Based on the observed value and expected result (~122.635 ERG per gram)
            # We need to scale the R4 value appropriately
            
            # Calculate the gold price using the formula: 10^18 / (R4_value * 100)
            # This scaling factor is derived from the oracle pool's data format and testing
            gold_price_per_gram_erg = (10**18) / (r4_value * 100)
            
            print(f"Gold price from oracle: {gold_price_per_gram_erg:.6f} ERG per gram")
            rates["gGOLD"] = gold_price_per_gram_erg
            
        except Exception as e:
            print(f"Error getting gold price from oracle: {e}")
            # No fallbacks - if we can't get the oracle price, we don't set a value
            print("No fallback implemented - gold price will not be available")
        
        print(f"Using conversion rates: {rates}")
        return rates
    except Exception as e:
        print(f"Warning: Exception fetching conversion rates: {e}")
        return rates  # Return what we have so far

def convert_to_erg(amount, currency, conversion_rates):
    """
    Convert an amount in a specific currency to ERG equivalent.
    
    Args:
        amount (str): Amount to convert
        currency (str): Currency to convert from
        conversion_rates (dict): Dictionary of conversion rates
        
    Returns:
        str: ERG equivalent amount or original amount if conversion not possible
    """
    if amount == "Not specified":
        return amount
        
    try:
        if currency == "ERG":
            return amount
        elif currency == "SigUSD" and "SigUSD" in conversion_rates:
            return f"{float(amount) / conversion_rates['SigUSD']:.2f}"
        elif currency == "GORT" and "GORT" in conversion_rates:
            return f"{float(amount) / conversion_rates['GORT']:.2f}"
        elif currency == "RSN" and "RSN" in conversion_rates:
            return f"{float(amount) / conversion_rates['RSN']:.2f}"
        elif currency == "BENE" and "BENE" in conversion_rates:
            return f"{float(amount) / conversion_rates['BENE']:.2f}"  # BENE is worth $1 in ERG
        elif currency == "g GOLD" and "gGOLD" in conversion_rates:
            return f"{float(amount) * conversion_rates['gGOLD']:.2f}"
        else:
            return amount  # For other currencies, just use the amount
    except ValueError:
        return amount
