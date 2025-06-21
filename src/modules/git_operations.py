import subprocess
import os
import shutil
import socket
import itertools
import threading
import time
import re

try:
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn
    from rich.console import Console
    from rich.live import Live
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

def parse_git_progress(line):
    """Parse git output to extract progress information."""
    # Pattern for git clone progress: "Receiving objects: 45% (450/1000), 2.3 MiB | 1.2 MiB/s"
    receiving_pattern = r"Receiving objects:\s*(\d+)%\s*\((\d+)/(\d+)\)(?:,\s*([\d.]+\s*[KMGT]?i?B)\s*\|\s*([\d.]+\s*[KMGT]?i?B/s))?"
    
    # Pattern for resolving deltas: "Resolving deltas: 67% (670/1000)"
    resolving_pattern = r"Resolving deltas:\s*(\d+)%\s*\((\d+)/(\d+)\)"
    
    # Pattern for compression/decompression
    compression_pattern = r"(Compressing|Decompressing) objects:\s*(\d+)%\s*\((\d+)/(\d+)\)"
    
    # Try to match receiving objects
    match = re.search(receiving_pattern, line)
    if match:
        percent = int(match.group(1))
        current = int(match.group(2))
        total = int(match.group(3))
        size = match.group(4) if match.group(4) else None
        speed = match.group(5) if match.group(5) else None
        return {
            'type': 'receiving',
            'percent': percent,
            'current': current,
            'total': total,
            'size': size,
            'speed': speed
        }
    
    # Try to match resolving deltas
    match = re.search(resolving_pattern, line)
    if match:
        percent = int(match.group(1))
        current = int(match.group(2))
        total = int(match.group(3))
        return {
            'type': 'resolving',
            'percent': percent,
            'current': current,
            'total': total
        }
    
    # Try to match compression
    match = re.search(compression_pattern, line)
    if match:
        operation = match.group(1).lower()
        percent = int(match.group(2))
        current = int(match.group(3))
        total = int(match.group(4))
        return {
            'type': operation,
            'percent': percent,
            'current': current,
            'total': total
        }
    
    return None

def advanced_progress_monitor(process, operation_name="Git Operation"):
    """Monitor git process with advanced progress bars using rich."""
    if not RICH_AVAILABLE:
        return spinner_animation_fallback(process, operation_name)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[bold green]{task.fields[speed]}"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False
    ) as progress:
        
        # Create initial task
        main_task = progress.add_task(f"[cyan]{operation_name}...", total=100, speed="")
        receiving_task = None
        resolving_task = None
        
        # Read process output in real-time
        while True:
            output = process.stderr.readline() if process.stderr else ""
            if output == "" and process.poll() is not None:
                break
            
            if output:
                # Parse the output for progress information
                progress_info = parse_git_progress(output.strip())
                
                if progress_info:
                    task_type = progress_info['type']
                    percent = progress_info['percent']
                    current = progress_info['current']
                    total = progress_info['total']
                    
                    if task_type == 'receiving':
                        if receiving_task is None:
                            receiving_task = progress.add_task(
                                "[green]Receiving objects", 
                                total=total, 
                                speed=progress_info.get('speed', '')
                            )
                        
                        progress.update(
                            receiving_task, 
                            completed=current, 
                            speed=progress_info.get('speed', '')
                        )
                        progress.update(main_task, completed=percent)
                        
                    elif task_type == 'resolving':
                        if resolving_task is None:
                            resolving_task = progress.add_task(
                                "[yellow]Resolving deltas", 
                                total=total,
                                speed=""
                            )
                        
                        progress.update(resolving_task, completed=current)
                        progress.update(main_task, completed=min(90 + (percent * 0.1), 100))
                    
                    elif task_type in ['compressing', 'decompressing']:
                        operation_display = task_type.title()
                        progress.update(
                            main_task, 
                            completed=percent,
                            description=f"[cyan]{operation_display} objects..."
                        )
                else:
                    # For lines without progress info, just show as activity
                    if "done" in output.lower() or "complete" in output.lower():
                        progress.update(main_task, completed=100)

def spinner_animation_fallback(process, operation_name):
    """Fallback spinner animation when rich is not available."""
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    while process.poll() is None:
        try:
            print(f"  {next(spinner)} {operation_name}...", end='\r', flush=True)
            time.sleep(0.1)
        except (BrokenPipeError, OSError):
            break
    print(' ' * 50, end='\r', flush=True)  # Clear the line


def spinner_animation(stop_event):
    """Displays a spinner animation in the console."""
    spinner = itertools.cycle(["-", "/", "|", "\\"])
    while not stop_event.is_set():
        try:
            print(f"  {next(spinner)} Processing...", end="\r", flush=True)
            time.sleep(0.1)
        except (BrokenPipeError, OSError):
            # Handle cases where stdout is closed or unavailable
            break
    # Clear the spinner line
    print(" " * 20, end="\r", flush=True)


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


def is_git_repo(path):
    """Check if the given path is a git repository."""
    return os.path.isdir(os.path.join(path, ".git"))


