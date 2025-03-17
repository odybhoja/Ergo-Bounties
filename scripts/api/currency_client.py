#!/usr/bin/env python3
"""
Currency API Client Module

This module handles fetching and processing of currency exchange rates from various sources:
- Spectrum API for crypto tokens (SigUSD, GORT, RSN)
- Ergo Explorer API for accessing the Gold/ERG oracle pool data

It provides a consistent interface for getting up-to-date conversion rates that 
are used throughout the application for calculating bounty values.
"""

import requests
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class CurrencyClient:
    """
    Client for fetching currency conversion rates from various APIs.
    Provides methods for retrieving and processing currency data.
    """
    
    # API endpoints
    SPECTRUM_API_URL = "https://api.spectrum.fi/v1/price-tracking/markets"
    ERGO_EXPLORER_API = "https://api.ergoplatform.com/api/v1"
    
    # Token identifiers
    XAU_ERG_ORACLE_NFT = "3c45f29a5165b030fdb5eaf5d81f8108f9d8f507b31487dd51f4ae08fe07cf4a"
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the currency client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.rates = {}
    
    def get_all_rates(self) -> Dict[str, float]:
        """
        Get conversion rates for all supported currencies.
        
        Returns:
            Dictionary mapping currency codes to their ERG exchange rate
        """
        # Clear existing rates
        self.rates = {}
        
        # Get crypto token rates from Spectrum
        self._fetch_spectrum_rates()
        
        # Set BENE rate (equivalent to $1 worth of ERG)
        if "SigUSD" in self.rates:
            self.rates["BENE"] = self.rates["SigUSD"]
            logger.info(f"Setting BENE rate to {self.rates['BENE']} (equivalent to $1 worth of ERG)")
        else:
            logger.warning("SigUSD rate not available, BENE rate cannot be set")
        
        # Get gold price from oracle pool
        self._fetch_gold_price()
        
        logger.info(f"Conversion rates: {self.rates}")
        return self.rates
    
    def _fetch_spectrum_rates(self) -> None:
        """
        Fetch crypto token rates from Spectrum API.
        Updates the internal rates dictionary with SigUSD, GORT, and RSN rates.
        """
        try:
            logger.info("Fetching market data from Spectrum API")
            response = requests.get(self.SPECTRUM_API_URL, timeout=self.timeout)
            
            if response.status_code != 200:
                logger.error(f"Error fetching Spectrum API data: {response.status_code}")
                return
                
            markets = response.json()
            logger.debug(f"Spectrum API returned {len(markets)} markets")
            
            # Process SigUSD rate (critical for other conversions)
            sigusd_markets = [
                m for m in markets 
                if m.get("quoteSymbol") == "SigUSD" and m.get("baseSymbol") == "ERG"
            ]
            
            if sigusd_markets:
                # Sort by volume if available to get the most liquid market
                if 'baseVolume' in sigusd_markets[0]:
                    sigusd_markets.sort(
                        key=lambda m: float(m.get('baseVolume', {}).get('value', 0)), 
                        reverse=True
                    )
                
                self.rates["SigUSD"] = float(sigusd_markets[0].get("lastPrice"))
                logger.info(f"Found SigUSD rate: {self.rates['SigUSD']}")
            else:
                logger.error("No SigUSD markets found in API data")
            
            # Process GORT rate
            gort_markets = [
                m for m in markets 
                if m.get("quoteSymbol") == "GORT" and m.get("baseSymbol") == "ERG"
            ]
            
            if gort_markets:
                self.rates["GORT"] = float(gort_markets[0].get("lastPrice"))
                logger.info(f"Found GORT rate: {self.rates['GORT']}")
            else:
                logger.warning("No GORT markets found in API data")
            
            # Process RSN rate
            rsn_markets = [
                m for m in markets 
                if m.get("quoteSymbol") == "RSN" and m.get("baseSymbol") == "ERG"
            ]
            
            if rsn_markets:
                self.rates["RSN"] = float(rsn_markets[0].get("lastPrice"))
                logger.info(f"Found RSN rate: {self.rates['RSN']}")
            else:
                logger.warning("No RSN markets found in API data")
                
        except Exception as e:
            logger.error(f"Error fetching Spectrum rates: {e}")
    
    def _fetch_gold_price(self) -> None:
        """
        Fetch gold price from the XAU/ERG oracle pool.
        Updates the internal rates dictionary with gold price.
        """
        try:
            logger.info("Getting gold price from XAU/ERG oracle pool")
            
            oracle_url = f"{self.ERGO_EXPLORER_API}/boxes/unspent/byTokenId/{self.XAU_ERG_ORACLE_NFT}"
            response = requests.get(oracle_url, timeout=60)  # Higher timeout for Explorer API
            
            if response.status_code != 200:
                logger.error(f"Oracle API returned status code {response.status_code}")
                return
                
            oracle_data = response.json()
            if not oracle_data.get('items') or len(oracle_data['items']) == 0:
                logger.error("No oracle pool boxes found")
                return
                
            # Get the most recent box (usually the first one)
            latest_box = oracle_data['items'][0]
            
            # Extract the R4 register value
            if 'additionalRegisters' not in latest_box or 'R4' not in latest_box['additionalRegisters']:
                logger.error("R4 register not found in oracle pool box")
                return
                
            r4_register = latest_box['additionalRegisters']['R4']
            r4_value = None
            
            if 'renderedValue' in r4_register:
                r4_value = r4_register['renderedValue']
            elif 'value' in r4_register:
                r4_value = r4_register['value']
                
            if not r4_value:
                logger.error("Could not extract R4 value from register")
                return
                
            # Convert R4 value to float
            r4_value = float(r4_value)
            
            # Calculate the gold price using the formula: 10^18 / (R4_value * 100)
            gold_price_per_gram_erg = (10**18) / (r4_value * 100)
            
            logger.info(f"Gold price from oracle: {gold_price_per_gram_erg:.6f} ERG per gram")
            self.rates["gGOLD"] = gold_price_per_gram_erg
            
        except Exception as e:
            logger.error(f"Error fetching gold price: {e}")
    
    def convert_to_erg(
        self, 
        amount: str, 
        currency: str, 
        rates: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Convert an amount in a specific currency to ERG equivalent.
        
        Args:
            amount: Amount to convert as a string
            currency: Currency code
            rates: Optional dictionary of conversion rates (uses internal rates if not provided)
            
        Returns:
            ERG equivalent amount as a string, or original amount if conversion not possible
        """
        if amount == "Not specified" or amount == "Ongoing":
            return amount
            
        # Use provided rates or fall back to internal rates
        conversion_rates = rates if rates is not None else self.rates
        
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
                return f"{float(amount) / conversion_rates['BENE']:.2f}"
            elif currency == "g GOLD" and "gGOLD" in conversion_rates:
                return f"{float(amount) * conversion_rates['gGOLD']:.2f}"
            else:
                logger.warning(f"Cannot convert {currency} to ERG (no conversion rate available)")
                return amount
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting {amount} {currency} to ERG: {e}")
            return amount
    
    def calculate_erg_value(
        self, 
        amount: str, 
        currency: str, 
        rates: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate ERG value from amount and currency.
        
        Args:
            amount: Amount as a string
            currency: Currency code
            rates: Optional dictionary of conversion rates (uses internal rates if not provided)
            
        Returns:
            ERG value as a float, or 0 if conversion not possible
        """
        if amount == "Not specified" or amount == "Ongoing":
            return 0.0
            
        # Use provided rates or fall back to internal rates
        conversion_rates = rates if rates is not None else self.rates
        
        try:
            if currency == "ERG":
                return float(amount)
            elif currency == "SigUSD" and "SigUSD" in conversion_rates:
                return float(amount) / conversion_rates["SigUSD"]
            elif currency == "GORT" and "GORT" in conversion_rates:
                return float(amount) / conversion_rates["GORT"]
            elif currency == "RSN" and "RSN" in conversion_rates:
                return float(amount) / conversion_rates["RSN"]
            elif currency == "BENE" and "BENE" in conversion_rates:
                return float(amount) / conversion_rates["BENE"]
            elif currency == "g GOLD" and "gGOLD" in conversion_rates:
                return float(amount) * conversion_rates["gGOLD"]
            else:
                logger.warning(f"Unknown currency or missing conversion rate: {currency}")
                return 0.0
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting {amount} {currency} to ERG: {e}")
            return 0.0
