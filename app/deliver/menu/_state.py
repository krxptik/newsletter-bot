from enum import Enum, auto


class State(Enum):
    MAIN = auto()
    EDIT = auto()
    MANAGE_RECIPIENTS = auto()
    ADDRESS_BOOK = auto()