import os
import json
import shutil

CONFIG_DIR = os.path.expanduser("~/.config/gittty")
REPOS_FILE_JSON = os.path.join(CONFIG_DIR, "frequent_repos.json")
REPOS_FILE_TXT_OLD = os.path.join(CONFIG_DIR, "frequent_repos.txt")


def _migrate_from_txt_to_json():
    """Migrates the old .txt repo file to the new .json format."""
    print("Migrating frequent repositories to new format...")
    try:
        with open(REPOS_FILE_TXT_OLD, "r") as f:
            urls = [line.strip() for line in f if line.strip()]

        # Add 'path': None to maintain data structure consistency
        repos = [{"name": url, "url": url, "path": None} for url in urls]
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
        with open(REPOS_FILE_JSON, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(
            f"Warning: Could not read the frequent repositories file at '{REPOS_FILE_JSON}'."
        )
        print(f"It might be corrupted. Error: {e}")

        # Backup the corrupted file
        corrupted_backup_path = REPOS_FILE_JSON + ".bak"
        try:
            shutil.move(REPOS_FILE_JSON, corrupted_backup_path)
            print(
                f"The corrupted file has been backed up to '{corrupted_backup_path}'."
            )
        except IOError as move_error:
            print(f"Could not back up the corrupted file. Error: {move_error}")

        return []  # Return an empty list to allow the program to continue


def save_frequent_repos(repos):
    """Saves the list of repo dictionaries to the file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(REPOS_FILE_JSON, "w") as f:
        json.dump(repos, f, indent=4)


def add_frequent_repo(repo_to_add):
    """Adds a repository to the frequent list, or updates the path if it already exists."""
    repos = load_frequent_repos()
    # Check if a repo with the same URL already exists
    existing_repo = next(
        (repo for repo in repos if repo.get("url") == repo_to_add.get("url")), None
    )

    if existing_repo:
        # If it exists, update its path
        existing_repo["path"] = repo_to_add.get("path")
    else:
        # Otherwise, add the new repo
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
