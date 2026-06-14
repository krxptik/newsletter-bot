import logging
import smtplib

from email_validator import validate_email, EmailNotValidError
from shared.terminal import divider, clear_terminal, label_block

logger = logging.getLogger(__name__)


def _is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def _validate_smtp_credentials(email: str, app_password: str) -> bool:
    logger.debug(f"Testing SMTP credentials for {email}")
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email, app_password)
        logger.info("SMTP credentials valid")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.warning(f"SMTP authentication failed for {email}")
        return False
    except Exception as e:
        logger.warning(f"SMTP connection error: {e}")
        return False


def is_valid_sender_details(email: str, app_password: str) -> bool:
    return _is_valid_email(email) and _validate_smtp_credentials(email, app_password)


def run_sender_setup(env_vars: dict) -> dict:
    logger.info("Running sender setup")
    email = env_vars.get("EMAIL_ADDRESS", "")
    app_password = env_vars.get("EMAIL_APP_PASSWORD", "")

    if is_valid_sender_details(email, app_password):
        logger.info("Existing sender credentials valid — skipping sender setup prompt")
        return env_vars

    logger.info("No valid sender credentials — prompting user")
    message = "No valid sender email and/or app password set."

    while True:
        clear_terminal()
        divider()
        print()
        print(label_block(["Sender email:", "Sender app password:"], [email or "not set", app_password or "not set"], justify_block="center"))
        divider(spacing=True)
        print(message)

        email_input = input("Please enter your email.\n> ").strip()
        app_pw_input = input("Please enter your email app password.\n> ").strip()
        logger.debug("User provided sender credentials")

        if is_valid_sender_details(email_input, app_pw_input):
            env_vars["EMAIL_ADDRESS"] = email_input
            env_vars["EMAIL_APP_PASSWORD"] = app_pw_input
            logger.info("New sender credentials accepted and saved")
            return env_vars

        logger.warning("Invalid sender credentials entered")
        message = "\nInvalid details. Please try again."