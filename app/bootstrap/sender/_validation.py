import logging
import smtplib

from shared.email import is_valid_email

logger = logging.getLogger(__name__)


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
    return is_valid_email(email) and _validate_smtp_credentials(email, app_password)