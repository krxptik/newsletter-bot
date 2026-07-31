import logging

from ._setup_wizard import run_setup_wizard
from ._settings_menu import run_main_menu
from app.persistence import load_config, refresh_dynamic_flags

logger = logging.getLogger(__name__)


def start_initialisation() -> None:
    logger.info("Starting initialisation")
    config = load_config()

    if config.is_complete():
        logger.info("Config complete — skipping setup wizard")
        run_main_menu(config)
    else:
        logger.info("Config incomplete — launching setup wizard")
        run_setup_wizard(config)
        refresh_dynamic_flags(config)
        run_main_menu(config)

    logger.info("Initialisation complete")