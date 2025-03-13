<div align="center">
  <h1>🏆 Ergo Ecosystem Bounties</h1>
  <p><strong>The central hub for tracking, claiming, and managing bounties across the Ergo blockchain ecosystem</strong></p>
  <p>
    <a href="/bounty_issues.md"><img src="https://img.shields.io/badge/Open%20Bounties-100+-brightgreen" alt="Open Bounties"></a>
    <a href="/docs/submission-guide.md"><img src="https://img.shields.io/badge/Documentation-Submission%20Guide-blue" alt="Documentation"></a>
    <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/Contributions-Welcome-orange" alt="Contributions Welcome"></a>
  </p>
</div>

## 🌟 Overview

Ergo Ecosystem Bounties offers financial incentives to developers who contribute to the Ergo blockchain ecosystem by implementing features, fixing bugs, or improving documentation. This repository serves as the central coordination point for all bounty-related activities.

- **Browse open bounties** to find work that matches your skills
- **Reserve bounties** to prevent duplicate work
- **Submit completed work** to claim rewards
- **Add missing bounties** to help grow the ecosystem

## 📋 Open Bounties

**[View Current Open Bounties →](/bounty_issues.md)**

| Category | Count | Value |
|----------|-------|-------|
| Keystone Wallet Integration | [Details](https://discord.com/channels/668903786361651200/669989266478202917/1344310506277830697) | 3,000 ERG |
| [Fleet SDK Tutorials](https://github.com/fleet-sdk/docs/issues/8) | 7 | 775 SigUSD |
| [Weekly Bounties (Mar 12, 2025)](/bounty_issues.md) | 100 | 47,145.01 ERG | 
| **Total** | **108** | **50,920.01 ERG** |

Open bounties are updated weekly with values shown in ERG equivalent. Some bounties may be paid in other tokens as noted in the "Paid in" column of the bounty listings.

## 🔍 Adding a Missing Bounty

If you know of a bounty that's not listed here:

1. **Verify the Bounty** - Ensure it has:
   - A clear issue in a GitHub repository
   - A specified bounty value
   - The "Bounty" tag on the issue

2. **Submit a PR** to add the repository to our tracking system:
   - Fork this repository
   - Edit the `tracked_repos.json` file to add the new repository
   - Format: `{"owner": "repo-owner", "repo": "repo-name"}`
   - Submit a PR with title: `[ADD REPO] owner/repo-name`

3. **For Manual Additions** - If the bounty doesn't follow standard format:
   - Create an issue in this repository with details
   - Use title format: `[MANUAL BOUNTY] Brief description`
   - Include: link to work, bounty value, and payment currency

> 💡 **Note:** The bounty listings are automatically updated daily via GitHub Actions. When you add a new repository to `tracked_repos.json`, the system will automatically include its bounties in the next update.

## ⚙️ Automated Bounty Tracking

This repository uses GitHub Actions to automatically track and update the list of open bounties:

- **Daily Updates**: The bounty list is refreshed every day at midnight UTC
- **On-Demand Updates**: Triggered whenever `tracked_repos.json` is modified
- **Manual Trigger**: Maintainers can manually run the workflow when needed

The automation:
1. Scans all repositories listed in `tracked_repos.json`
2. Identifies issues with bounty tags or mentions
3. Extracts bounty amounts and currencies
4. Generates updated `bounty_issues.md` and CSV reports
5. Commits the changes back to the repository

To add a new repository to the tracking system, simply add it to `tracked_repos.json` and the automation will handle the rest.

## 🚀 Bounty Process

This repository uses a PR-based system for both reserving and submitting bounties:

- **Reserving a Bounty**: Submit a PR with a JSON file marked as `in-progress` to claim a bounty before starting work
- **Submitting Work**: Create or update a PR with your completed work details and set status to `awaiting-review`

Both processes use the same JSON template and PR workflow. Reservations are first-come, first-served.

**[📝 View the Detailed Submission Guide →](/docs/submission-guide.md)**

## 💰 Donations

The Ergo ecosystem bounty program is supported by donations. Contributions help fund Ergo core development, improve tooling, and promote Ergo technology among developers.

### Donation Addresses

**Multi-signature Wallet (3-of-5 threshold-sig):**  
[View on Explorer](https://ergexplorer.com/addresses#2BggBDgr9nBXyMpT5NbZf1QRN2pfHmzJxWwcfGEsgqzs94TEJv5GmtKTjmew74DjoTjTULa2A4RjJW6qGvniFm29KZKZ4attHxSZxuq1hQnXbURvoYm7jkHHzrd4ZF9u29cgHZczv2LWNiHoU6seFkC73JvGkT1khxkzRatPwDZ6aP87VPV6F4b1XmsitCB2DoKCYEtgtP1yCXmDhfSgdzDatn4SjSfZkxysggBH3TzJqTzZkqn8pp1DeAdiPJ1JZr8KeUGpnjkpjddoc)

**Paideia Wallet:**  
[View on Explorer](https://ergexplorer.com/addresses#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)

We appreciate donations, they will be spent on Ergo core development, improving tooling and promoting Ergo tech around developers. 

## OPEN BOUNTIES
|Owner|Title & Link|Count|Bounty ERG Equiv|Paid in|
|---|---|---|---|---|
| ergoplatform | [Make ErgoScript version of Merklized abstract syntax tree / finite state machine example tests](https://github.com/ergoplatform/sigmastate-interpreter/issues/1053) | 1 | 200.00 | ERG |
| ergoplatform | [Finish executeFromSelfReg implementation](https://github.com/ergoplatform/sigmastate-interpreter/issues/1039) | 2 | 636.46 | SigUSD |
| ergoplatform | [debug function](https://github.com/ergoplatform/sigmastate-interpreter/issues/1035) | 3 | 636.46 | SigUSD |
| ergoplatform | [Finish Bulletproofs range check example](https://github.com/ergoplatform/sigmastate-interpreter/issues/1032) | 4 | 200.00 | ERG |
| ergoplatform | [Add Numeric.toBits method](https://github.com/ergoplatform/sigmastate-interpreter/issues/992) | 5 | 200.00 | ERG |
| ergoplatform | [Consider using secp256k1-jni from Bitcoin-s](https://github.com/ergoplatform/sigmastate-interpreter/issues/970) | 6 | 636.46 | SigUSD |
| ergoplatform | [ Update flatMap documentation and remove unused code towards post-JIT semantics](https://github.com/ergoplatform/sigmastate-interpreter/issues/955) | 7 | 127.29 | SigUSD |
| ergoplatform | [Add cross-compilation to Scala3](https://github.com/ergoplatform/sigmastate-interpreter/issues/947) | 8 | 636.46 | SigUSD |
| ergoplatform | [Implement SBoolean.toByte](https://github.com/ergoplatform/sigmastate-interpreter/issues/931) | 9 | 636.46 | SigUSD |
| ergoplatform | [Inferred type is not checked agains ascription](https://github.com/ergoplatform/sigmastate-interpreter/issues/915) | 10 | 636.46 | SigUSD |
| ergoplatform | [Implement ContractTemplate compiler](https://github.com/ergoplatform/sigmastate-interpreter/issues/852) | 11 | 1272.91 | SigUSD |
| ergoplatform | [Serialize SFunc in TypeSerializer](https://github.com/ergoplatform/sigmastate-interpreter/issues/847) | 12 | 636.46 | SigUSD |
| ergoplatform | [[v6.0] Accumulate ErgoTree rewriting cost when handling Deserialize operations](https://github.com/ergoplatform/sigmastate-interpreter/issues/846) | 13 | 254.58 | SigUSD |
| ergoplatform | [Revise all error messages adopting usability pattern](https://github.com/ergoplatform/sigmastate-interpreter/issues/832) | 14 | 636.46 | SigUSD |
| ergoplatform | [Implement missing Unit support in compiler](https://github.com/ergoplatform/sigmastate-interpreter/issues/820) | 15 | 636.46 | SigUSD |
| ergoplatform | [Implement conversion from Long-encoded nBits representation to BigInt and back](https://github.com/ergoplatform/sigmastate-interpreter/issues/675) | 16 | 254.58 | SigUSD |
| ergoplatform | [Support n-ary functions in ErgoScript (front-end only)](https://github.com/ergoplatform/sigmastate-interpreter/issues/616) | 17 | 636.46 | SigUSD |
| ergoplatform | [Declared variable is missing in the environment (BigInt type)](https://github.com/ergoplatform/sigmastate-interpreter/issues/574) | 18 | 254.58 | SigUSD |
| ergoplatform | [Implement Some and None as global methods](https://github.com/ergoplatform/sigmastate-interpreter/issues/462) | 19 | 300.00 | ERG |
| ergoplatform | [Implementation of Box.getReg](https://github.com/ergoplatform/sigmastate-interpreter/issues/416) | 20 | 200.00 | ERG |
| ergoplatform | [Revise and optimize hashCode for Digest32 and other hashes](https://github.com/ergoplatform/sigmastate-interpreter/issues/197) | 21 | 254.58 | SigUSD |
| ergoplatform | [UnsignedBigInt implementation](https://github.com/ergoplatform/sigma-rust/issues/792) | 22 | 500.00 | ERG |
| ergoplatform | [New collection methods](https://github.com/ergoplatform/sigma-rust/issues/788) | 23 | 200.00 | ERG |
| ergoplatform | [Lazy default for Option.getOrElse and Coll.getOrElse](https://github.com/ergoplatform/sigma-rust/issues/787) | 24 | 100.00 | ERG |
| ergoplatform | [Add GetVar(inputIndex  varId) + fix Context.getVar](https://github.com/ergoplatform/sigma-rust/issues/785) | 25 | 100.00 | ERG |
| ergoplatform | [New Numeric Methods](https://github.com/ergoplatform/sigma-rust/issues/784) | 26 | 200.00 | ERG |
| ergoplatform | [(De)Serialize SFunc ](https://github.com/ergoplatform/sigma-rust/issues/783) | 27 | 100.00 | ERG |
| ergoplatform | [Add Python bindings](https://github.com/ergoplatform/sigma-rust/issues/780) | 28 | 954.68 | SigUSD |
| ergoplatform | [SOption[T] serialization support](https://github.com/ergoplatform/sigma-rust/issues/775) | 29 | 100.00 | ERG |
| ergoplatform | [Add Header.checkPow method](https://github.com/ergoplatform/sigma-rust/issues/767) | 30 | 200.00 | ERG |
| ergoplatform | [Autolykos 2 validation for custom messages](https://github.com/ergoplatform/sigma-rust/issues/766) | 31 | 200.00 | ERG |
| ergoplatform | [Add encodeNBits and decodeNBits methods](https://github.com/ergoplatform/sigma-rust/issues/765) | 32 | 200.00 | ERG |
| ergoplatform | [Improve README ](https://github.com/ergoplatform/sigma-rust/issues/759) | 33 | 636.46 | SigUSD |
| ergoplatform | [Criterion Benchmarks ](https://github.com/ergoplatform/sigma-rust/issues/739) | 34 | 254.58 | SigUSD |
| ergoplatform | [Add input extension to blockchain/transaction/byId JSON output](https://github.com/ergoplatform/ergo/issues/2200) | 35 | 50.00 | ERG |
| ergoplatform | [Put mining fee inputs into multiple transactions when too many of them](https://github.com/ergoplatform/ergo/issues/2185) | 36 | 118.70 | g GOLD |
| ergoplatform | [Inv - RequestModifier Test in ErgoNodeViewSynchronizerSpecification](https://github.com/ergoplatform/ergo/issues/2184) | 37 | 118.70 | g GOLD |
| ergoplatform | [Add new functionalities to improve mempool tracking efficiency](https://github.com/ergoplatform/ergo/issues/2174) | 38 | 118.70 | g GOLD |
| ergoplatform | [Update mempool asynchronously when processing a new block](https://github.com/ergoplatform/ergo/issues/2157) | 39 | 254.58 | SigUSD |
| ergoplatform | [ergo-core ci improvements](https://github.com/ergoplatform/ergo/issues/2134) | 40 | 127.29 | SigUSD |
| ergoplatform | [ErgoTransactionSpec is unstable](https://github.com/ergoplatform/ergo/issues/2095) | 41 | 127.29 | SigUSD |
| ergoplatform | [Label transactions with inputs not using blockchain context  simplify their revalidation in mempool](https://github.com/ergoplatform/ergo/issues/2092) | 42 | 636.46 | SigUSD |
| ergoplatform | [Implement UTXO set scan](https://github.com/ergoplatform/ergo/issues/2034) | 43 | 1272.91 | SigUSD |
| ergoplatform | [OrderedTxPool inconsistency ](https://github.com/ergoplatform/ergo/issues/1952) | 44 | 636.46 | SigUSD |
| ergoplatform | [Consider headers and full-blocks a peer has when requesting them ](https://github.com/ergoplatform/ergo/issues/1915) | 45 | 1272.91 | SigUSD |
| ergoplatform | [Log API queries (@DEBUG level)](https://github.com/ergoplatform/ergo/issues/1909) | 46 | 254.58 | SigUSD |
| ergoplatform | [/wallet/payment/send is trying to spend custom scan boxes](https://github.com/ergoplatform/ergo/issues/1905) | 47 | 636.46 | SigUSD |
| ergoplatform | [Timeout on /wallet/payment/send ](https://github.com/ergoplatform/ergo/issues/1885) | 48 | 636.46 | SigUSD |
| ergoplatform | [Fee estimation APIs getExpectedWaitTime/getRecommendedFee return invalid values](https://github.com/ergoplatform/ergo/issues/1884) | 49 | 636.46 | SigUSD |
| ergoplatform | [Consider slicing by height in /boxes/unspent](https://github.com/ergoplatform/ergo/issues/1870) | 50 | 636.46 | SigUSD |
| ergoplatform | [Rest endpoints `/utils/*` accept GET parameters with oversized ErgoTree/Address](https://github.com/ergoplatform/ergo/issues/1868) | 51 | 636.46 | SigUSD |
| ergoplatform | [Wrapping unconfirmed transactions](https://github.com/ergoplatform/ergo/issues/1753) | 52 | 1272.91 | SigUSD |
| ergoplatform | [Do not wallet-rescan blockchain from height 0 after wallet initialization](https://github.com/ergoplatform/ergo/issues/1722) | 53 | 636.46 | SigUSD |
| ergoplatform | [Change scan id type to long](https://github.com/ergoplatform/ergo/issues/1668) | 54 | 1272.91 | SigUSD |
| ergoplatform | [Set Loglevel via ergo.conf](https://github.com/ergoplatform/ergo/issues/1633) | 55 | 254.58 | SigUSD |
| ergoplatform | [An issue with restoring state after keepVersions = 0](https://github.com/ergoplatform/ergo/issues/1631) | 56 | 636.46 | SigUSD |
| ergoplatform | [Make a test that the UTXO set tree is not modified as a result of proofsForTransactions call](https://github.com/ergoplatform/ergo/issues/1614) | 57 | 254.58 | SigUSD |
| ergoplatform | [Optimize VersionedLDBAVLStorage methods](https://github.com/ergoplatform/ergo/issues/1598) | 58 | 636.46 | SigUSD |
| ergoplatform | [Make ErgoNodeViewHolder and its callers responsive](https://github.com/ergoplatform/ergo/issues/1588) | 59 | 1272.91 | SigUSD |
| ergoplatform | [Extract logic from CleanupWorker actor and test it ](https://github.com/ergoplatform/ergo/issues/1556) | 60 | 636.46 | SigUSD |
| ergoplatform | [Transactions returned from memory pool are Stream collection](https://github.com/ergoplatform/ergo/issues/1551) | 61 | 636.46 | SigUSD |
| ergoplatform | [Implement getSnapshotsInfo and snapshotsInfo network messages](https://github.com/ergoplatform/ergo/issues/1517) | 62 | 636.46 | SigUSD |
| ergoplatform | [Check spending of tokens created in offchain transaction ](https://github.com/ergoplatform/ergo/issues/1448) | 63 | 636.46 | SigUSD |
| ergoplatform | [Non-atomic update of HistoryStorage](https://github.com/ergoplatform/ergo/issues/1443) | 64 | 636.46 | SigUSD |
| ergoplatform | [Sign a custom message [Feature request]](https://github.com/ergoplatform/ergo/issues/1392) | 65 | 1272.91 | SigUSD |
| ergoplatform | [Add proof that interlink vector corresponds to its header](https://github.com/ergoplatform/ergo/issues/1384) | 66 | 1272.91 | SigUSD |
| ergoplatform | [NiPoPoW powered bootstrapping ](https://github.com/ergoplatform/ergo/issues/1365) | 67 | 6364.56 | SigUSD |
| ergoplatform | [Inrementally rebuild block candidate for the same height](https://github.com/ergoplatform/ergo/issues/1363) | 68 | 1272.91 | SigUSD |
| ergoplatform | [Unsupported HTTP method: HTTP method too long](https://github.com/ergoplatform/ergo/issues/1318) | 69 | 127.29 | SigUSD |
| ergoplatform | [Eliminate offchainRegistry](https://github.com/ergoplatform/ergo/issues/1228) | 70 | 636.46 | SigUSD |
| ergoplatform | [Light node with pruning can't catch after long shutdown ](https://github.com/ergoplatform/ergo/issues/1159) | 71 | 636.46 | SigUSD |
| ergoplatform | [Take into account dataInputs during mempool updateFamily](https://github.com/ergoplatform/ergo/issues/1156) | 72 | 200.00 | ERG |
| ergoplatform | [Unconfirmed wallet transactions during node restart](https://github.com/ergoplatform/ergo/issues/1154) | 73 | 1272.91 | SigUSD |
| ergoplatform | [FullBlockProcessor.isLinkable needed?](https://github.com/ergoplatform/ergo/issues/1125) | 74 | 200.00 | ERG |
| ergoplatform | [Make explicit representation of transactional graph in the memory pool](https://github.com/ergoplatform/ergo/issues/1051) | 75 | 200.00 | ERG |
| ergoplatform | [Wrap primitive types in communication between API and the core](https://github.com/ergoplatform/ergo/issues/1005) | 76 | 100.00 | ERG |
| ergoplatform | [Check how to run the node behind Tor and write a manual on that ](https://github.com/ergoplatform/ergo/issues/970) | 77 | 100.00 | ERG |
| ergoplatform | [Save version of the node in the Block Extensions section](https://github.com/ergoplatform/ergo/issues/962) | 78 | 200.00 | ERG |
| ergoplatform | [[API] Specify context variables in creating transaction](https://github.com/ergoplatform/ergo/issues/938) | 79 | 200.00 | ERG |
| ergoplatform | [API: /wallet/unlock  error message in response.](https://github.com/ergoplatform/ergo/issues/903) | 80 | 127.29 | SigUSD |
| ergoplatform | [Wallet API and Exchange Integration Documentation](https://github.com/ergoplatform/ergo/issues/878) | 81 | 200.00 | ERG |
| rosen-bridge | [Validate withdrawal address in Watcher](https://github.com/rosen-bridge/ui/issues/13) | 1 | 26.88 | RSN |
| rosen-bridge | [Add wallet disconnect button](https://github.com/rosen-bridge/ui/issues/12) | 2 | 10.75 | RSN |
| rosen-bridge | [Read lock addresses from address files](https://github.com/rosen-bridge/ui/issues/11) | 3 | 26.88 | RSN |
| rosen-bridge | [Add pagination to Watcher withdrawal token select](https://github.com/rosen-bridge/ui/issues/10) | 4 | 26.88 | RSN |
| rosen-bridge | [Link transaction ids of Watcher action responses to their appropriate block explorer](https://github.com/rosen-bridge/ui/issues/9) | 5 | 10.75 | RSN |
| rosen-bridge | [Remove `ignoreBuildErrors` from Next config](https://github.com/rosen-bridge/ui/issues/8) | 6 | 10.75 | RSN |
| ergoplatform | [Remove scan dependency](https://github.com/ergoplatform/oracle-core/pull/330) | 82 | 38.91 | GORT |
| StabilityNexus | [Submit tx fails if description is to long.](https://github.com/StabilityNexus/BenefactionPlatform-Ergo/issues/18) | 1 | 63.65 | BENE |
| StabilityNexus | [Amount limits on project actions](https://github.com/StabilityNexus/BenefactionPlatform-Ergo/issues/5) | 2 | 63.65 | BENE |
| ChainCashLabs | [Do tests for refund](https://github.com/ChainCashLabs/chaincash/issues/6) | 1 | 15.56 | GORT |
| ChainCashLabs | [Reserve contract for custom tokens](https://github.com/ChainCashLabs/chaincash/issues/3) | 2 | 38.91 | GORT |
| ChainCashLabs | [Support refunds](https://github.com/ChainCashLabs/chaincash-rs/issues/58) | 3 | 237.39 | g GOLD |
| ChainCashLabs | [/acceptance/checkNote API method](https://github.com/ChainCashLabs/chaincash-rs/issues/51) | 4 | 118.70 | g GOLD |
| ChainCashLabs | [Improving /healthcheck ](https://github.com/ChainCashLabs/chaincash-rs/issues/50) | 5 | 118.70 | g GOLD |
| ChainCashLabs | [Improve Project CI/CD Process](https://github.com/ChainCashLabs/chaincash-rs/issues/46) | 6 | 38.91 | GORT |
| ChainCashLabs | [Use sigma-rust for wallet functionality](https://github.com/ChainCashLabs/chaincash-rs/issues/42) | 7 | 38.91 | GORT |
| ChainCashLabs | [Unlock nodes wallet if locked](https://github.com/ChainCashLabs/chaincash-rs/issues/31) | 8 | 3.89 | GORT |
| ChainCashLabs | [Add openapi schema and swagger ui](https://github.com/ChainCashLabs/chaincash-rs/issues/28) | 9 | 15.56 | GORT |
| input-output-hk | [Check or restore keys during sliced tree recovery ](https://github.com/input-output-hk/scrypto/issues/89) | 1 | 636.46 | SigUSD |
|---|---|---|---|---|
|---|**Project**|---|**Count**|**ERG Equivalent**|
|---| **ergoplatform Subtotal:** |   | 82 | 45,641.84 |
|---| **rosen-bridge Subtotal:** |   | 6 | 112.88 |
|---| **StabilityNexus Subtotal:** |   | 2 | 127.29 |
|---| **ChainCashLabs Subtotal:** |   | 9 | 626.54 |
|---| **input-output-hk Subtotal:** |   | 1 | 636.46 |
|---|---|---|---|---|
|---| **Overall Totals:** |   | 100 | 47,145.01 |

Report generated: 2025-03-12 08:48:52 UTC

## Listing of Repos Queried 
|Owner|Repo|
|---|---|
|ergoplatform|sigmastate-interpreter|
|ergoplatform|sigma-rust|
|ergoplatform|ergo|
|rosen-bridge|ui|
|kushti|dexy-stable|
|ergoplatform|grow-ergo|
|ergoplatform|oracle-core|
|StabilityNexus|BenefactionPlatform-Ergo|
|ChainCashLabs|chaincash|
|ChainCashLabs|chaincash-rs| 
|input-output-hk|scrypto| ** added March 5th, 2025
