class InsufficientQuotaError(Exception):
    pass


class UserExitError(Exception):
    """Raised when the user chooses to exit from the main menu."""
    pass


class InternetConnectionError(Exception):
    """Raised when the user declares that they do not have a working Internet connection."""
    pass