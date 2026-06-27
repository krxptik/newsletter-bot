import os
import pyfiglet

import threading
import itertools
import sys
import time
import shutil

# ------- CLI SETTINGS -------

WIDTH = shutil.get_terminal_size().columns

# ===== DISPLAY =====

def clear_terminal() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def divider(width: int = WIDTH, single: bool = False, spacing: bool = False) -> None:
    raw_line = "-" * width if single else "=" * width
    line = f"\n{raw_line}\n" if spacing else raw_line
    print(line)


def center_text(text: str, width: int = WIDTH):
    return text.center(width)

def display_banner(header: str, single: bool = False, width: int = WIDTH) -> None:
    divider(width, single)

    raw = center_text(header, width)
    text = "\n" + raw + "\n"
    print(text)
    
    divider(width, single)

def display_banner_figlet(header: str, width: int = WIDTH) -> None:
    clear_terminal()
        
    divider(width)
    print()
    print(pyfiglet.figlet_format(header, font="banner3-D", justify="center", width=width))
    divider(width)


# ===== FORMATTING =====

def label_line(
        label: str, value: str, 
        width: int = WIDTH, separator: str = "", 
        label_width: int | None = None, justify: str = "left") -> str:
    
    label_width = label_width if label_width else len(str(label))
    separator_length = len(separator) + 2
    value_length = width - label_width - separator_length
    value_indent = label_width + separator_length

    wrapped_value = wrap_text(str(value), width=value_length, indent=value_indent, justify=justify)
    
    return f"{label:<{label_width}} {separator} {wrapped_value}"

def wrap_text(text: str, width: int, indent: int = 0, justify: str = "left") -> str:
    """Wrap text to width, hyphenating long words only where meaningful.
    justify: 'left', 'right', or 'center'
    """
    MIN_HYPHEN_BEFORE = 3
    MIN_WORD_LENGTH = 6

    words = text.split()
    idx = 0
    lines = []
    indent_spacing = " " * indent
    current = ""

    while idx < len(words):
        word = words[idx]
        remaining_length = width - len(current)

        if remaining_length > 0:
            if len(word) <= remaining_length:
                current += word + " "
                idx += 1
            elif len(word) >= MIN_WORD_LENGTH and remaining_length - 1 >= MIN_HYPHEN_BEFORE:
                left, right = word[:remaining_length - 1], word[remaining_length - 1:]
                words[idx] = right
                current += left + "-"
            else:
                lines.append(current.rstrip())
                current = ""
        else:
            lines.append(current.rstrip())
            current = ""

    if current:
        lines.append(current.rstrip())

    def _align_value(line: str) -> str:
        stripped = line.rstrip()
        if justify == "right":
            return indent_spacing + stripped.rjust(width)
        elif justify == "center":
            return indent_spacing + stripped.center(width)
        else:
            return indent_spacing + stripped

    raw = "\n".join(_align_value(line) for line in lines)
    return raw[indent:]


def _align(text: str, width: int = WIDTH, justify="left"):
    if justify == "right":
        return text.rjust(width)
    elif justify == "center":
        return text.center(width)
    else:
        return text

def label_block(
        labels: list, values: list, 
        width: int = WIDTH, separator: str = "", 
        justify: str = "left", justify_block: str = "left") -> str:
    
    label_width = max(len(str(label)) for label in labels)
    
    rows = [
        _align(label_line(label, value, width, separator, label_width, justify), justify=justify_block) 
        for label, value in zip(labels, values)
    ]

    return "\n".join(rows)


# ===== INPUT =====

def confirmation(prompt: str) -> bool:
    """Ask user for Y/N confirmation."""
    while True:
        response = input(f"\n{prompt} (y/n): ").strip().upper()
        if response == 'Y':
            return True
        elif response == 'N':
            return False
        else:
            print("ERROR: Please enter Y or N")
            time.sleep(1)


# ===== ASYNC =====

def _spinner(message: str, stop_event: threading.Event) -> None:
    for char in itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
        if stop_event.is_set():
            break
        sys.stdout.write(f"\r  {char}  {message}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(message) + 6) + "\r")

def run_with_spinner(message: str, func, *args, **kwargs):
    stop_event = threading.Event()
    t = threading.Thread(target=_spinner, args=(message, stop_event))
    t.start()
    try:
        result = func(*args, **kwargs)
    finally:
        stop_event.set()
        t.join()
    return result