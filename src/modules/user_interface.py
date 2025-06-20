from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog, confirm
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import PathCompleter
import os

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def display_welcome():
    """Displays a welcome message on the TTY."""
    print(f"{Colors.HEADER}--------------------------------------------------{Colors.ENDC}")
    print(f"{Colors.HEADER}       Welcome to GitTTY - Your Git lifeline      {Colors.ENDC}")
    print(f"{Colors.HEADER}--------------------------------------------------{Colors.ENDC}")
    print("Clone your essential repositories directly from the TTY.\n")

def get_user_input(prompt):
    """Gets text input from the user."""
    return input(f"{prompt}: ").strip()

def get_repo_url_interactively():
    """Asks the user to build or enter a repo URL interactively."""
    
    url_method = radiolist_dialog(
        title="Repository URL",
        text="How do you want to provide the repository URL?",
        values=[
            ("quick", "Build from a preset (e.g., GitHub)"),
            ("manual", "Enter the full URL manually")
        ]
    ).run()

    if url_method == "manual":
        return get_user_input("Enter the full Git repository URL (HTTPS or SSH)")
    
    elif url_method == "quick":
        base_url_key = radiolist_dialog(
            title="Select a Provider",
            text="Select the Git hosting provider:",
            values=[
                ("github_https", "GitHub (HTTPS)"),
                ("github_ssh", "GitHub (SSH)"),
                ("gitlab_https", "GitLab (HTTPS)"),
                ("gitlab_ssh", "GitLab (SSH)"),
            ]
        ).run()

        if not base_url_key:
            return None

        base_urls = {
            "github_https": "https://github.com/",
            "github_ssh": "git@github.com:",
            "gitlab_https": "https://gitlab.com/",
            "gitlab_ssh": "git@gitlab.com:",
        }

        repo_path = get_user_input(f"Enter the repository path (e.g., owner/repo.git) for {base_urls[base_url_key]}")
        if repo_path:
            return base_urls[base_url_key] + repo_path
    
    return None # Return None if user cancels

def get_destination_path_interactively():
    """Asks for a destination path with autocompletion."""
    completer = PathCompleter(expanduser=True)
    path = prompt(
        "Enter the destination path (e.g., /home/user/dotfiles): ",
        completer=completer,
        complete_while_typing=True
    )
    return os.path.expanduser(path) if path else None

def confirm_destination(path):
    """
    Checks if a destination path exists and provides appropriate warnings.
    Returns True to proceed, False to cancel.
    """
    if os.path.exists(path):
        if os.path.isdir(path) and os.listdir(path):
            print(f"{Colors.WARNING}Warning: The destination directory '{path}' already exists and is not empty.{Colors.ENDC}")
            return confirm("Do you want to attempt to clone into this directory anyway?")
        elif os.path.isfile(path):
             print(f"{Colors.FAIL}Error: The destination path '{path}' exists and is a file. Please choose a different path.{Colors.ENDC}")
             return False
    return True # Path doesn't exist or is an empty dir, so proceed.

def get_branch_or_tag_interactively():
    """Asks the user if they want to specify a branch or tag."""
    if confirm("Do you want to specify a specific branch or tag to clone?"):
        branch = prompt("Enter the branch or tag name: ")
        return branch
    return None

def ask_for_shallow_clone():
    """Asks the user if they want to perform a shallow clone."""
    return confirm("Do you want to perform a shallow clone? (Downloads only the latest version, faster for large repos)")
