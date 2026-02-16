import time

# ===== INPUT HELPER FUNCTIONS =====

def get_input_with_back(prompt: str, validator=None, error_msg: str = "Invalid input.") -> str | None:
    """Get user input with validation and back option."""
    while True:
        print(f"\n{prompt}")
        print("(Type 'back' to cancel)")
        user_input = input("> ").strip()
        
        if user_input.lower() == 'back':
            return None
        
        if not user_input:
            print("ERROR: Input cannot be empty.")
            time.sleep(1)
            continue
        
        if validator and not validator(user_input):
            print(f"ERROR: {error_msg}")
            time.sleep(1)
            continue
        
        return user_input


def confirm_action(prompt: str) -> bool:
    """Ask user for Y/N confirmation."""
    while True:
        response = input(f"\n{prompt} (Y/N): ").strip().upper()
        if response == 'Y':
            return True
        elif response == 'N':
            return False
        else:
            print("ERROR: Please enter Y or N")
            time.sleep(1)