class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def display_welcome():
    """Displays a welcome message on the TTY."""
    print(f"{Colors.HEADER}--------------------------------------------------{Colors.ENDC}")
    print(f"{Colors.HEADER}       Welcome to GitTTY - Your Git lifeline      {Colors.ENDC}")
    print(f"{Colors.HEADER}--------------------------------------------------{Colors.ENDC}")
    print("Clone your essential repositories directly from the TTY.\n")

def get_user_input(prompt):
    """Gets text input from the user."""
    return input(f"{prompt}: ").strip()
