#!/usr/bin/env python3

import sys
from modules.user_interface import display_welcome, get_user_input
from modules.git_operations import clone_repository
from modules.config_manager import load_frequent_repos, save_frequent_repo

def main():
    display_welcome()

    while True:
        repo_url = None
        frequent_repos = load_frequent_repos()
        if frequent_repos:
            print("Frequent repositories found.")
            choice = get_user_input("Show frequent repositories? (y/n)")
            if choice.lower() == 'y':
                print("\n--- Frequent Repositories ---")
                for i, repo in enumerate(frequent_repos):
                    print(f"  {i + 1}: {repo}")
                print("-----------------------------")
                repo_choice = get_user_input("Select a repo by number, or press Enter to specify a new one")
                if repo_choice.isdigit() and 1 <= int(repo_choice) <= len(frequent_repos):
                    repo_url = frequent_repos[int(repo_choice) - 1]

        if not repo_url:
            repo_url = get_user_input("Enter the Git repository URL (HTTPS or SSH), or 'q' to quit")
            if repo_url.lower() == 'q':
                break

        destination_path = get_user_input("Enter the destination path (e.g. /home/user/dotfiles)")

        if not destination_path:
            print("The destination path cannot be empty. Please try again.")
            continue

        if clone_repository(repo_url, destination_path):
            print("Operation completed. Do you want to clone another repository?")
            save_frequent_repo(repo_url)
        else:
            print("Cloning failed. Please check the URL and destination path. Do you want to try again?")

        choice = get_user_input("Enter 'y' for yes, anything else for no")
        if choice.lower() != 'y':
            break

    print("\nThank you for using GitTTY! We hope we've helped you recover your system.")

if __name__ == '__main__':
    main()