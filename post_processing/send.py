from email.message import EmailMessage
from typing import List
import smtplib
import ssl
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587                 

def send_email(em: EmailMessage, to_addrs: List) -> None:
    try:
        # Create a secure SSL context
        context = ssl.create_default_context()

        # Connect to the server and log in
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)  # Secure the connection
            server.login(os.getenv("EMAIL_ADDRESS"), os.getenv('EMAIL_APP_PASSWORD'))
            server.send_message(
                em, 
                to_addrs=to_addrs
            )
        print("Email sent successfully!")

    except smtplib.SMTPException as e:
        print(f"Error: unable to send email. {e}")