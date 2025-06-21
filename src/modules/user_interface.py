from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog, confirm
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import PathCompleter
import os
from modules.config_manager import get_default_clone_dir, set_default_clone_dir, get_theme, set_theme, load_frequent_repos
from modules.git_operations import is_git_repo, pull_repository
from modules.themes import get_theme as get_theme_object, get_available_themes, get_theme_preview

try:
    from fuzzywuzzy import fuzz, process
    FUZZY_SEARCH_AVAILABLE = True
except ImportError:
    FUZZY_SEARCH_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    RICH_UI_AVAILABLE = True
    ui_console = Console()
except ImportError:
    RICH_UI_AVAILABLE = False
    ui_console = None


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
    if RICH_UI_AVAILABLE:
        # Rich enhanced welcome
        title = Text("GitTTY - Your Git Lifeline", style="bold magenta")
        subtitle = Text("Clone your essential repositories directly from the TTY", style="italic cyan")
        
        welcome_panel = Panel(
            f"{title}\n{subtitle}",
            border_style="blue",
            padding=(1, 2)
        )
        ui_console.print(welcome_panel)
        ui_console.print()
    else:
        # Fallback to traditional display
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
        print("3. API integrations (GitHub/GitLab)")
        print("4. Back to main menu")
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
            manage_api_integrations()
        
        elif choice == "4":
            break
        
        else:
            print(f"{colors.WARNING}Invalid option. Please try again.{colors.ENDC}")


def manage_theme_settings():
    """Manage theme settings."""
    global colors  # Declare global at the beginning of the function
    
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


def search_frequent_repos():
    """Search through frequent repositories."""
    repos = load_frequent_repos()
    
    if not repos:
        print(f"{colors.WARNING}No frequent repositories found to search.{colors.ENDC}")
        input("Press Enter to continue...")
        return None
    
    print(f"\n{colors.HEADER}--- Search Repositories ---{colors.ENDC}")
    
    if not FUZZY_SEARCH_AVAILABLE:
        print(f"{colors.WARNING}Note: Advanced fuzzy search is not available. Install 'fuzzywuzzy' for better search results.{colors.ENDC}")
    
    search_query = input("Enter search term (name or URL): ").strip()
    
    if not search_query:
        print(f"{colors.WARNING}Search term cannot be empty.{colors.ENDC}")
        input("Press Enter to continue...")
        return None
    
    # Perform search
    matching_repos = []
    
    if FUZZY_SEARCH_AVAILABLE:
        # Use fuzzy matching for better results
        repo_strings = []
        for i, repo in enumerate(repos):
            search_string = f"{repo.get('name', '')} {repo.get('url', '')}"
            repo_strings.append((search_string, i))
        
        # Extract just the strings for fuzzy matching
        strings_only = [item[0] for item in repo_strings]
        
        # Get fuzzy matches (threshold of 60 for reasonable results)
        fuzzy_results = process.extract(search_query, strings_only, limit=len(strings_only))
        
        for match_string, score in fuzzy_results:
            if score >= 60:  # Minimum similarity threshold
                # Find the original repo index
                repo_index = next(i for string, i in repo_strings if string == match_string)
                matching_repos.append((repos[repo_index], score))
        
        # Sort by score (best matches first)
        matching_repos.sort(key=lambda x: x[1], reverse=True)
        matching_repos = [repo for repo, score in matching_repos]  # Remove scores for display
        
    else:
        # Simple string matching fallback
        search_lower = search_query.lower()
        for repo in repos:
            name = repo.get('name', '').lower()
            url = repo.get('url', '').lower()
            if search_lower in name or search_lower in url:
                matching_repos.append(repo)
    
    if not matching_repos:
        print(f"{colors.WARNING}No repositories found matching '{search_query}'.{colors.ENDC}")
        input("Press Enter to continue...")
        return None
    
    # Display results
    print(f"\n{colors.OKGREEN}Found {len(matching_repos)} matching repositories:{colors.ENDC}")
    for i, repo in enumerate(matching_repos, 1):
        path_info = f" -> {repo.get('path', 'Not cloned')}"
        print(f"  {i}. {colors.OKCYAN}{repo.get('name')}{colors.ENDC} ({repo.get('url')}){path_info}")
    
    print(f"  {len(matching_repos) + 1}. Back to search")
    print("-" * 50)
    
    try:
        choice = input("Select a repository by number: ").strip()
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(matching_repos):
                return matching_repos[choice_num - 1]
            elif choice_num == len(matching_repos) + 1:
                return None
            else:
                print(f"{colors.WARNING}Invalid selection.{colors.ENDC}")
                input("Press Enter to continue...")
                return None
        else:
            print(f"{colors.WARNING}Please enter a valid number.{colors.ENDC}")
            input("Press Enter to continue...")
            return None
    except ValueError:
        print(f"{colors.WARNING}Invalid input.{colors.ENDC}")
        input("Press Enter to continue...")
        return None

