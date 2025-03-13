# Contributing to Ergo Ecosystem Bounties

Thank you for your interest in contributing to the Ergo Ecosystem Bounties repository! This document provides guidelines and instructions for contributing to this project.

## 📋 Ways to Contribute

There are several ways you can contribute to the Ergo Ecosystem Bounties project:

1. **Complete Bounties**: Implement solutions for open bounties and submit your work
2. **Add Missing Bounties**: Help track bounties from other repositories
3. **Improve Documentation**: Enhance guides, READMEs, and other documentation
4. **Report Issues**: Report bugs or suggest improvements
5. **Review Submissions**: Help review bounty submissions (for maintainers)

## 🔍 Adding a Missing Bounty

If you know of a bounty that's not listed in our tracking system:

1. **Verify the Bounty Requirements**:
   - The issue should be in a GitHub repository
   - It should have a specified bounty value
   - It should be tagged with "Bounty" or similar

2. **Add the Repository to Tracking**:
   - Fork this repository
   - Edit the `tracked_repos.json` file to add the new repository
   - Format: `{"owner": "repo-owner", "repo": "repo-name"}`
   - Submit a PR with title: `[ADD REPO] owner/repo-name`

3. **For Manual Additions**:
   - If the bounty doesn't follow the standard format, create an issue in this repository
   - Use title format: `[MANUAL BOUNTY] Brief description`
   - Include: link to work, bounty value, and payment currency

## 🚀 Submitting a Bounty Claim

To submit a claim for a completed bounty:

1. **Complete the Work**: Implement the solution and submit a PR to the relevant repository
2. **Create a Submission File**:
   - Create a JSON file in the `submissions/` directory
   - Name format: `{github_username}-{descriptive-name}.json`
   - Use the [submission template](/templates/submission-template.json)
3. **Submit a PR**: Create a pull request to this repository with your submission file

For detailed instructions, see the [Submission Guide](/docs/submission-guide.md).

## 🔒 Reserving a Bounty

To prevent duplicate work, you can reserve a bounty before starting:

1. **Check Existing Reservations**: Review [open PRs](https://github.com/ErgoDevs/Ergo-Bounties/pulls)
2. **Create a Reservation**:
   - Follow the same process as submitting a claim, but:
   - Set `status` to `in-progress`
   - Leave `work_link` and `submission_date` empty
   - Include an `expected_completion` date
   - Use PR title format: `[WIP] Bounty repo#issue - Description`

## 📝 Pull Request Guidelines

When submitting a pull request:

1. **Use Clear Titles**: Begin with appropriate tag (`[WIP]`, `[READY]`, `[ADD REPO]`, etc.)
2. **Provide Context**: Include relevant information in the description
3. **Link Related Issues**: Reference any related issues or PRs
4. **Keep Changes Focused**: Each PR should address a single concern

## 🌟 Code of Conduct

- Be respectful and inclusive in all interactions
- Provide constructive feedback
- Follow through on commitments (especially for reservations)
- Communicate openly about delays or issues

## 🔄 Review Process

All submissions will be reviewed by maintainers who will:

1. Verify the work meets the bounty requirements
2. Check that the PR has been merged in the target repository
3. Confirm the bounty value matches what was advertised
4. Process payment upon approval

## 💬 Getting Help

If you have questions or need assistance:

- Open an issue in this repository
- Reach out on the [Ergo Discord server](https://discord.gg/ergo)
- Check the [Ergo Platform documentation](https://docs.ergoplatform.com/)

Thank you for contributing to the Ergo ecosystem!
