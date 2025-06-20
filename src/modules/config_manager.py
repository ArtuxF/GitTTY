import os
import json

CONFIG_DIR = os.path.expanduser("~/.config/gittty")
REPOS_FILE_JSON = os.path.join(CONFIG_DIR, "frequent_repos.json")
REPOS_FILE_TXT_OLD = os.path.join(CONFIG_DIR, "frequent_repos.txt")

def _migrate_from_txt_to_json():
    """Migrates the old .txt repo file to the new .json format."""
    print("Migrating frequent repositories to new format...")
    try:
        with open(REPOS_FILE_TXT_OLD, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        repos = [{'name': url, 'url': url} for url in urls]
        save_frequent_repos(repos)
        os.remove(REPOS_FILE_TXT_OLD)
        print("Migration successful.")
        return repos
    except (IOError, FileNotFoundError):
        # Old file didn't exist, nothing to migrate
        return []

def load_frequent_repos():
    """Reads the frequent repositories file and returns a list of repo dictionaries."""
    if not os.path.exists(REPOS_FILE_JSON):
        if os.path.exists(REPOS_FILE_TXT_OLD):
            return _migrate_from_txt_to_json()
        return []
    try:
        with open(REPOS_FILE_JSON, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return []

def save_frequent_repos(repos):
    """Saves the list of repo dictionaries to the file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(REPOS_FILE_JSON, 'w') as f:
        json.dump(repos, f, indent=4)

def add_frequent_repo(repo_to_add):
    """Adds a repository to the frequent list, avoiding duplicate URLs."""
    repos = load_frequent_repos()
    # Check if a repo with the same URL already exists
    if not any(repo['url'] == repo_to_add['url'] for repo in repos):
        repos.append(repo_to_add)
        save_frequent_repos(repos)

def remove_frequent_repo(index):
    """Removes a repository from the frequent list by its index (0-based)."""
    repos = load_frequent_repos()
    if 0 <= index < len(repos):
        del repos[index]
        save_frequent_repos(repos)
        return True
    return False
