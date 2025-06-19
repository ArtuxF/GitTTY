import subprocess
import os

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
