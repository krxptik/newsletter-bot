from tqdm import tqdm as _tqdm

from .. import constants

DEFAULT_BAR_FORMAT = (
    " " * constants.CENTER_MARGIN +
    "{desc}: {percentage:3.0f}%|{bar}| {n}/{total} {unit}s "
    "[{elapsed} elapsed, ~{remaining} left]"
)


def app_tqdm(*args, **kwargs):
    kwargs.setdefault("ncols", constants.WIDTH + constants.CENTER_MARGIN)
    kwargs.setdefault("bar_format", DEFAULT_BAR_FORMAT)
    return _tqdm(*args, **kwargs)


def run_with_spinner(message: str, func, *args, **kwargs):
    import itertools
    import sys
    import threading
    import time

    stop_event = threading.Event()

    def _spinner():
        for char in itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
            if stop_event.is_set():
                break
            sys.stdout.write(f"\r  {char}  {message}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(message) + 6) + "\r")

    t = threading.Thread(target=_spinner)
    t.start()
    try:
        result = func(*args, **kwargs)
    finally:
        stop_event.set()
        t.join()
    return result