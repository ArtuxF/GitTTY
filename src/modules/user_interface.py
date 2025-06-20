from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog, confirm
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import PathCompleter
import os
from modules.config_manager import get_default_clone_dir, set_default_clone_dir


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def display_welcome():
    """Displays a welcome message on the TTY."""
    print(
        f"{Colors.HEADER}--------------------------------------------------{Colors.ENDC}"
    )
    print(
        f"{Colors.HEADER}       Welcome to GitTTY - Your Git lifeline      {Colors.ENDC}"
    )
    print(
        f"{Colors.HEADER}--------------------------------------------------{Colors.ENDC}"
    )
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
            ("manual", "Enter the full URL manually"),
        ],
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
            ],
        ).run()

        if not base_url_key:
            return None

        base_urls = {
            "github_https": "https://github.com/",
            "github_ssh": "git@github.com:",
            "gitlab_https": "https://gitlab.com/",
            "gitlab_ssh": "git@gitlab.com:",
        }

        repo_path = get_user_input(
            f"Enter the repository path (e.g., owner/repo.git) for {base_urls[base_url_key]}"
        )
        if repo_path:
            return base_urls[base_url_key] + repo_path

    return None  # Return None if user cancels


def get_destination_path_interactively():
    """
    Asks for a destination path, offering a default and manual entry.
    If the path doesn't exist, it will be created by the clone operation.
    """
    # Get the default path from config
    default_path = get_default_clone_dir()

    # Options for the user
    values = [
        ("default", f"Use default path: '{default_path}'"),
        ("manual", "Enter a path manually"),
    ]

    choice = radiolist_dialog(
        title="Choose Destination Path",
        text="Where do you want to clone the repository?",
        values=values,
    ).run()

    destination_path = None
    if choice == "default":
        destination_path = default_path
    elif choice == "manual":
        completer = PathCompleter(expanduser=True)
        path_input = prompt(
            "Enter the destination path: ",
            completer=completer,
            complete_while_typing=True,
        )
        if path_input:
            destination_path = os.path.expanduser(path_input)

    if not destination_path:
        return None  # User cancelled or entered empty path

    # The git clone command will create the directory. We just need to confirm
    # if it already exists and is not empty.
    if confirm_destination(destination_path):
        return destination_path
    else:
        return None  # User chose not to proceed


def confirm_destination(path):
    """
    Checks if a destination path exists and provides appropriate warnings.
    Returns True to proceed, False to cancel.
    """
    if os.path.exists(path):
        if os.path.isdir(path) and os.listdir(path):
            print(
                f"{Colors.WARNING}Warning: The destination directory '{path}' already exists and is not empty.{Colors.ENDC}"
            )
            return confirm(
                "Do you want to attempt to clone into this directory anyway?"
            )
        elif os.path.isfile(path):
            print(
                f"{Colors.FAIL}Error: The destination path '{path}' exists and is a file. Please choose a different path.{Colors.ENDC}"
            )
            return False
    return True  # Path doesn't exist or is an empty dir, so proceed.


def get_branch_or_tag_interactively():
    """Asks the user if they want to specify a branch or tag."""
    if confirm("Do you want to specify a specific branch or tag to clone?"):
        branch = prompt("Enter the branch or tag name: ")
        return branch
    return None


def ask_for_shallow_clone():
    """Asks the user if they want to perform a shallow clone."""
    return confirm(
        "Do you want to perform a shallow clone? (Downloads only the latest version, faster for large repos)"
    )


def manage_settings():
    """Display the settings menu."""
    current_dir = get_default_clone_dir()
    print(f"\nCurrent default clone directory: {current_dir}")

    if confirm("Do you want to change the default clone directory?").run():
        new_dir = prompt(
            "Enter the new default clone directory: ",
            default=current_dir,
            completer=PathCompleter(),
        )
        if new_dir:
            set_default_clone_dir(os.path.expanduser(new_dir))
            print(f"Default clone directory updated to: {os.path.expanduser(new_dir)}")


def get_repo_action_interactively():
    """Asks the user what to do with a selected repository."""
    action = radiolist_dialog(
        title="Repository Action",
        text="What do you want to do with this repository?",
        values=[
            ("clone_update", "Clone or Update"),
            ("details", "View Details"),
            ("remove", "Remove from list"),
            ("back", "Go Back"),
        ],
    ).run()
    return action


def display_repo_details(repo):
    """Displays the details of a repository."""
    print("\n--- Repository Details ---")
    print(f"  Name: {repo.get('name', 'N/A')}")
    print(f"  URL: {repo.get('url', 'N/A')}")
    print(f"  Local Path: {repo.get('path', 'Not Cloned Yet')}")
    print("--------------------------")
    input("Press Enter to continue...")


def ask_to_stash_changes():
    """Asks the user if they want to stash local changes."""
    return confirm(
        "Local changes would be overwritten by pull. Do you want to stash them, pull, and then reapply?"
    ).run()