def browse_frequent_repos():
    """Browse and select from frequent repositories with search option."""
    while True:
        repos = load_frequent_repos()
        
        if not repos:
            print(f"{colors.WARNING}No frequent repositories found.{colors.ENDC}")
            input("Press Enter to continue...")
            return None
        
        print(f"\n{colors.HEADER}--- Frequent Repositories ---{colors.ENDC}")
        
        # Show all repositories
        for i, repo in enumerate(repos, 1):
            path_info = f" -> {repo.get('path', 'Not cloned')}"
            print(f"  {i}. {colors.OKCYAN}{repo.get('name')}{colors.ENDC} ({repo.get('url')}){path_info}")
        
        print(f"\n  {len(repos) + 1}. Search repositories")
        print(f"  {len(repos) + 2}. Back to main menu")
        print("-" * 50)
        
        choice = input("Select an option: ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(repos):
                return repos[choice_num - 1]
            elif choice_num == len(repos) + 1:
                # Search functionality
                selected_repo = search_frequent_repos()
                if selected_repo:
                    return selected_repo
                # If no repo selected from search, continue the loop
            elif choice_num == len(repos) + 2:
                return None
            else:
                print(f"{colors.WARNING}Invalid selection.{colors.ENDC}")
                input("Press Enter to continue...")
        else:
            print(f"{colors.WARNING}Please enter a valid number.{colors.ENDC}")
            input("Press Enter to continue...")


def manage_api_integrations():
    """Manage API integrations with GitHub and GitLab."""
    from modules.config_manager import get_api_tokens, set_api_token, remove_api_token, get_gitlab_url, set_gitlab_url
    
    while True:
        tokens = get_api_tokens()
        
        if RICH_UI_AVAILABLE:
            ui_console.print(f"\n[bold blue]--- API Integrations ---[/bold blue]")
        else:
            print(f"\n{colors.HEADER}--- API Integrations ---{colors.ENDC}")
        
        print("1. Configure GitHub token")
        print("2. Configure GitLab token")
        print("3. Set custom GitLab URL")
        print("4. Test connections")
        print("5. Browse online repositories")
        print("6. Remove API tokens")
        print("7. Back to settings")
        
        # Show current status
        if tokens:
            print(f"\n{colors.OKCYAN}Current integrations:{colors.ENDC}")
            if "github" in tokens:
                print(f"  ✅ GitHub: Connected")
            if "gitlab" in tokens:
                print(f"  ✅ GitLab: Connected")
        else:
            print(f"\n{colors.WARNING}No API tokens configured{colors.ENDC}")
        
        print("-" * 50)
        
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            configure_github_token()
        elif choice == "2":
            configure_gitlab_token()
        elif choice == "3":
            configure_gitlab_url()
        elif choice == "4":
            test_api_connections()
        elif choice == "5":
            browse_online_repositories()
        elif choice == "6":
            remove_api_tokens_menu()
        elif choice == "7":
            break
        else:
            print(f"{colors.WARNING}Invalid option. Please try again.{colors.ENDC}")
            input("Press Enter to continue...")


def configure_github_token():
    """Configure GitHub personal access token."""
    print(f"\n{colors.HEADER}--- GitHub Token Configuration ---{colors.ENDC}")
    print("To create a GitHub Personal Access Token:")
    print("1. Go to GitHub.com → Settings → Developer settings → Personal access tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Give it a name (e.g., 'GitTTY')")
    print("4. Select scopes: 'repo' (for private repos) or 'public_repo' (for public only)")
    print("5. Copy the generated token")
    print()
    
    token = input("Enter your GitHub Personal Access Token (or press Enter to cancel): ").strip()
    
    if not token:
        return
    
    # Test the token
    try:
        from modules.api_clients import test_token
        
        print("Testing connection...")
        success, message, user_info = test_token("github", token)
        
        if success:
            from modules.config_manager import set_api_token
            set_api_token("github", token)
            
            if RICH_UI_AVAILABLE:
                ui_console.print(f"✅ [green]GitHub token configured successfully![/green]")
                ui_console.print(f"Connected as: [cyan]{user_info.get('username', 'Unknown')}[/cyan]")
            else:
                print(f"{colors.OKGREEN}✅ GitHub token configured successfully!{colors.ENDC}")
                print(f"Connected as: {user_info.get('username', 'Unknown')}")
        else:
            if RICH_UI_AVAILABLE:
                ui_console.print(f"❌ [red]Token validation failed: {message}[/red]")
            else:
                print(f"{colors.FAIL}❌ Token validation failed: {message}{colors.ENDC}")
    
    except ImportError:
        print(f"{colors.WARNING}API client not available. Token saved but not validated.{colors.ENDC}")
        from modules.config_manager import set_api_token
        set_api_token("github", token)
    
    input("Press Enter to continue...")


def configure_gitlab_token():
    """Configure GitLab personal access token."""
    print(f"\n{colors.HEADER}--- GitLab Token Configuration ---{colors.ENDC}")
    print("To create a GitLab Personal Access Token:")
    print("1. Go to GitLab.com → User Settings → Access Tokens")
    print("2. Create a new token with name (e.g., 'GitTTY')")
    print("3. Select scopes: 'read_repository' and 'read_user'")
    print("4. Copy the generated token")
    print()
    
    token = input("Enter your GitLab Personal Access Token (or press Enter to cancel): ").strip()
    
    if not token:
        return
    
    # Test the token
    try:
        from modules.api_clients import test_token
        from modules.config_manager import get_gitlab_url
        
        gitlab_url = get_gitlab_url()
        print(f"Testing connection to {gitlab_url}...")
        success, message, user_info = test_token("gitlab", token, gitlab_url)
        
        if success:
            from modules.config_manager import set_api_token
            set_api_token("gitlab", token)
            
            if RICH_UI_AVAILABLE:
                ui_console.print(f"✅ [green]GitLab token configured successfully![/green]")
                ui_console.print(f"Connected as: [cyan]{user_info.get('username', 'Unknown')}[/cyan]")
            else:
                print(f"{colors.OKGREEN}✅ GitLab token configured successfully!{colors.ENDC}")
                print(f"Connected as: {user_info.get('username', 'Unknown')}")
        else:
            if RICH_UI_AVAILABLE:
                ui_console.print(f"❌ [red]Token validation failed: {message}[/red]")
            else:
                print(f"{colors.FAIL}❌ Token validation failed: {message}{colors.ENDC}")
    
    except ImportError:
        print(f"{colors.WARNING}API client not available. Token saved but not validated.{colors.ENDC}")
        from modules.config_manager import set_api_token
        set_api_token("gitlab", token)
    
    input("Press Enter to continue...")


def configure_gitlab_url():
    """Configure custom GitLab URL."""
    from modules.config_manager import get_gitlab_url, set_gitlab_url
    
    current_url = get_gitlab_url()
    print(f"\n{colors.HEADER}--- GitLab URL Configuration ---{colors.ENDC}")
    print(f"Current GitLab URL: {colors.OKCYAN}{current_url}{colors.ENDC}")
    print("This is useful for self-hosted GitLab instances.")
    print()
    
    new_url = input(f"Enter new GitLab URL (or press Enter to keep current): ").strip()
    
    if new_url:
        if not new_url.startswith(('http://', 'https://')):
            new_url = 'https://' + new_url
        
        set_gitlab_url(new_url)
        print(f"{colors.OKGREEN}GitLab URL updated to: {new_url}{colors.ENDC}")
    
    input("Press Enter to continue...")


def test_api_connections():
    """Test all configured API connections."""
    from modules.config_manager import get_api_tokens, get_gitlab_url
    
    tokens = get_api_tokens()
    
    if not tokens:
        print(f"{colors.WARNING}No API tokens configured.{colors.ENDC}")
        input("Press Enter to continue...")
        return
    
    print(f"\n{colors.HEADER}--- Testing API Connections ---{colors.ENDC}")
    
    try:
        from modules.api_clients import test_token
        
        for service, token in tokens.items():
            print(f"\nTesting {service.title()}...")
            
            if service == "gitlab":
                gitlab_url = get_gitlab_url()
                success, message, user_info = test_token(service, token, gitlab_url)
            else:
                success, message, user_info = test_token(service, token)
            
            if success:
                username = user_info.get('username', 'Unknown')
                print(f"  ✅ {service.title()}: Connected as {username}")
            else:
                print(f"  ❌ {service.title()}: {message}")
    
    except ImportError:
        print(f"{colors.WARNING}API client not available for testing.{colors.ENDC}")
    
    input("Press Enter to continue...")


def remove_api_tokens_menu():
    """Menu to remove API tokens."""
    from modules.config_manager import get_api_tokens, remove_api_token
    
    tokens = get_api_tokens()
    
    if not tokens:
        print(f"{colors.WARNING}No API tokens configured.{colors.ENDC}")
        input("Press Enter to continue...")
        return
    
    print(f"\n{colors.HEADER}--- Remove API Tokens ---{colors.ENDC}")
    services = list(tokens.keys())
    
    for i, service in enumerate(services, 1):
        print(f"  {i}. Remove {service.title()} token")
    
    print(f"  {len(services) + 1}. Cancel")
    print("-" * 30)
    
    choice = input("Select a token to remove: ").strip()
    
    if choice.isdigit():
        choice_num = int(choice)
        if 1 <= choice_num <= len(services):
            service = services[choice_num - 1]
            if remove_api_token(service):
                print(f"{colors.OKGREEN}{service.title()} token removed successfully.{colors.ENDC}")
            else:
                print(f"{colors.FAIL}Failed to remove {service} token.{colors.ENDC}")
        elif choice_num == len(services) + 1:
            return
        else:
            print(f"{colors.WARNING}Invalid selection.{colors.ENDC}")
    else:
        print(f"{colors.WARNING}Please enter a valid number.{colors.ENDC}")
    
    input("Press Enter to continue...")


def browse_online_repositories():
    """Browse repositories from connected API services."""
    from modules.config_manager import get_api_tokens, get_gitlab_url
    
    tokens = get_api_tokens()
    
    if not tokens:
        print(f"{colors.WARNING}No API tokens configured. Please configure at least one service first.{colors.ENDC}")
        print("Go to Settings → API integrations to set up GitHub or GitLab tokens.")
        input("Press Enter to continue...")
        return None
    
    print(f"\n{colors.HEADER}--- Browse Online Repositories ---{colors.ENDC}")
    services = list(tokens.keys())
    
    for i, service in enumerate(services, 1):
        print(f"  {i}. Browse {service.title()} repositories")
    
    print(f"  {len(services) + 1}. Back")
    print("-" * 40)
    
    choice = input("Select a service: ").strip()
    
    if choice.isdigit():
        choice_num = int(choice)
        if 1 <= choice_num <= len(services):
            service = services[choice_num - 1]
            token = tokens[service]
            
            try:
                from modules.api_clients import create_client
                
                if service == "gitlab":
                    client = create_client(service, token, get_gitlab_url())
                else:
                    client = create_client(service, token)
                
                return browse_service_repositories(client, service)
                
            except ImportError:
                print(f"{colors.WARNING}API client not available. Install 'requests' package.{colors.ENDC}")
                input("Press Enter to continue...")
                return None
            except Exception as e:
                print(f"{colors.FAIL}Error accessing {service}: {str(e)}{colors.ENDC}")
                input("Press Enter to continue...")
                return None
                
        elif choice_num == len(services) + 1:
            return None
        else:
            print(f"{colors.WARNING}Invalid selection.{colors.ENDC}")
            input("Press Enter to continue...")
            return None
    else:
        print(f"{colors.WARNING}Please enter a valid number.{colors.ENDC}")
        input("Press Enter to continue...")
        return None


def browse_service_repositories(client, service_name):
    """Browse repositories from a specific service."""
    try:
        print(f"\nFetching {service_name} repositories...")
        repos = client.get_repositories(per_page=20)
        
        if not repos:
            print(f"{colors.WARNING}No repositories found.{colors.ENDC}")
            input("Press Enter to continue...")
            return None
        
        while True:
            print(f"\n{colors.HEADER}--- {service_name.title()} Repositories ---{colors.ENDC}")
            
            for i, repo in enumerate(repos, 1):
                visibility = "🔒" if repo.get("private") else "🌐"
                language = f" [{repo.get('language', 'N/A')}]" if repo.get('language') else ""
                stars = f" ⭐{repo.get('stars', 0)}" if repo.get('stars') else ""
                
                print(f"  {i}. {visibility} {colors.OKCYAN}{repo['name']}{colors.ENDC}{language}{stars}")
                if repo.get('description'):
                    desc = repo['description'][:60] + "..." if len(repo['description']) > 60 else repo['description']
                    print(f"      {desc}")
            
            print(f"\n  {len(repos) + 1}. Load more repositories")
            print(f"  {len(repos) + 2}. Back")
            print("-" * 50)
            
            choice = input("Select a repository: ").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(repos):
                    selected_repo = repos[choice_num - 1]
                    result = handle_online_repository_selection(selected_repo, service_name)
                    if result:  # If user chose to clone
                        return result
                elif choice_num == len(repos) + 1:
                    # Load more repositories
                    try:
                        more_repos = client.get_repositories(per_page=20)
                        if more_repos:
                            repos.extend(more_repos)
                        else:
                            print(f"{colors.WARNING}No more repositories found.{colors.ENDC}")
                            input("Press Enter to continue...")
                    except Exception as e:
                        print(f"{colors.FAIL}Error loading more repositories: {str(e)}{colors.ENDC}")
                        input("Press Enter to continue...")
                elif choice_num == len(repos) + 2:
                    return None
                else:
                    print(f"{colors.WARNING}Invalid selection.{colors.ENDC}")
                    input("Press Enter to continue...")
            else:
                print(f"{colors.WARNING}Please enter a valid number.{colors.ENDC}")
                input("Press Enter to continue...")
    
    except Exception as e:
        print(f"{colors.FAIL}Error browsing repositories: {str(e)}{colors.ENDC}")
        input("Press Enter to continue...")
        return None


def handle_online_repository_selection(repo, service_name):
    """Handle actions for a selected online repository."""
    print(f"\n{colors.HEADER}--- Repository: {repo['name']} ---{colors.ENDC}")
    print(f"Description: {repo.get('description', 'No description')}")
    print(f"Language: {repo.get('language', 'N/A')}")
    print(f"Stars: {repo.get('stars', 0)}")
    print(f"Private: {'Yes' if repo.get('private') else 'No'}")
    print()
    print("1. Clone repository (HTTPS)")
    print("2. Clone repository (SSH)")
    print("3. Add to frequent repositories")
    print("4. View more details")
    print("5. Back")
    print("-" * 30)
    
    choice = input("Select an action: ").strip()
    
    if choice == "1":
        return repo['clone_url_https']
    elif choice == "2":
        return repo['clone_url_ssh']
    elif choice == "3":
        # Add to frequent repositories
        from modules.config_manager import add_frequent_repo
        
        friendly_name = input(f"Enter a friendly name for '{repo['name']}': ").strip()
        if not friendly_name:
            friendly_name = repo['name']
        
        clone_url = repo['clone_url_https']  # Default to HTTPS
        
        add_frequent_repo({
            "name": friendly_name,
            "url": clone_url,
            "path": None
        })
        
        print(f"{colors.OKGREEN}Repository added to frequent list!{colors.ENDC}")
        input("Press Enter to continue...")
    elif choice == "4":
        # Show more details
        print(f"\n{colors.HEADER}--- Detailed Information ---{colors.ENDC}")
        print(f"Full name: {repo.get('full_name', 'N/A')}")
        print(f"HTTPS Clone URL: {repo['clone_url_https']}")
        print(f"SSH Clone URL: {repo['clone_url_ssh']}")
        print(f"Default branch: {repo.get('default_branch', 'main')}")
        print(f"Last updated: {repo.get('updated_at', 'N/A')}")
        if repo.get('forks'):
            print(f"Forks: {repo['forks']}")
        
        input("Press Enter to continue...")
    elif choice == "5":
        return None
    else:
        print(f"{colors.WARNING}Invalid option.{colors.ENDC}")
        input("Press Enter to continue...")
    
    return None
