# Currency Prices

*Report generated: 2025-03-14 21:07:21 UTC*

## Navigation

[![All Bounties](https://img.shields.io/badge/All_Bounties-106-blue)](all.md) [![By Language](https://img.shields.io/badge/By_Language-6-green)](by_language/) [![By Currency](https://img.shields.io/badge/By_Currency-6-yellow)](by_currency/) [![By Organization](https://img.shields.io/badge/By_Organization-6-orange)](by_org/) [![Currency Prices](https://img.shields.io/badge/Currency_Prices-5-purple)](currency_prices.md)

## Filter Bounties

**By Programming Language:** [Svelte (2)](by_language/svelte.md) • [Scala (71)](by_language/scala.md) • [Java (1)](by_language/java.md) • [Rust (23)](by_language/rust.md) • [TypeScript (6)](by_language/typescript.md) • [Various (2)](by_language/various.md)

**By Currency:** [BENE (2)](by_currency/bene.md) • [SigUSD (54)](by_currency/sigusd.md) • [ERG (28)](by_currency/erg.md) • [g GOLD (6)](by_currency/gold.md) • [GORT (7)](by_currency/gort.md) • [RSN (6)](by_currency/rsn.md)

**By Organization:** [StabilityNexus (2)](by_org/stabilitynexus.md) • [input-output-hk (1)](by_org/input-output-hk.md) • [ergoplatform (85)](by_org/ergoplatform.md) • [rosen-bridge (7)](by_org/rosen-bridge.md) • [ChainCashLabs (9)](by_org/chaincashlabs.md) • [EF_DAO_LLC (2)](by_org/ef_dao_llc.md)

## Current Prices

| Currency | ERG Equivalent | Notes |
|----------|----------------|-------|
| [BENE](by_currency/bene.md) | 1.220422 | No market value; pegged to $1 USD (same as SigUSD) |
| [GORT](by_currency/gort.md) | 0.078338 | From Spectrum Finance API (GORT/ERG market) |
| [RSN](by_currency/rsn.md) | 0.053869 | From Spectrum Finance API (RSN/ERG market) |
| [SigUSD](by_currency/sigusd.md) | 1.220422 | Stablecoin pegged to USD; from Spectrum Finance API |
| [g GOLD](by_currency/gold.md) | 87.605562 | Price per gram of gold; from XAU/ERG oracle pool |

*Note: These prices are used to calculate ERG equivalents for bounties paid in different currencies.*

## Data Sources & API Information

The currency prices are fetched from the following sources:

### Spectrum Finance API

Most token prices (SigUSD, GORT, RSN) are fetched from the Spectrum Finance API:

**Endpoint:** `https://api.spectrum.fi/v1/price-tracking/markets`

**Example Request:**
```bash
curl -X GET "https://api.spectrum.fi/v1/price-tracking/markets"
```

**Python Example:**
```python
import requests
response = requests.get("https://api.spectrum.fi/v1/price-tracking/markets", timeout=30)
markets = response.json()
```

#### SigUSD
Fetched by filtering Spectrum markets where `quoteSymbol` is "SigUSD" and `baseSymbol` is "ERG".

**Python Example:**
```python
sigusd_markets = [m for m in markets if m.get("quoteSymbol") == "SigUSD" and m.get("baseSymbol") == "ERG"]
sigusd_rate = float(sigusd_markets[0].get("lastPrice"))
```

#### GORT & RSN
Similarly fetched by filtering for their respective symbols paired with ERG:

**Python Example for GORT:**
```python
gort_markets = [m for m in markets if m.get("quoteSymbol") == "GORT" and m.get("baseSymbol") == "ERG"]
gort_rate = float(gort_markets[0].get("lastPrice"))
```

**Python Example for RSN:**
```python
rsn_markets = [m for m in markets if m.get("quoteSymbol") == "RSN" and m.get("baseSymbol") == "ERG"]
rsn_rate = float(rsn_markets[0].get("lastPrice"))
```

### Gold Price (g GOLD)

Gold price is fetched from the XAU/ERG oracle pool on the Ergo blockchain:

**Endpoint:** `https://api.ergoplatform.com/api/v1/boxes/unspent/byTokenId/3c45f29a5165b030fdb5eaf5d81f8108f9d8f507b31487dd51f4ae08fe07cf4a`

**Example Request:**
```bash
curl -X GET "https://api.ergoplatform.com/api/v1/boxes/unspent/byTokenId/3c45f29a5165b030fdb5eaf5d81f8108f9d8f507b31487dd51f4ae08fe07cf4a"
```

**Python Example:**
```python
import requests

# Oracle NFT token ID
XAU_ERG_ORACLE_NFT = "3c45f29a5165b030fdb5eaf5d81f8108f9d8f507b31487dd51f4ae08fe07cf4a"
ERGO_EXPLORER_API = "https://api.ergoplatform.com/api/v1"

# Get boxes containing the oracle pool NFT
oracle_url = f"{ERGO_EXPLORER_API}/boxes/unspent/byTokenId/{XAU_ERG_ORACLE_NFT}"
response = requests.get(oracle_url, timeout=60)
oracle_data = response.json()

# Get the most recent box (usually the first one)
latest_box = oracle_data['items'][0]

# Extract the R4 register value
r4_register = latest_box['additionalRegisters']['R4']
r4_value = r4_register.get('renderedValue') or r4_register.get('value')
r4_value = float(r4_value)

# Calculate the gold price using the formula
gold_price_per_gram_erg = (10**18) / (r4_value * 100)
```

**Calculation:**
The gold price is calculated from the R4 register of the latest oracle pool box using the formula:
`gold_price_per_gram_erg = (10^18) / (R4_value * 100)`

### BENE

BENE is pegged to $1 USD, so its ERG equivalent is set to the same value as SigUSD, which is also a USD stablecoin:

**Python Example:**
```python
# After getting SigUSD rate
bene_rate = sigusd_rate
```
