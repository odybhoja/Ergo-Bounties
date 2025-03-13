import requests

def get_org_repos(org, github_token):
    """
    Get all repositories for an organization.
    
    Args:
        org (str): Organization name
        github_token (str): GitHub API token
        
    Returns:
        list: List of repository objects
    """
    headers = {"Authorization": f"token {github_token}"}
    url = f"https://api.github.com/orgs/{org}/repos?per_page=100"
    all_repos = []
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching repositories for organization {org}: {response.status_code}")
            return []
            
        repos = response.json()
        all_repos.extend(repos)
        url = response.links.get('next', {}).get('url')
    
    return all_repos

def get_repo_languages(owner, repo, github_token):
    """
    Get languages used in a repository.
    
    Args:
        owner (str): Repository owner
        repo (str): Repository name
        github_token (str): GitHub API token
        
    Returns:
        list: List of languages
    """
    headers = {"Authorization": f"token {github_token}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        languages = response.json()
        # Sort languages by bytes of code and get top 2
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:2]
        return [lang[0] for lang in sorted_languages]
    return []

def get_issues(owner, repo, github_token, state='open'):
    """
    Get issues from a repository.
    
    Args:
        owner (str): Repository owner
        repo (str): Repository name
        github_token (str): GitHub API token
        state (str): Issue state (open, closed, all)
        
    Returns:
        list: List of issue objects
    """
    headers = {"Authorization": f"token {github_token}"}
    url = f'https://api.github.com/repos/{owner}/{repo}/issues?state={state}&per_page=100'
    all_issues = []
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching issues from {owner}/{repo}: {response.status_code}")
            return []
            
        issues = response.json()
        all_issues.extend(issues)
        url = response.links.get('next', {}).get('url')
    
    return all_issues
