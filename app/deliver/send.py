import logging
import os
import smtplib
import ssl
from email.message import EmailMessage

logger = logging.getLogger(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(em: EmailMessage, to_addrs: list[str]) -> None:
    logger.info(f"Sending email to {len(to_addrs)} recipient(s): {to_addrs}")

    try:
        context = ssl.create_default_context()

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            logger.debug(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}")
            server.starttls(context=context)
            email_address = os.getenv("EMAIL_ADDRESS")
            email_app_password = os.getenv("EMAIL_APP_PASSWORD")
            if email_address is None or email_app_password is None:
                raise ValueError("Missing EMAIL_ADDRESS or EMAIL_APP_PASSWORD environment variable")
            server.login(email_address, email_app_password)
            logger.debug("SMTP login successful")
            server.send_message(em, to_addrs=to_addrs)

        logger.info("Email sent successfully")
        print("Email sent successfully!")

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        print(f"Error: authentication failed — check your email and app password.")

    except smtplib.SMTPException as e:
        logger.error(f"SMTP error while sending email: {e}")
        print(f"Error: unable to send email. {e}")

    except Exception as e:
        logger.exception(f"Unexpected error sending email: {e}")
        print(f"Error: unexpected failure. Check logs for details.")