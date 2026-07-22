from shared.ui import widgets, screen

def display_ai_details(api_key: str | None) -> None:
    screen.clear()
    screen.divider()
    widgets.blank()
    widgets.dot_leader_list([("Google AI API key:", api_key or "not set")])
    widgets.blank()
    screen.divider()