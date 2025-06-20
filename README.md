# GitTTY: Your Git Lifeline in a TTY

[![wakatime](https://wakatime.com/badge/user/ce729308-d968-4fab-8b9a-eb4bdc3ddb80/project/7b8ee217-db76-4db7-b6b4-c3e50c886664.svg)](https://wakatime.com/badge/user/ce729308-d968-4fab-8b9a-eb4bdc3ddb80/project/7b8ee217-db76-4db7-b6b4-c3e50c886664)

GitTTY is a robust and user-friendly TTY tool designed for emergency situations where you only have access to a command-line interface. It allows you to quickly clone, update, and manage your essential Git repositories (like dotfiles or configuration scripts) with ease.

![GitTTY Demo](https://user-images.githubusercontent.com/12345/67890.gif) 
*(Replace with your actual Asciinema GIF/screenshot)*

## Core Features

*   **Interactive Menus**: A simple, menu-driven interface that guides you through every operation.
*   **Smart URL Builder**: No need to type full URLs. Quickly build links for GitHub or GitLab (both HTTPS and SSH).
*   **Frequent Repositories**: Save your most-used repositories with friendly names for quick access later.
*   **Update Existing Repos**: Pull the latest changes for any repository you've previously cloned and saved.
*   **Post-Clone Script Execution**: Automatically run an installation or setup script right after cloning.
*   **Branch & Tag Selection**: Choose a specific branch or tag to clone.
*   **Shallow Clone Support**: Option to perform a shallow clone (`--depth 1`) to save time and disk space.
*   **User-Friendly Error Messages**: Translates common Git errors into clear, understandable advice.
*   **Robustness**: Includes checks for internet connectivity, Git installation, and handles corrupted configuration files gracefully.
*   **Command-Line Flags**: Use `-h`/`--help` for usage information and `--version` to check the version.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/GitTTY.git
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
*   `modules/user_interface.py`: Manages all user interaction, including menus, prompts, and confirmations using `prompt-toolkit`.
*   `modules/git_operations.py`: Handles all Git commands (`clone`, `pull`) and provides user-friendly error translation.
*   `modules/config_manager.py`: Manages the list of frequent repositories, storing them in `~/.config/gittty/frequent_repos.json`.

This structure makes the tool easy to maintain and extend.
