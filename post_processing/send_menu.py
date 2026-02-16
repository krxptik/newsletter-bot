from utils.clear_terminal import clear_terminal
from email.message import EmailMessage
from enum import Enum, auto
import os
import webbrowser
import json
import time

class State(Enum):
    MAIN = auto()
    EDIT = auto()

class MenuHandler:
    def __init__(self, subject: str, path: str, html: str):
        self.state = State.MAIN
        self.path = path
        self.to_addrs = set()
        self.em = EmailMessage()
        self.addrs_names = {
            "To": [],
            "Cc": [],
            "Bcc": []
        }
        with open('data/email_addrs.json', 'r') as f:
            self.groups = json.load(f)

        self.em['Subject'] = subject
        self.em['From'] = os.getenv("EMAIL_ADDRESS")
        self.em.set_content("This email contains HTML elements."
                    "If you are seeing this, the email is not loading properly."
                    "Please view this in a proper email client.")
        self.em.add_alternative(html, subtype='html')
        
    def handle_main_input(self, user_input: str) -> None:
        if user_input.isdigit():
            option = int(user_input)

            if option == 1:
                self.state = State.EDIT
            elif option == 2:
                webbrowser.open_new_tab(f"file://{os.path.abspath(self.path)}")
            elif option == 3:
                if (self.em.get('Subject') and self.em.get('From') and len(self.to_addrs) > 0):
                    self.state = None
                else:
                    self._show_error('Necessary email details empty, please fill them in.')

    def handle_edit_input(self, user_input: str) -> None:
        cmd = user_input.lower()

        if cmd.startswith('edit'):
            _, _, part = user_input.partition('edit ')
            parsed = part.strip().split(' ')

            if parsed[0] == 'subject':
                new = input("New 'Subject': ")
                self._set_header('Subject', new)

            elif parsed[0] in ('to', 'cc', 'bcc'):
                recipient_type = parsed[0].capitalize() 

                if parsed[1] == 'add':
                    new = input(f"Add recipient/group under '{recipient_type}': ")

                    if "@" in new:
                        self.addrs_names[recipient_type].append(new)
                        self._set_header(recipient_type, ', '.join(self.addrs_names[recipient_type]))
                        self.to_addrs.add(new)

                    else:
                        addrs = self.groups.get(new.upper())

                        if addrs is not None:
                            self.addrs_names[recipient_type].append(new.upper())
                            self._set_header(recipient_type, ', '.join(self.addrs_names[recipient_type]))
                            self.to_addrs.update(addrs)
                        else:
                            self._show_error(f"Group '{new.upper()}' not found in email_addrs.json.")
                    

                elif parsed[1] == 'remove':
                    rem = input(f"Remove recipient/group under '{recipient_type}': ")

                    if "@" in rem:
                        if rem in self.to_addrs:
                            self.to_addrs.remove(rem)
                            self.addrs_names[recipient_type].remove(rem)
                            self._set_header(recipient_type, ', '.join(self.addrs_names[recipient_type]))
                        else:
                            self._show_error(f"Recipient '{rem}' not found in {recipient_type}.")
                    
                    else:
                        addrs = self.groups.get(rem.upper())

                        if rem.upper() in self.addrs_names[recipient_type]:
                            self.to_addrs -= set(addrs)
                            self.addrs_names[recipient_type].remove(rem)
                            self._set_header(recipient_type, ', '.join(self.addrs_names[recipient_type]))
                        else:
                            self._show_error(f"Group '{rem}' not found in {recipient_type}.")

        elif cmd == 'back':
            self.state = State.MAIN

        else:
            self._show_error(f"Invalid command.")

    def _show_error(self, message: str) -> None:
        """Display error message temporarily."""
        clear_terminal()
        print(f"{message}")
        print("\nReturning to menu in 3 seconds...")
        time.sleep(3)

    def _set_header(self, header: str, value) -> None:
        """Safely set a single-instance email header (To, Cc, Bcc)."""
        if header in self.em:
            self.em.replace_header(header, value)
        else:
            self.em[header] = value
         
def display_details(em: EmailMessage) -> None:
    clear_terminal()
    print("EMAIL DETAILS")
    print(f"{'='*60}")
    print(f"Subject: {em.get('Subject'), ''}")
    print(f"From: {em.get('From'), ''}")
    print(f"To: {em.get('To'), ''}")
    print(f"Cc: {em.get('Cc'), ''}")
    print(f"Bcc: {em.get('Bcc'), ''}")
    print(f"{'='*60}")

def send_menu(subject: str, path: str, html: str):
    handler = MenuHandler(subject, path, html)

    while handler.state is not None:
        clear_terminal()
        
        if handler.state == State.MAIN:
            display_details(handler.em)
        
            print("\nOptions:")
            print("(1) Edit details")
            print("(2) View HTML")
            print("(3) Submit details and send email")

            user_input = input("> ")
            handler.handle_main_input(user_input)

        elif handler.state == State.EDIT:
            display_details(handler.em)

            print("\nOptions:")
            print("edit <subject> | edit <to/cc/bcc> <add/remove> | back\n")
            
            user_input = input("> ")

            handler.handle_edit_input(user_input)

    return (handler.em, list(handler.to_addrs))