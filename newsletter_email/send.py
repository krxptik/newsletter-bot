import smtplib
import ssl
from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587                 
SENDER_EMAIL = "jaredcasimsiman@gmail.com" 
PASSWORD = "untv vcwj sjgs ppyr"
TO_EMAILS = [
    "jaredcasimsiman2@gmail.com", 
    "jaredmcasimsiman@gmail.com"
]
CC_EMAILS = [
    "steamyflame@gmail.com"
]

BCC_EMAILS = [
    "meowdoublemrow@gmail.com"
]

msg = EmailMessage()
msg.set_content("Hello, this is a test email sent using Python's smtplib!") # Email body
msg['Subject'] = "Test Email from Python"
msg['From'] = SENDER_EMAIL
msg['To'] = ", ".join(TO_EMAILS)
msg['Cc'] = ", ".join(CC_EMAILS)

try:
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Connect to the server and log in
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)  # Secure the connection
        server.login(SENDER_EMAIL, PASSWORD)
        server.send_message(
            msg, 
            to_addrs=TO_EMAILS + CC_EMAILS + BCC_EMAILS
        )
    print("Email sent successfully!")

except smtplib.SMTPException as e:
    print(f"Error: unable to send email. {e}")