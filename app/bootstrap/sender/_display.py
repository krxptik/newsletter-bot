from shared.ui import widgets, screen


def display_sender_details(email: str | None, app_password: str | None) -> None:
    screen.clear()
    screen.divider()
    widgets.blank()
    widgets.dot_leader_list([
        ("Sender email:", email or "not set"),
        ("Sender app password:", app_password or "not set")
    ])
    widgets.blank()
    screen.divider()