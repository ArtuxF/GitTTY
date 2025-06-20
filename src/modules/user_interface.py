from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog, confirm
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import PathCompleter
import os
from modules.config_manager import get_default_clone_dir, set_default_clone_dir, get_theme, set_theme
from modules.git_operations import is_git_repo, pull_repository
from modules.themes import get_theme as get_theme_object, get_available_themes, get_theme_preview


class Colors:
    """Dynamic color class that loads colors from the current theme."""
    
    @staticmethod
    def _get_current_theme():
        """Get the current theme object."""
        theme_name = get_theme()
        return get_theme_object(theme_name)
    
    @property
    def HEADER(self):
        return self._get_current_theme().get_color("header")
    
    @property
    def OKBLUE(self):
        return self._get_current_theme().get_color("info")
    
    @property
    def OKCYAN(self):
        return self._get_current_theme().get_color("cyan")
    
    @property
    def OKGREEN(self):
        return self._get_current_theme().get_color("success")
    
    @property
    def WARNING(self):
        return self._get_current_theme().get_color("warning")
    
    @property
    def FAIL(self):
        return self._get_current_theme().get_color("error")
    
    @property
    def ENDC(self):
        return self._get_current_theme().get_color("reset")
    
    @property
    def BOLD(self):
        return self._get_current_theme().get_color("bold")
    
    @property
    def UNDERLINE(self):
        return self._get_current_theme().get_color("underline")


# Create a global instance
colors = Colors()


def display_welcome():
    """Displays a welcome message on the TTY."""
    print(
        f"{colors.HEADER}--------------------------------------------------{colors.ENDC}"
    )
    print(
        f"{colors.HEADER}       Welcome to GitTTY - Your Git lifeline      {colors.ENDC}"
    )
    print(
        f"{colors.HEADER}--------------------------------------------------{colors.ENDC}"
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
    Returns 'clone', 'pull', or None.
    """
    if os.path.exists(path):
        if os.path.isdir(path) and os.listdir(path):
            if is_git_repo(path):
                print(
                    f"{colors.OKCYAN}The destination '{path}' is already a Git repository.{colors.ENDC}"
                )
                if confirm("Do you want to pull the latest changes instead?").run():
                    return "pull"
                else:
                    return None  # User chose not to pull
            else:
                print(
                    f"{colors.WARNING}Warning: The destination directory '{path}' already exists and is not empty.{colors.ENDC}"
                )
                if confirm(
                    "Do you want to attempt to clone into this directory anyway?"
                ).run():
                    return "clone"  # User chose to proceed with cloning
                else:
                    return None  # User chose not to proceed
        elif os.path.isfile(path):
            print(
                f"{colors.FAIL}Error: The destination path '{path}' exists and is a file. Please choose a different path.{colors.ENDC}"
            )
            return None
    return "clone"  # Path doesn't exist or is an empty dir, so proceed with clone.


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
    while True:
        print(f"\n{colors.HEADER}--- Settings ---{colors.ENDC}")
        print("1. Change default clone directory")
        print("2. Change theme")
        print("3. Back to main menu")
        print("-------------------")
        
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            current_dir = get_default_clone_dir()
            print(f"\nCurrent default clone directory: {colors.OKCYAN}{current_dir}{colors.ENDC}")
            
            if confirm("Do you want to change the default clone directory?").run():
                new_dir = prompt(
                    "Enter the new default clone directory: ",
                    default=current_dir,
                    completer=PathCompleter(),
                )
                if new_dir:
                    set_default_clone_dir(os.path.expanduser(new_dir))
                    print(f"{colors.OKGREEN}Default clone directory updated to: {os.path.expanduser(new_dir)}{colors.ENDC}")
        
        elif choice == "2":
            manage_theme_settings()
        
        elif choice == "3":
            break
        
        else:
            print(f"{colors.WARNING}Invalid option. Please try again.{colors.ENDC}")


def manage_theme_settings():
    """Manage theme settings."""
    current_theme = get_theme()
    available_themes = get_available_themes()
    
    print(f"\n{colors.HEADER}--- Theme Settings ---{colors.ENDC}")
    print(f"Current theme: {colors.OKCYAN}{current_theme}{colors.ENDC}")
    print("\nAvailable themes:")
    
    # Show theme previews
    for i, theme_name in enumerate(available_themes, 1):
        preview = get_theme_preview(theme_name)
        current_marker = " (current)" if theme_name == current_theme else ""
        print(f"  {i}. {theme_name.title()}{current_marker}: {preview}")
    
    print(f"  {len(available_themes) + 1}. Back")
    print("-" * 50)
    
    try:
        choice = input("Select a theme by number: ").strip()
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(available_themes):
                selected_theme = available_themes[choice_num - 1]
                if selected_theme != current_theme:
                    set_theme(selected_theme)
                    print(f"{colors.OKGREEN}Theme changed to '{selected_theme}'. Changes will take effect immediately.{colors.ENDC}")
                    # Force reload colors by creating a new instance
                    global colors
                    colors = Colors()
                else:
                    print(f"{colors.WARNING}Theme '{selected_theme}' is already selected.{colors.ENDC}")
            elif choice_num == len(available_themes) + 1:
                return
            else:
                print(f"{colors.WARNING}Invalid selection.{colors.ENDC}")
        else:
            print(f"{colors.WARNING}Please enter a valid number.{colors.ENDC}")
    except ValueError:
        print(f"{colors.WARNING}Invalid input.{colors.ENDC}")
    
    input("Press Enter to continue...")


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
