<!-- GENERATED FILE - DO NOT EDIT DIRECTLY -->
<!-- Generated on: 2025-03-17 15:42:55 -->

# Currency Prices

# Currency Prices

*Report generated: 2025-03-17 15:42:55 UTC*

## Navigation

[![All Bounties](https://img.shields.io/badge/All%20Bounties-104-blue)](all.md) [![By Language](https://img.shields.io/badge/By%20Language-6-green)](by_language/) [![By Currency](https://img.shields.io/badge/By%20Currency-6-yellow)](by_currency/) [![By Organization](https://img.shields.io/badge/By%20Organization-6-orange)](by_org/) [![Currency Prices](https://img.shields.io/badge/Currency%20Prices-5-purple)](currency_prices.md)

## Filter Bounties

**By Programming Language:** [Svelte (2)](by_language/svelte.md) • [Scala (71)](by_language/scala.md) • [Java (1)](by_language/java.md) • [Rust (22)](by_language/rust.md) • [TypeScript (6)](by_language/typescript.md) • [Various (2)](by_language/various.md)

**By Currency:** [BENE (2)](by_currency/bene.md) • [SigUSD (54)](by_currency/sigusd.md) • [ERG (28)](by_currency/erg.md) • [g GOLD (6)](by_currency/gold.md) • [GORT (7)](by_currency/gort.md) • [RSN (6)](by_currency/rsn.md)

**By Organization:** [StabilityNexus (2)](by_org/stabilitynexus.md) • [input-output-hk (1)](by_org/input-output-hk.md) • [ergoplatform (84)](by_org/ergoplatform.md) • [rosen-bridge (6)](by_org/rosen-bridge.md) • [ChainCashLabs (9)](by_org/chaincashlabs.md) • [EF_DAO_LLC (2)](by_org/ef_dao_llc.md)

## Current Prices

| Currency | ERG Equivalent | Notes |
|----------|----------------|-------|
| [BENE](by_currency/bene.md) | 1.220422 | Each BENE is worth $1 in ERG |
| [GORT](by_currency/gort.md) | 0.078338 | Governance token for ErgoDEX |
| [RSN](by_currency/rsn.md) | 0.053869 | Governance token for Rosen Bridge |
| [SigUSD](by_currency/sigusd.md) | 1.220422 | Stablecoin pegged to USD |
| [gGOLD](by_currency/ggold.md) | 83.667208 | Price per gram of gold in ERG |

*Note: These prices are used to calculate ERG equivalents for bounties paid in different currencies.*

## How Prices are Retrieved

The currency prices are retrieved using different APIs:

### Spectrum API

SigUSD, GORT, and RSN prices are retrieved from the [Spectrum.fi](https://spectrum.fi/) API:

```
GET https://api.spectrum.fi/v1/price-tracking/markets
```

The API returns market data for various trading pairs. We filter this data to find specific currency pairs:

- For SigUSD: We look for markets where `quoteSymbol=SigUSD` and `baseSymbol=ERG`
- For GORT: We look for markets where `quoteSymbol=GORT` and `baseSymbol=ERG`
- For RSN: We look for markets where `quoteSymbol=RSN` and `baseSymbol=ERG`

### BENE

BENE price is set to be equivalent to SigUSD (which is pegged to USD), making 1 BENE equal to $1 worth of ERG.

### Gold Price from Oracle Pool

The price of gold (g GOLD) is retrieved from the XAU/ERG oracle pool using the Ergo Explorer API:

```
GET https://api.ergoplatform.com/api/v1/boxes/unspent/byTokenId/3c45f29a5165b030fdb5eaf5d81f8108f9d8f507b31487dd51f4ae08fe07cf4a
```

This queries for unspent boxes containing the oracle pool NFT. The price is extracted from the R4 register of the latest box.



---

<div align="center">
  <p>
    <a href="../docs/donate.md"><img src="https://img.shields.io/badge/❤️%20Donate-F44336" alt="Donate"></a>
    <a href="../docs/bounty-submission-guide.md#reserving-a-bounty"><img src="https://img.shields.io/badge/🔒%20Claim-4CAF50" alt="Claim a Bounty"></a>
  </p>
</div>


<!-- END OF GENERATED CONTENT -->
