# Bounty Submissions

This directory contains all bounty submissions for the Ergo ecosystem. Each submission is a JSON file that follows a specific format and naming convention.

## Submission Process

1. Complete the work for a bounty or contribution to the Ergo ecosystem
2. Submit a PR to the relevant repository with your implementation
3. Create a JSON file in this directory named `{github_username}-{descriptive-name}.json` (e.g., `user123-ergoscript-fsmtest.json`)
4. Fill out the JSON file using the [submission template](../templates/submission-template.json)
5. Submit a PR to this repository with your JSON file
6. Wait for review and approval

## JSON File Format

Each submission must include the following required fields:

- `contributor`: Your GitHub username
- `wallet_address`: The address where payment should be sent
- `work_link`: Link to the PR where the work was completed
- `work_title`: A short title describing the work
- `payment_currency`: Currency for payment (e.g., ERG, SigUSD, RSN)
- `bounty_value`: The payment amount (numeric value)
- `status`: Current submission status (`awaiting-review`, `approved`, `paid`)
- `submission_date`: Date of submission

Additional recommended fields:

- `bounty_id`: The GitHub issue number in `{repo}#{issue_number}` format (if applicable)
- `contact_method`: A way for reviewers to reach out if they have questions
- `original_issue_link`: The full URL to the original issue or bounty
- `description`: A brief summary of the work completed

The following fields will be filled out by reviewers:

- `review_notes`: Notes from the reviewer
- `payment_tx_id`: Transaction ID of the payment
- `payment_date`: Date when payment was processed

## Example

See the [submission template](../templates/submission-template.json) for a complete example.

## Review Process

1. Maintainers will review your submission
2. If approved, the PR will be merged
3. Payment will be processed based on the JSON details
4. The status will be updated to `paid` once payment is complete

For more detailed instructions, see the [submission guide](../docs/submission-guide.md).
