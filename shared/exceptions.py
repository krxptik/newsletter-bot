class InsufficientQuotaError(Exception):
    pass


class UserExitError(Exception):
    """Raised when the user chooses to exit from the main menu."""
    pass