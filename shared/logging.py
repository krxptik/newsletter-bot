"""
shared/logging.py
-----------------
Call setup_logging() exactly once, early in main(), after load_dotenv().
Every other module gets a logger with:

    import logging
    logger = logging.getLogger(__name__)

That's all — no further configuration needed anywhere else.
"""

import logging
from pathlib import Path
from datetime import datetime


def setup_logging(log_to_file: bool = True) -> None:
    fmt = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handlers: list[logging.Handler] = []

    if log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(fmt)
        file_handler.setLevel("DEBUG")
        handlers.append(file_handler)

    logging.basicConfig(level="DEBUG", handlers=handlers)

    for lib in ("urllib3", "requests", "feedparser", "google"):
        logging.getLogger(lib).setLevel(logging.WARNING)

    logging.getLogger(__name__).info("Logging initialised")
    if log_to_file:
        logging.getLogger(__name__).info(f"Log file: {log_file}")