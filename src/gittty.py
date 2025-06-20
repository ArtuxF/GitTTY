#!/usr/bin/env python3

import sys
import os
import argparse
from modules.user_interface import (
    display_welcome,
    get_user_input,
    get_repo_url_interactively,
    get_destination_path_interactively,
    confirm_destination,
    get_branch_or_tag_interactively,
    ask_for_shallow_clone,
    manage_settings,
)
from modules.git_operations import (
    clone_repository,
    execute_script_in_repo,
    check_git_installed,
    check_connectivity,
    pull_repository,
    get_repo_root,
)
from modules.config_manager import (
    load_frequent_repos,
    add_frequent_repo,
    remove_frequent_repo,
)


def manage_frequent_repos():
    """Handles the logic for managing frequent repositories."""
    while True:
        print("\n--- Manage Frequent Repositories ---")
        repos = load_frequent_repos()
        if not repos:
            print("No frequent repositories found.")
            return

        for i, repo in enumerate(repos):
            print(f"  {i + 1}: {repo['name']} ({repo['url']})")
        print("------------------------------------")

        choice = get_user_input(
            "Select a repo to remove (by number), or press Enter to go back"
        )
        if not choice:
            break

        if choice.isdigit():
            repo_index = int(choice) - 1
            if remove_frequent_repo(repo_index):
                print("Repository removed successfully.")
            else:
                print("Invalid number.")
        else:
            print("Invalid input.")


def run_interactive_mode():
    """Runs the main interactive loop of the application."""
    display_welcome()

    try:
        while True:
            print("\n--- Main Menu ---")
            print("1. Clone a new repository")
            print("2. Select from frequent repositories to clone")
            print("3. Manage frequent repositories")
            print("4. Update an existing repository")
            print("5. Settings")
            print("6. Update GitTTY")
            print("q. Quit")
            print("-------------------")

            choice = get_user_input("Select an option")
            repo_url = None

            if choice == "1":
                if not check_connectivity():
                    continue
                repo_url = get_repo_url_interactively()
            elif choice == "2":
                if not check_connectivity():
                    continue
                frequent_repos = load_frequent_repos()
                if frequent_repos:
                    print("\n--- Frequent Repositories ---")
                    for i, repo in enumerate(frequent_repos):
                        print(f"  {i + 1}: {repo['name']} ({repo['url']})")
                    print("-----------------------------")
                    repo_choice = get_user_input(
                        "Select a repo by number, or press Enter to go back"
                    )
                    if repo_choice.isdigit() and 1 <= int(repo_choice) <= len(
                        frequent_repos
                    ):
                        repo_url = frequent_repos[int(repo_choice) - 1]["url"]
                    elif repo_choice:
                        print("Invalid selection.")
                        continue
                else:
                    print("No frequent repositories found. Please add one first.")
                    continue
            elif choice == "3":
                manage_frequent_repos()
                continue
            elif choice == "4":
                if not check_connectivity():
                    continue

                frequent_repos = load_frequent_repos()
                updatable_repos = [
                    repo
                    for repo in frequent_repos
                    if repo.get("path") and os.path.exists(repo.get("path"))
                ]

                if not updatable_repos:
                    print(
                        "No updatable repositories found. Clone a repository and save it first."
                    )
                    continue

                print("\n--- Select a Repository to Update ---")
                for i, repo in enumerate(updatable_repos):
                    print(f"  {i + 1}: {repo['name']} ({repo['path']})")
                print("-------------------------------------")

                repo_choice = get_user_input(
                    "Select a repo by number, or press Enter to go back"
                )
                if repo_choice.isdigit() and 1 <= int(repo_choice) <= len(
                    updatable_repos
                ):
                    selected_repo = updatable_repos[int(repo_choice) - 1]
                    pull_repository(selected_repo["path"])
                elif repo_choice:
                    print("Invalid selection.")

                continue
            elif choice == "5":
                manage_settings()
                continue
            elif choice == "6":
                if not check_connectivity():
                    continue
                gittty_repo_path = get_repo_root()
                if gittty_repo_path:
                    print(f"Found GitTTY repository at: {gittty_repo_path}")
                    pull_repository(gittty_repo_path)
                    print(
                        "\nUpdate complete. If there were any changes, please restart the application."
                    )
                else:
                    print(
                        "Could not find the GitTTY repository. This command only works if you installed via 'git clone'."
                    )
                continue
            elif choice.lower() == "q":
                break
            else:
                print("Invalid option.")
                continue

            if not repo_url:
                continue

            destination_path = get_destination_path_interactively()
            if not destination_path:
                print("The destination path cannot be empty. Please try again.")
                continue

            branch_or_tag = get_branch_or_tag_interactively()
            shallow = ask_for_shallow_clone()

            if clone_repository(repo_url, destination_path, branch_or_tag, shallow):
                print("Operation completed.")

                repo_name_from_url = repo_url.split("/")[-1].replace(".git", "")
                cloned_repo_path = os.path.join(destination_path, repo_name_from_url)

                run_script_choice = get_user_input(
                    "Do you want to execute a script in the cloned repository? (y/n)"
                )
                if run_script_choice.lower() == "y":
                    script_path = get_user_input(
                        "Enter the relative path to the script (e.g., install.sh or scripts/setup.py)"
                    )
                    if script_path:
                        execute_script_in_repo(script_path, cloned_repo_path)

                save_choice = get_user_input(
                    "Do you want to add this repository to the frequent list? (y/n)"
                )
                if save_choice.lower() == "y":
                    repo_name = get_user_input(
                        "Enter a friendly name for this repository"
                    )
                    if not repo_name:
                        repo_name = repo_url
                    add_frequent_repo(
                        {"name": repo_name, "url": repo_url, "path": cloned_repo_path}
                    )
                    print("Repository saved to frequent list.")
            else:
                print("Cloning failed. Please check the URL and destination path.")

            another_op = get_user_input(
                "Do you want to perform another operation? (y/n)"
            )
            if another_op.lower() != "y":
                break

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user. Exiting gracefully.")
        sys.exit(0)

    print("\nThank you for using GitTTY! We hope we've helped you recover your system.")


def main():
    parser = argparse.ArgumentParser(
        description="GitTTY: Your Git lifeline in a TTY environment.",
        epilog="By default, GitTTY runs in an interactive mode with a menu-driven interface.",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.0"  # Simple versioning
    )

    # This check is minimal. If any args are passed that aren't the ones we define,
    # argparse will handle it (e.g., show help or an error).
    # We just want to run interactively if NO args are given.
    if len(sys.argv) == 1:
        if not check_git_installed():
            sys.exit(1)
        run_interactive_mode()
    else:
        # Let argparse handle the arguments (--help, --version, or errors)
        args = parser.parse_args()


if __name__ == "__main__":
    main()
