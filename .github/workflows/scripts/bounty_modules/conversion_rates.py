import requests

def get_conversion_rates():
    """
    Get conversion rates for various currencies to ERG.
    
    Returns:
        dict: Dictionary of currency rates
    """
    # Initialize rates with BENE at 0 (as specified)
    rates = {
        "BENE": 0.0
    }
    print(f"Setting BENE rate to 0 as it has no value/pair")
    
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
        
        # Get gold price from a public API
        try:
            # Using CoinGecko API to get gold price in USD
            gold_response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=gold&vs_currencies=usd")
            if gold_response.status_code == 200:
                gold_data = gold_response.json()
                gold_usd_price = gold_data.get('gold', {}).get('usd')
                
                if gold_usd_price:
                    # Convert gold price to ERG
                    # 1 troy ounce = 31.1035 grams
                    gold_price_per_gram_usd = gold_usd_price / 31.1035
                    
                    # Convert USD to ERG using SigUSD as bridge (SigUSD is pegged to USD)
                    # If 1 ERG = X SigUSD, and 1 SigUSD = 1 USD, then 1 gram of gold in ERG = gold_price_per_gram_usd / X
                    gold_price_per_gram_erg = gold_price_per_gram_usd / rates["SigUSD"]
                    
                    rates["gGOLD"] = gold_price_per_gram_erg
                    print(f"Found gold price: ${gold_usd_price} per troy oz, ${gold_price_per_gram_usd:.2f} per gram, {gold_price_per_gram_erg:.2f} ERG per gram")
                else:
                    print("Gold price data not found in CoinGecko response")
                    raise Exception("Gold price not available")
            else:
                print(f"Error fetching gold price: {gold_response.status_code}")
                raise Exception("Failed to fetch gold price data")
        except Exception as gold_error:
            print(f"Error getting gold price: {gold_error}")
            raise Exception(f"Gold price fetch failed: {gold_error}")
        
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
            return "0.00"  # BENE has no value
        elif currency == "g GOLD" and "gGOLD" in conversion_rates:
            return f"{float(amount) * conversion_rates['gGOLD']:.2f}"
        else:
            return amount  # For other currencies, just use the amount
    except ValueError:
        return amount
