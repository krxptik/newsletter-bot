from shared.terminal import WIDTH, display_banner, divider, center_text, label_block, wrap_text, clear_terminal


# ===== FEED SECTIONS =====

def render_feed_section(f_type: str, feeds: list, width: int = WIDTH) -> None:
    clear_terminal()
    display_banner(f"{f_type} FEEDS", width=width)
    print()

    if feeds:
        _render_feed_list(feeds)
    else:
        print(center_text("No feeds configured.", width))

    divider(width, single=True, spacing=True)
    print("Options:")
    print("  (1) Add new feed")
    print("  (2) Remove existing feed")
    print("  (3) Confirm and proceed")


def render_remove_section(f_type: str, feeds: list) -> None:
    clear_terminal()
    display_banner(f"SELECT {f_type} FEED TO REMOVE")
    print()
    _render_feed_list(feeds)
    divider(single=True, spacing=True)


# ===== FEED DISPLAY =====

def _render_feed_list(feeds: list) -> None:
    for i, feed in enumerate(feeds, 1):
        print(f"[{i}] {feed['name']}")
        print(wrap_text(feed["url"], WIDTH))
        if i < len(feeds):
            print()


def display_feed_data(feed: dict) -> None:
    labels = ["Type:", "Name:", "URL:"]
    values = [feed["type"], feed["name"], feed["url"]]

    if feed["type"] == "NON-RSS":
        labels.append("Date visible:")
        values.append(str(feed["allow_regex_fallback"]))

    print()
    print(label_block(labels, values))