# 🔄 Ongoing Reward Programs

In addition to specific bounties, the Ergo ecosystem offers ongoing reward programs to encourage continuous contributions in key areas. These programs provide opportunities for contributors to receive rewards for their work even if there isn't a specific bounty listed.

## Current Ongoing Programs

<!-- BEGIN_ONGOING_PROGRAMS_TABLE -->
| Organization | Program | Details | Primary Language |
|-------------|---------|---------|------------------|
| [EF_DAO_LLC](by_org/ef_dao_llc.md) | [Educational Reward Program](#-educational-reward-program) | [Details](#-educational-reward-program) | [Various](by_language/various.md) |
| [EF_DAO_LLC](by_org/ef_dao_llc.md) | [Development Reward Program](#-development-reward-program) | [Details](#-development-reward-program) | [Various](by_language/various.md) |
<!-- END_ONGOING_PROGRAMS_TABLE -->

## Current Active Bounties

<!-- BEGIN_ACTIVE_BOUNTIES_TABLE -->
The following bounties are currently active and available for contribution:

| Organization | Repository | Title & Link | Bounty Amount | Paid in | Primary Language | Reserve |
|--------------|------------|--------------|--------------|---------|------------------|---------|
| [DevDAO](../data/by_org/devdao.md) | [keystone-integration](https://github.com/DevDAO/keystone-integration) | [Keystone Wallet Integration](https://discord.com/channels/668903786361651200/669989266478202917/1344310506277830697) | 3000 (3000.00 ERG) | [ERG](../data/by_currency/erg.md) | [Various](../data/by_language/various.md) | [<kbd>Reserve</kbd>](https://github.com/DevDAO/keystone-integration/issues/new?title=Reservation:%20Keystone%20Wallet%20Integration&body=%23%20Bounty%20Reservation%0A%0A%2A%2ATitle%3A%2A%2A%20Keystone%20Wallet%20Integration%0A%2A%2ABounty%20Link%3A%2A%2A%20https%3A%2F%2Fdiscord.com%2Fchannels%2F668903786361651200%2F669989266478202917%2F1344310506277830697%0A%2A%2AValue%3A%2A%2A%203000%20ERG%0A%0A%23%23%20Developer%20Information%0A%0A%2A%2AGitHub%20Username%3A%2A%2A%20%5BYour%20GitHub%20Username%5D%0A%2A%2ADiscord%20Username%20(optional)%3A%2A%2A%20%5BYour%20Discord%20handle%20for%20any%20questions%5D%0A%0A%23%23%20Development%20Plan%0A%0APlease%20share%20a%20brief%20overview%20of%3A%0A%0A-%20Your%20approach%20to%20implementing%20this%20bounty%0A-%20Estimated%20timeframe%20for%20completion%0A-%20Any%20questions%20you%20have%20about%20the%20requirements%0A%0A%2A%2ANote%3A%2A%2A%20By%20submitting%20this%20reservation%2C%20you%20are%20committing%20to%20working%20on%20this%20bounty.%20If%20you%20later%20decide%20not%20to%20proceed%2C%20please%20close%20this%20issue%20so%20others%20can%20work%20on%20it.) |
| [fleet-sdk](../data/by_org/fleet-sdk.md) | [docs](https://github.com/fleet-sdk/docs) | [[Educational] Fleet-Tutorial + Bounties](https://github.com/fleet-sdk/docs/issues/8) | 775 (775.00 ERG) | [SigUSD](../data/by_currency/sigusd.md) | [Various](../data/by_language/various.md) | [<kbd>Reserve</kbd>](https://github.com/fleet-sdk/docs/issues/new?title=Reservation:%20%5BEducational%5D%20Fleet-Tutorial%20%2B%20Bounties&body=%23%20Bounty%20Reservation%0A%0A%2A%2ATitle%3A%2A%2A%20%5BEducational%5D%20Fleet-Tutorial%20%2B%20Bounties%0A%2A%2ABounty%20Link%3A%2A%2A%20https%3A%2F%2Fgithub.com%2Ffleet-sdk%2Fdocs%2Fissues%2F8%0A%2A%2AValue%3A%2A%2A%20775%20SigUSD%0A%0A%23%23%20Developer%20Information%0A%0A%2A%2AGitHub%20Username%3A%2A%2A%20%5BYour%20GitHub%20Username%5D%0A%2A%2ADiscord%20Username%20(optional)%3A%2A%2A%20%5BYour%20Discord%20handle%20for%20any%20questions%5D%0A%0A%23%23%20Development%20Plan%0A%0APlease%20share%20a%20brief%20overview%20of%3A%0A%0A-%20Your%20approach%20to%20implementing%20this%20bounty%0A-%20Estimated%20timeframe%20for%20completion%0A-%20Any%20questions%20you%20have%20about%20the%20requirements%0A%0A%2A%2ANote%3A%2A%2A%20By%20submitting%20this%20reservation%2C%20you%20are%20committing%20to%20working%20on%20this%20bounty.%20If%20you%20later%20decide%20not%20to%20proceed%2C%20please%20close%20this%20issue%20so%20others%20can%20work%20on%20it.) |
<!-- END_ACTIVE_BOUNTIES_TABLE -->


## 📚 Educational Reward Program

The Educational Reward Program is designed to stimulate the creation of educational content that benefits the Ergo community. We believe in the power of knowledge-sharing and empowerment as key drivers of growth.

### Program Details

- **Focus Area**: Developer Tutorials and Guides
- **Eligibility**: Contributors of all skill levels
- **Reward**: Varies based on contribution quality and impact
- **Currency**: ERG

### How to Participate

If you have educational content, even if it's not explicitly mentioned here, it could still be eligible for a reward. We invite you to contribute any educational materials that can enrich learning experiences.

To claim a reward for your educational contribution:

1. **Complete your educational content**:
   - Create tutorials, guides, explainers, or other educational materials
   - Publish your content (on your blog, GitHub, YouTube, etc.)
   - Ensure it provides value to the Ergo community

2. **Submit a claim through this repository**:
   - Fork this repository
   - Create a new JSON file in the `submissions/` directory with the naming convention:
     ```
     {github_username}-educational-{descriptive-name}.json
     ```
   - Fill out the JSON file using the template below:
     ```json
     {
       "contributor": "your-github-username",
       "wallet_address": "your-ergo-wallet-address",
       "contact_method": "Discord: username#1234",
       "work_link": "https://link-to-your-educational-content",
       "work_title": "Title of Your Educational Content",
       "bounty_id": "program-edu",
       "original_issue_link": "https://github.com/ErgoDevs/Ergo-Bounties/blob/main/docs/ongoing-programs.md",
       "payment_currency": "ERG",
       "bounty_value": 0,
       "status": "awaiting-review",
       "submission_date": "YYYY-MM-DD",
       "description": "Detailed description of your educational content and its value to the Ergo community."
     }
     ```
   - Note: Leave the `bounty_value` as 0 - the reviewers will determine the appropriate reward based on the quality and impact of your contribution.
   - Submit a PR with the title: `[EDUCATIONAL] Title of Your Educational Content`

3. **Review Process**:
   - Maintainers will review your submission
   - They will evaluate the quality, depth, and impact of your educational content
   - If approved, they will assign a reward value and merge your PR
   - Payment will be processed based on the details in your JSON file

## 💻 Development Reward Program

The Development Reward Program acknowledges and appreciates significant contributions to the Ergo repositories. This program rewards developers who help improve and enhance the Ergo ecosystem through code contributions.

### Program Details

- **Focus Area**: Ergo repositories and ecosystem projects
- **Eligibility**: Contributors who make significant improvements
- **Reward**: Varies based on contribution impact
- **Currency**: ERG

### How to Participate

If your contributions have significantly enhanced the development and improvement of the Ergo ecosystem, you could be eligible for a reward.

To claim a reward for your development contribution:

1. **Complete your development work**:
   - Make significant contributions to Ergo repositories
   - Ensure your PR is merged in the target repository
   - Verify your work has a meaningful impact on the ecosystem

2. **Submit a claim through this repository**:
   - Fork this repository
   - Create a new JSON file in the `submissions/` directory with the naming convention:
     ```
     {github_username}-development-{descriptive-name}.json
     ```
   - Fill out the JSON file using the template below:
     ```json
     {
       "contributor": "your-github-username",
       "wallet_address": "your-ergo-wallet-address",
       "contact_method": "Discord: username#1234",
       "work_link": "https://github.com/ergoplatform/repo/pull/999",
       "work_title": "Title of Your Development Contribution",
       "bounty_id": "program-dev",
       "original_issue_link": "https://github.com/ErgoDevs/Ergo-Bounties/blob/main/docs/ongoing-programs.md",
       "payment_currency": "ERG",
       "bounty_value": 0,
       "status": "awaiting-review",
       "submission_date": "YYYY-MM-DD",
       "description": "Detailed description of your development contribution, its impact, and why it deserves a reward."
     }
     ```
   - Note: Leave the `bounty_value` as 0 - the reviewers will determine the appropriate reward based on the significance and impact of your contribution.
   - Submit a PR with the title: `[DEVELOPMENT] Title of Your Development Contribution`

3. **Review Process**:
   - Maintainers will review your submission
   - They will evaluate the significance and impact of your development contribution
   - If approved, they will assign a reward value and merge your PR
   - Payment will be processed based on the details in your JSON file

## Why Participate?

We deeply appreciate the time, dedication, and expertise you invest in enhancing our ecosystem. By participating in our mission to improve educational materials and drive development within the Ergo community, you are playing a crucial role in the collective growth and success of the platform.

These ongoing programs complement our specific bounties and provide additional avenues for contributors to be rewarded for their valuable work.
