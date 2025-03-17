#!/bin/bash

# This script adds guardrail comments to Markdown files that are automatically generated

# Define the header and footer comments
HEADER='<!-- 
/** WARNING: AUTO-GENERATED FILE. DO NOT MODIFY DIRECTLY **/
/** Any changes made to this file will be overwritten by the automated system **/
/** Instead, update the generation scripts in .github/workflows/scripts/ **/
-->

'

FOOTER='

<!-- 
/** GENERATION END **/
/** Content above is automatically generated and will be overwritten **/
-->'

# List of all markdown files to update
FILES=(
  "README.md"
  "bounties/all.md"
  "bounties/currency_prices.md"
  "bounties/featured_bounties.md"
  "bounties/summary.md"
  $(find bounties/by_currency -name "*.md")
  $(find bounties/by_language -name "*.md")
  $(find bounties/by_org -name "*.md")
)

# Update each file
for file in "${FILES[@]}"; do
  echo "Processing $file..."
  
  # Skip if file doesn't exist
  if [ ! -f "$file" ]; then
    echo "  File not found, skipping."
    continue
  fi
  
  # Create a temporary file
  temp_file="${file}.temp"
  
  # Add header, copy original content, and add footer
  echo "$HEADER" > "$temp_file"
  cat "$file" >> "$temp_file"
  echo "$FOOTER" >> "$temp_file"
  
  # Replace original with new file
  mv "$temp_file" "$file"
  
  echo "  Added guardrails to $file"
done

echo "Done! Added guardrail comments to all generated Markdown files."
