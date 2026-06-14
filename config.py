from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

OUTPUT_DIR = PROJECT_ROOT / "newsletters"

DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = DATA_DIR / "config"
RUNTIME_DIR = DATA_DIR / "runtime"

APP_DIR = PROJECT_ROOT / "app"
TEMPLATES_DIR = APP_DIR / "render" / "templates"
AI_PROMPTS_DIR = APP_DIR / "enrich" / "prompts"