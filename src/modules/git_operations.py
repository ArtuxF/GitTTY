import subprocess
import os
import shutil
import socket


def translate_git_error(stderr):
    """
    Translates common Git error messages into more user-friendly explanations and suggestions.
    """
    stderr_lower = stderr.lower()  # Case-insensitive matching

    if "repository not found" in stderr_lower:
        return (
            "Error: Repository not found.\n"
            "Suggestion: Double-check the URL for typos. If it's a private repository, ensure you have the necessary permissions."
        )
    if "authentication failed" in stderr_lower:
        return (
            "Error: Authentication failed.\n"
            "Suggestion: For HTTPS, check your username and password (or personal access token). For SSH, ensure your SSH key is correctly set up."
        )
    if "permission denied (publickey)" in stderr_lower:
        return (
            "Error: SSH Permission Denied.\n"
            "Suggestion: Verify that your SSH key is added to your SSH agent and registered with your Git provider (e.g., GitHub, GitLab)."
        )
    if "could not resolve host" in stderr_lower:
        return (
            "Error: Could not resolve host.\n"
            "Suggestion: Check your internet connection and DNS settings. Try to ping the host."
        )
    if (
        "your local changes to the following files would be overwritten by merge"
        in stderr_lower
    ):
        return (
            "Error: Local changes would be overwritten by pull.\n"
            "Suggestion: Stash or commit your local changes before pulling the updates. You can use 'git stash' to save them temporarily."
        )
    if "not a git repository" in stderr_lower:
        return (
            "Error: Not a Git repository.\n"
            "Suggestion: Make sure you are in the correct directory that contains the .git folder."
        )
    if "already exists and is not an empty directory" in stderr_lower:
        return (
            "Error: Destination path already exists and is not empty.\n"
            "Suggestion: Please choose a different directory or remove the existing one if it's not needed."
        )

    # Default fallback message
    return f"An unexpected Git error occurred. Raw error:\n---\n{stderr.strip()}\n---"


def check_connectivity(host="8.8.8.8", port=53, timeout=3):
    """
    Check for internet connectivity by trying to connect to a known host.
    Returns True if connection is successful, False otherwise.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print("Error: No internet connection detected.")
        return False


def check_git_installed():
    """Checks if Git is installed and available in the system's PATH."""
    if not shutil.which("git"):
        print(
            "Error: The 'git' command was not found. Please make sure Git is installed and in your PATH."
        )
        return False
    return True


def clone_repository(repo_url, destination_path, branch_or_tag=None, shallow=False):
    """
    Executes the git clone command.
    Handles real-time output to show progress.
    """
    print(f"\nCloning '{repo_url}' into '{destination_path}'...")
    print("Please wait, output will be shown after the command completes...")

    try:
        # The git clone command will create the destination directory.
        # We've already checked for existence and permissions in the main script.
        command = ["git", "clone"]

        # If a branch or tag is specified, append it to the command
        if branch_or_tag:
            command.extend(["--branch", branch_or_tag])

        # If shallow clone is requested, add the depth flag
        if shallow:
            command.extend(["--depth", "1"])

        command.extend([repo_url, destination_path])

        # Execute the command and capture the output
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Use communicate() to safely read all output and avoid deadlocks
        stdout, stderr = process.communicate()

        # Display Git's output. Clone progress is usually on stderr.
        if stderr:
            # Don't print progress bars, just the final status
            final_stderr = "\n".join(
                [
                    line
                    for line in stderr.splitlines()
                    if not line.startswith("Receiving objects")
                    and not line.startswith("Resolving deltas")
                ]
            )
            print(final_stderr.strip())
        if stdout:
            print(stdout, end="")

        if process.returncode == 0:
            print("\nRepository cloned successfully!")
            return True
        else:
            print("\n--- Error Cloning Repository ---")
            print(translate_git_error(stderr))
            return False

    except FileNotFoundError:
        print(
            "Error: The 'git' command was not found. Make sure Git is installed and in your PATH."
        )
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
        print(
            f"Warning: Script '{full_script_path}' does not have execute permissions."
        )
        choice = input("Attempt to add execute permissions and run? (y/n)")
        if choice.lower() == "y":
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
            text=True,
        )

        # Real-time output
        for line in process.stdout:
            print(line, end="")
        for line in process.stderr:
            print(line, end="")

        process.wait()

        if process.returncode == 0:
            print("\n--- Script executed successfully! ---")
            return True
        else:
            print(
                f"\n--- Script finished with errors. Exit code: {process.returncode} ---"
            )
            return False

    except Exception as e:
        print(f"An unexpected error occurred while executing the script: {e}")
        return False


def pull_repository(repo_path):
    """Executes git pull in a given repository directory."""
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        print(f"Error: '{repo_path}' is not a valid Git repository.")
        return False

    print(f"\n--- Attempting to pull updates for {repo_path} ---")
    print("Please wait, output will be shown after the command completes...")
    try:
        process = subprocess.Popen(
            ["git", "pull"],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Use communicate() to safely read all output and avoid deadlocks
        stdout, stderr = process.communicate()

        if stderr:
            print(stderr, end="")
        if stdout:
            print(stdout, end="")

        if process.returncode == 0:
            print("\n--- Repository updated successfully! ---")
            return True
        else:
            print("\n--- Error Pulling Repository ---")
            print(translate_git_error(stderr))
            return False

    except Exception as e:
        print(f"An unexpected error occurred during git pull: {e}")
        return False
