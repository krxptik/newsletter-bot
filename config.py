# config.py
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
TEMPLATES_DIR = PROJECT_ROOT / "post_processing" / "templates"
OUTPUT_DIR = PROJECT_ROOT / "newsletter"
AI_DIR = PROJECT_ROOT / "ai"