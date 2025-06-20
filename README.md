# GitTTY: Your Git Lifeline in a TTY

[![wakatime](https://wakatime.com/badge/user/ce729308-d968-4fab-8b9a-eb4bdc3ddb80/project/7b8ee217-db76-4db7-b6b4-c3e50c886664.svg)](https://wakatime.com/badge/user/ce729308-d968-4fab-8b9a-eb4bdc3ddb80/project/7b8ee217-db76-4db7-b6b4-c3e50c886664)
[![GitHub last commit](https://img.shields.io/github/last-commit/ArtuxF/GitTTY)](https://github.com/ArtuxF/GitTTY/commits/main)
[![GitHub Repo stars](https://img.shields.io/github/stars/ArtuxF/GitTTY)](https://github.com/ArtuxF/GitTTY/stargazers)
[![GitHub repo size](https://img.shields.io/github/repo-size/ArtuxF/GitTTY)](https://github.com/ArtuxF/GitTTY)
[![GitHub license](https://img.shields.io/github/license/ArtuxF/GitTTY)](https://github.com/ArtuxF/GitTTY/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/ArtuxF/GitTTY)](https://github.com/ArtuxF/GitTTY/issues)

GitTTY is a robust and user-friendly TTY tool designed for emergency situations where you only have access to a command-line interface. It allows you to quickly clone, update, and manage your essential Git repositories (like dotfiles or configuration scripts) with ease.

![banner](https://github.com/user-attachments/assets/f4e06510-9898-4cce-acf0-4cc05c8b6807)


## Core Features

*   **Interactive Menus**: A simple, menu-driven interface that guides you through every operation.
*   **Smart URL Builder**: No need to type full URLs. Quickly build links for GitHub or GitLab (both HTTPS and SSH).
*   **Configurable Default Directory**: Set and customize your default cloning directory through the Settings menu.
*   **Frequent Repositories Management**: Save your most-used repositories with friendly names and manage them with detailed actions:
    *   Clone or Update repositories
    *   View detailed repository information (URL, local path, etc.)
    *   Remove repositories from your frequent list
*   **Smart Repository Detection**: Automatically detects if a destination directory is already a Git repository and offers to pull updates instead of cloning.
*   **Visual Progress Indicators**: Spinner animations during long-running operations like cloning and pulling to provide real-time feedback.
*   **Auto-Stash Integration**: When pulling updates, if local changes would be overwritten, GitTTY offers to automatically stash changes, pull, and reapply them.
*   **Self-Update**: Update GitTTY to the latest version directly from the main menu.
*   **Post-Clone Script Execution**: Automatically run an installation or setup script right after cloning.
*   **Branch & Tag Selection**: Choose a specific branch or tag to clone.
*   **Shallow Clone Support**: Option to perform a shallow clone (`--depth 1`) to save time and disk space.
*   **User-Friendly Error Messages**: Translates common Git errors into clear, understandable advice.
*   **Robustness**: Includes checks for internet connectivity, Git installation, and handles corrupted configuration files gracefully.
*   **Command-Line Flags**: Use `-h`/`--help` for usage information and `--version` to check the version.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/ArtuxF/GitTTY.git
    cd GitTTY
    ```

2.  **Set up a virtual environment** (recommended):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate 
    # For Fish shell: source .venv/bin/activate.fish
    ```

3.  **Install the package**:
    ```bash
    pip install .
    ```
    This will also install the required `prompt-toolkit` dependency and make the `gittty` command available in your environment.

## Usage

Once installed, simply run the command:

```bash
gittty
```

This will launch the interactive main menu.

### Non-Interactive Use

You can also use flags for quick help or version checking:

*   **Show help message**: `gittty -h` or `gittty --help`
*   **Show version**: `gittty --version`

## How It Works

GitTTY is built with a modular architecture in Python:

*   `gittty.py`: The main entry point, handling command-line arguments and the interactive menu logic.
*   `modules/user_interface.py`: Manages all user interaction, including menus, prompts, and confirmations using `prompt-toolkit`. Provides visual feedback and repository management dialogs.
*   `modules/git_operations.py`: Handles all Git commands (`clone`, `pull`, `stash`) with visual progress indicators and provides user-friendly error translation.
*   `modules/config_manager.py`: Manages both frequent repositories and user settings (like default clone directory), storing them in `~/.config/gittty/` as JSON files.

### New in Recent Updates

*   **Enhanced Repository Management**: Detailed view and management options for frequent repositories
*   **Smart Conflict Resolution**: Automatic stash/unstash workflow for handling local changes during pulls
*   **Visual Feedback**: Real-time progress indicators during Git operations
*   **Flexible Configuration**: Customizable default clone directory through the Settings menu
*   **Intelligent Directory Handling**: Automatic detection of existing Git repositories with pull suggestions

This structure makes the tool easy to maintain and extend while providing a smooth user experience even in emergency TTY-only scenarios.
