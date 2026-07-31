from shared.ui import widgets


def confirmation(prompt: str) -> bool:
    """Ask user for Y/N confirmation."""
    while True:
        response = widgets.m_input(f"{prompt} (Y/N): ").strip().upper()

        if response == "Y":
            return True

        if response == "N":
            return False

        widgets.notify("ERROR: Please enter Y or N")
        widgets.blank()