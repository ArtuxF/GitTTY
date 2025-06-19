def display_welcome():
    """Displays a welcome message on the TTY."""
    print("--------------------------------------------------")
    print("       Welcome to GitTTY - Your Git lifeline      ")
    print("--------------------------------------------------")
    print("Clone your essential repositories directly from the TTY.\n")

def get_user_input(prompt):
    """Gets text input from the user."""
    return input(f"{prompt}: ").strip()
