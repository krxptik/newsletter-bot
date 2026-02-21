# utils/logging_config.py
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_to_file: bool = True):
    """Configure logging for entire application."""
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (always)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # File handler (optional)
    handlers = [console_handler]
    if log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel("DEBUG")  # File gets everything
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level="DEBUG",  # Capture everything, handlers filter
        handlers=handlers
    )
    
    # Quiet noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    logging.info("Logging configured")
    logging.info(f"Log level: {log_level}")
    if log_to_file:
        logging.info(f"Log file: {log_file}")