#!/usr/bin/env python3
"""
Currency API Client Module

This module handles fetching and processing of currency exchange rates from various sources:
- Spectrum API for crypto tokens (SigUSD, GORT, RSN)
- Ergo Explorer API for accessing the Gold/ERG oracle pool data

It provides a consistent interface for getting up-to-date conversion rates that 
are used throughout the application for calculating bounty values.
"""

import logging
from typing import Dict, List, Any, Optional

from src.api.base_client import BaseClient

# Configure logging
logger = logging.getLogger(__name__)


class CurrencyClient(BaseClient):
    """
    Client for fetching currency conversion rates from various APIs.
    Provides methods for retrieving and processing currency data.
    """

    R4_REGISTER_KEY = 'R4'
    RENDERED_VALUE_KEY = 'renderedValue'
    VALUE_KEY = 'value'

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
        super().__init__(timeout=timeout)
        self.rates = {}

    def get_all_rates(self) -> Dict[str, float]:
        """
        Get conversion rates for all supported currencies.

        Returns:
            Dictionary mapping currency codes to their ERG exchange rate
        """
        # Clear existing rates
        self.rates = {}

        # Set initial default rates in case API calls fail
        self.rates["SigUSD"] = 0.819389
        self.rates["GORT"] = 12.76516
        self.rates["RSN"] = 18.563417
        self.rates["BENE"] = 0.819389

        # Get crypto token rates from Spectrum
        self._fetch_spectrum_rates()

        # Set BENE rate (equivalent to $1 worth of ERG)
        if "SigUSD" in self.rates:
            self.rates["BENE"] = self.rates["SigUSD"]
            logger.info(
                f"Setting BENE rate to {self.rates['BENE']} (equivalent to $1 worth of ERG)"
            )
        else:
            logger.warning("SigUSD rate not available, using default for BENE")

        # Get gold price from oracle pool
        self._fetch_gold_price()

        # Set default gold price if fetching failed
        if "gGOLD" not in self.rates:
            self.rates["gGOLD"] = 84.032555
            logger.warning("Gold price not available from oracle, using default rate")

        logger.info(f"Conversion rates: {self.rates}")
        return self.rates

    def _fetch_spectrum_rates(self) -> None:
        """
        Fetch crypto token rates from Spectrum API.
        Updates the internal rates dictionary with SigUSD, GORT, and RSN rates.
        """
        try:
            logger.info("Fetching market data from Spectrum API")
            response = self.session.get(self.SPECTRUM_API_URL, timeout=self.timeout)

            if response.status_code != 200:
                logger.error(f"Error fetching Spectrum API data: {response.status_code}")
                return

            markets = response.json()
            logger.debug(f"Spectrum API returned {len(markets)} markets")

            # Target tokens to fetch from Spectrum
            target_tokens = ["SigUSD", "GORT", "RSN"]

            for token in target_tokens:
                token_markets = [
                    m for m in markets
                    if m.get("quoteSymbol") == token and m.get("baseSymbol") == "ERG"
                ]

                if token_markets:
                    # Special sorting for SigUSD by volume
                    if token == "SigUSD" and "baseVolume" in token_markets[0]:
                        token_markets.sort(
                            key=lambda m: float(m.get("baseVolume", {}).get("value", 0)),
                            reverse=True,
                        )
                    
                    # Use the price from the first market (highest volume for SigUSD)
                    try:
                        self.rates[token] = float(token_markets[0].get("lastPrice"))
                        logger.info(f"Found {token} rate: {self.rates[token]}")
                    except (ValueError, TypeError, IndexError) as price_error:
                         logger.error(f"Error processing price for {token} from market data {token_markets[0]}: {price_error}")
                else:
                    logger.warning(f"No {token} markets found in API data")

        except Exception as e:
            logger.error(f"Error fetching or processing Spectrum rates: {e}")

    def _fetch_gold_price(self) -> None:
        """
        Fetch gold price from the XAU/ERG oracle pool.
        Updates the internal rates dictionary with gold price.
        """
        try:
            logger.info("Getting gold price from XAU/ERG oracle pool")

            oracle_url = (
                f"{self.ERGO_EXPLORER_API}/boxes/unspent/byTokenId/{self.XAU_ERG_ORACLE_NFT}"
            )
            response = self.session.get(oracle_url, timeout=60)  # Higher timeout for Explorer API

            if response.status_code != 200:
                logger.error(f"Oracle API returned status code {response.status_code}")
                return

            oracle_data = response.json()
            if not oracle_data.get("items") or len(oracle_data["items"]) == 0:
                logger.error("No oracle pool boxes found")
                return

            # Get the most recent box (usually the first one)
            latest_box = oracle_data["items"][0]

            # Extract the R4 register value
            if (
                "additionalRegisters" not in latest_box
                or self.R4_REGISTER_KEY not in latest_box["additionalRegisters"]
            ):
                logger.error("R4 register not found in oracle pool box")
                return

            r4_register = latest_box["additionalRegisters"][self.R4_REGISTER_KEY]
            r4_value = None

            if self.RENDERED_VALUE_KEY in r4_register:
                r4_value = r4_register[self.RENDERED_VALUE_KEY]
            elif self.VALUE_KEY in r4_register:
                r4_value = r4_register[self.VALUE_KEY]

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

    def calculate_erg_value(
        self,
        amount: str,
        currency: str,
        rates: Optional[Dict[str, float]] = None,
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
            return self._convert_currency_to_erg(amount, currency, conversion_rates)
        except Exception as e:
            logger.error(f"Error converting {amount} {currency} to ERG: {e}")
            return 0.0

    def _convert_currency_to_erg(self, amount: str, currency: str, rates: Dict[str, float]) -> float:
        """
        Helper function to convert an amount in a specific currency to ERG.

        Args:
            amount: Amount to convert as a string
            currency: Currency code
            rates: Dictionary of conversion rates

        Returns:
            ERG equivalent amount as a float, or 0 if conversion not possible
        """
        try:
            amount_float = float(amount)
            if currency == "ERG":
                return amount_float

            # Define conversion logic: rate key and operation (divide or multiply)
            conversion_map = {
                "SigUSD": ("SigUSD", "divide"),
                "GORT": ("GORT", "divide"),
                "RSN": ("RSN", "divide"),
                "BENE": ("BENE", "divide"),
                "g GOLD": ("gGOLD", "multiply"),
            }

            if currency in conversion_map:
                rate_key, operation = conversion_map[currency]
                if rate_key in rates:
                    rate = rates[rate_key]
                    if operation == "divide":
                        return amount_float / rate if rate != 0 else 0.0
                    elif operation == "multiply":
                        return amount_float * rate
                else:
                    logger.warning(f"Missing conversion rate for {rate_key} used by {currency}")
                    return 0.0
            else:
                logger.warning(f"Unknown currency: {currency}")
                return 0.0
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting {amount} {currency} to ERG: {e}")
            return 0.0
