import os

def clear_terminal() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')