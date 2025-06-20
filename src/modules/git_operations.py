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

def execute_script_in_repo(script_path, repo_path):
    """Executes a script within a given repository directory."""
    full_script_path = os.path.join(repo_path, script_path)

    if not os.path.exists(full_script_path):
        print(f"Error: Script '{full_script_path}' not found.")
        return False

    # Check for execute permissions
    if not os.access(full_script_path, os.X_OK):
        print(f"Warning: Script '{full_script_path}' does not have execute permissions.")
        choice = input("Attempt to add execute permissions and run? (y/n)")
        if choice.lower() == 'y':
            try:
                os.chmod(full_script_path, os.stat(full_script_path).st_mode | 0o111)
                print("Execute permissions added.")
            except OSError as e:
                print(f"Error setting execute permissions: {e}")
                return False
        else:
            return False

    print(f"\n--- Executing script: {full_script_path} ---")
    try:
        # Execute the script from within the repo directory
        process = subprocess.Popen(
            [full_script_path],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Real-time output
        for line in process.stdout:
            print(line, end='')
        for line in process.stderr:
            print(line, end='')

        process.wait()

        if process.returncode == 0:
            print("\n--- Script executed successfully! ---")
            return True
        else:
            print(f"\n--- Script finished with errors. Exit code: {process.returncode} ---")
            return False

    except Exception as e:
        print(f"An unexpected error occurred while executing the script: {e}")
        return False
