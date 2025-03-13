import json
import os
import sys

# Get the absolute path to the repository root
repo_root = "/Users/m/Documents/GitHub/Ergo-Bounties"

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Repository root:", repo_root)

repos_path = os.path.join(repo_root, "bounties/tracked_repos.json")
orgs_path = os.path.join(repo_root, "bounties/tracked_orgs.json")

print("\nChecking if files exist:")
print(f"  {repos_path} exists: {os.path.exists(repos_path)}")
print(f"  {orgs_path} exists: {os.path.exists(orgs_path)}")

try:
    print("\nReading tracked_repos.json...")
    with open(repos_path, "r") as f:
        repos = json.load(f)
        print(repos)

    print("\nReading tracked_orgs.json...")
    with open(orgs_path, "r") as f:
        orgs = json.load(f)
        print(orgs)
except Exception as e:
    print(f"Error: {e}")
