import os

CONFIG_DIR = os.path.expanduser("~/.config/gittty")
REPOS_FILE = os.path.join(CONFIG_DIR, "frequent_repos.txt")

def load_frequent_repos():
    """Reads the frequent repositories file and returns a list of URLs."""
    if not os.path.exists(REPOS_FILE):
        return []
    try:
        with open(REPOS_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except IOError:
        return []

def save_frequent_repo(url):
    """Adds a repository URL to the frequent list, avoiding duplicates."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    repos = load_frequent_repos()
    if url not in repos:
        with open(REPOS_FILE, 'a') as f:
            f.write(url + '\n')