def clone_repository(repo_url, destination_path, branch_or_tag=None, shallow=False):
    """
    Executes the git clone command with advanced progress bars.
    """
    print(f"\nCloning '{repo_url}' into '{destination_path}'...")

    command = ["git", "clone", "--progress"]
    if branch_or_tag:
        command.extend(["--branch", branch_or_tag])
    if shallow:
        command.extend(["--depth", "1"])
    command.extend([repo_url, destination_path])

    try:
        # Execute the git command with real-time progress monitoring
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )

        # Monitor progress
        if RICH_AVAILABLE:
            advanced_progress_monitor(process, "Cloning repository")
        else:
            # Fallback to simple spinner in a thread
            stop_spinner = threading.Event()
            spinner_thread = threading.Thread(
                target=lambda: spinner_animation_fallback(process, "Cloning repository")
            )
            spinner_thread.start()
            
            # Wait for process to complete
            process.wait()
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join(timeout=1)

        # Get final output
        stdout, stderr = process.communicate() if process.poll() is None else ("", "")

        if process.returncode == 0:
            if RICH_AVAILABLE:
                console.print("✅ Repository cloned successfully!", style="bold green")
            else:
                print("\n✅ Repository cloned successfully!")
            return True
        else:
            if RICH_AVAILABLE:
                console.print("❌ Error cloning repository", style="bold red")
                console.print(translate_git_error(stderr))
            else:
                print("\n❌ Error cloning repository")
                print(translate_git_error(stderr))
            return False
            
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"❌ An unexpected error occurred: {e}", style="bold red")
        else:
            print(f"\n❌ An unexpected error occurred: {e}")
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
    """Executes git pull with advanced progress monitoring."""
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        error_msg = f"Error: '{repo_path}' is not a valid Git repository."
        if RICH_AVAILABLE:
            console.print(error_msg, style="bold red")
        else:
            print(error_msg)
        return False

    if RICH_AVAILABLE:
        console.print(f"📥 Pulling updates for [cyan]{repo_path}[/cyan]")
    else:
        print(f"\n--- Attempting to pull updates for {repo_path} ---")

    try:
        # First, check if there are uncommitted changes
        status_process = subprocess.Popen(
            ["git", "status", "--porcelain"], 
            cwd=repo_path, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        status_output, _ = status_process.communicate()
        
        has_changes = bool(status_output.strip())
        
        if has_changes:
            if RICH_AVAILABLE:
                console.print("⚠️  Uncommitted changes detected", style="yellow")
            
            # Import here to avoid circular imports
            from modules.user_interface import ask_to_stash_changes
            
            if ask_to_stash_changes():
                # Stash changes
                if RICH_AVAILABLE:
                    console.print("📦 Stashing local changes...", style="blue")
                else:
                    print("Stashing local changes...")
                
                stash_process = subprocess.Popen(
                    ["git", "stash", "push", "-m", "GitTTY auto-stash before pull"],
                    cwd=repo_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stash_process.wait()
                
                if stash_process.returncode != 0:
                    if RICH_AVAILABLE:
                        console.print("❌ Failed to stash changes", style="bold red")
                    else:
                        print("Failed to stash changes")
                    return False

        # Execute git pull with progress
        process = subprocess.Popen(
            ["git", "pull", "--progress"], 
            cwd=repo_path, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Monitor progress
        if RICH_AVAILABLE:
            advanced_progress_monitor(process, "Pulling updates")
        else:
            # Fallback to simple spinner
            spinner_thread = threading.Thread(
                target=lambda: spinner_animation_fallback(process, "Pulling updates")
            )
            spinner_thread.start()
            process.wait()
            if spinner_thread.is_alive():
                spinner_thread.join(timeout=1)

        stdout, stderr = process.communicate() if process.poll() is None else ("", "")

        if process.returncode == 0:
            # If we stashed changes, try to pop them back
            if has_changes and ask_to_stash_changes():
                if RICH_AVAILABLE:
                    console.print("📦 Restoring stashed changes...", style="blue")
                else:
                    print("Restoring stashed changes...")
                
                pop_process = subprocess.Popen(
                    ["git", "stash", "pop"],
                    cwd=repo_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                pop_process.wait()
                
                if pop_process.returncode != 0:
                    if RICH_AVAILABLE:
                        console.print("⚠️  Could not automatically restore stashed changes. Check 'git stash list'", style="yellow")
                    else:
                        print("Warning: Could not automatically restore stashed changes. Check 'git stash list'")

            if RICH_AVAILABLE:
                console.print("✅ Repository updated successfully!", style="bold green")
            else:
                print("✅ Repository updated successfully!")
            
            if stdout.strip():
                print(stdout.strip())
            return True
        else:
            if RICH_AVAILABLE:
                console.print("❌ Error pulling repository", style="bold red")
                console.print(translate_git_error(stderr))
            else:
                print("\n❌ Error pulling repository")
                print(translate_git_error(stderr))
            return False

    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"❌ An unexpected error occurred during git pull: {e}", style="bold red")
        else:
            print(f"An unexpected error occurred during git pull: {e}")
        return False


def get_repo_root():
    """Finds the root directory of the GitTTY repository."""
    try:
        # Start from the directory of the current script
        current_dir = os.path.dirname(os.path.realpath(__file__))
        # Go up until we find a .git directory
        while current_dir != "/":
            if os.path.isdir(os.path.join(current_dir, ".git")):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        return None  # Reached root without finding .git
    except Exception:
        # Fallback for environments where __file__ is not defined
        if os.path.isdir(os.path.join(os.getcwd(), ".git")):
            return os.getcwd()
        return None
