#!/usr/bin/env python3

import sys
import os
from modules.user_interface import display_welcome, get_user_input
from modules.git_operations import clone_repository, execute_script_in_repo
from modules.config_manager import load_frequent_repos, add_frequent_repo, remove_frequent_repo

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
        
        choice = get_user_input("Select a repo to remove (by number), or press Enter to go back")
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


def main():
    display_welcome()

    while True:
        print("\n--- Main Menu ---")
        print("1. Clone a new repository")
        print("2. Select from frequent repositories")
        print("3. Manage frequent repositories")
        print("q. Quit")
        print("-------------------")
        
        choice = get_user_input("Select an option")

        if choice == '1':
            repo_url = get_user_input("Enter the Git repository URL (HTTPS or SSH)")
        elif choice == '2':
            repo_url = None
            frequent_repos = load_frequent_repos()
            if frequent_repos:
                print("\n--- Frequent Repositories ---")
                for i, repo in enumerate(frequent_repos):
                    print(f"  {i + 1}: {repo['name']} ({repo['url']})")
                print("-----------------------------")
                repo_choice = get_user_input("Select a repo by number, or press Enter to go back")
                if repo_choice.isdigit() and 1 <= int(repo_choice) <= len(frequent_repos):
                    repo_url = frequent_repos[int(repo_choice) - 1]['url']
                elif repo_choice:
                    print("Invalid selection.")
                    continue
            else:
                print("No frequent repositories found. Please add one first.")
                continue
        elif choice == '3':
            manage_frequent_repos()
            continue
        elif choice.lower() == 'q':
            break
        else:
            print("Invalid option.")
            continue

        if not repo_url:
            continue

        destination_path = get_user_input("Enter the destination path (e.g. /home/user/dotfiles)")

        if not destination_path:
            print("The destination path cannot be empty. Please try again.")
            continue

        if clone_repository(repo_url, destination_path):
            print("Operation completed.")
            
            # Get the actual path of the cloned repo
            repo_name_from_url = repo_url.split('/')[-1].replace('.git', '')
            cloned_repo_path = os.path.join(destination_path, repo_name_from_url)

            run_script_choice = get_user_input("Do you want to execute a script in the cloned repository? (y/n)")
            if run_script_choice.lower() == 'y':
                script_path = get_user_input("Enter the relative path to the script (e.g., install.sh or scripts/setup.py)")
                if script_path:
                    execute_script_in_repo(script_path, cloned_repo_path)

            save_choice = get_user_input("Do you want to add this repository to the frequent list? (y/n)")
            if save_choice.lower() == 'y':
                repo_name = get_user_input("Enter a friendly name for this repository")
                if not repo_name:
                    repo_name = repo_url # Default to URL if no name is given
                add_frequent_repo({'name': repo_name, 'url': repo_url})
                print("Repository saved to frequent list.")
        else:
            print("Cloning failed. Please check the URL and destination path.")

        another_op = get_user_input("Do you want to perform another operation? (y/n)")
        if another_op.lower() != 'y':
            break

    print("\nThank you for using GitTTY! We hope we've helped you recover your system.")

if __name__ == '__main__':
    main()