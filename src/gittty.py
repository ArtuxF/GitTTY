#!/usr/bin/env python3

import sys
import subprocess
import os

def display_welcome():
    """Displays a welcome message on the TTY."""
    print("--------------------------------------------------")
    print("       Welcome to GitTTY - Your Git lifeline      ")
    print("--------------------------------------------------")
    print("Clone your essential repositories directly from the TTY.\n")

def get_user_input(prompt):
    """Gets text input from the user."""
    return input(f"{prompt}: ").strip()

def clone_repository(repo_url, destination_path):
    """
    Executes the git clone command.
    Handles real-time output to show progress.
    """
    print(f"\nCloning '{repo_url}' into '{destination_path}'...")

    try:
        # Create the destination directory if it doesn't exist
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        # Git command. We assume destination_path is the *parent* of the repo.
        # The git clone command will create its own subdirectory.
        # For example: git clone repo.git /path/to/clone
        # This will create /path/to/clone/repo.
        command = ['git', 'clone', repo_url, destination_path]

        # Execute the command and capture the output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Display Git's output in real-time
        for line in process.stdout:
            print(line, end='')
        for line in process.stderr:
            print(line, end='')

        # Wait for the process to finish and get the return code
        process.wait()

        if process.returncode == 0:
            print("\nRepository cloned successfully!")
            return True
        else:
            print(f"\nError cloning the repository. Exit code: {process.returncode}")
            return False

    except FileNotFoundError:
        print("Error: The 'git' command was not found. Make sure Git is installed and in your PATH.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def main():
    display_welcome()

    while True:
        repo_url = get_user_input("Enter the Git repository URL (HTTPS or SSH), or 'q' to quit")
        if repo_url.lower() == 'q':
            break

        destination_path = get_user_input("Enter the destination path (e.g. /home/user/dotfiles)")

        if not destination_path:
            print("The destination path cannot be empty. Please try again.")
            continue

        # More robust validation could be added here (e.g., write permissions).

        if clone_repository(repo_url, destination_path):
            print("Operation completed. Do you want to clone another repository?")
        else:
            print("Cloning failed. Please check the URL and destination path. Do you want to try again?")

        choice = get_user_input("Enter 'y' for yes, anything else for no")
        if choice.lower() != 'y':
            break

    print("\nThank you for using GitTTY! We hope we've helped you recover your system.")

if __name__ == '__main__':
    main()