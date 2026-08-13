from shared.ui import screen, widgets


def header_str(n: int, domain: str, paths: list[str]) -> str:
    return f"[{n}] {domain} ({len(paths)} blocked)"


def domain_sections(blocklist: dict[str, list[str]]) -> list[tuple[str, list[str]]]:
    return [
        (header_str(n, domain, paths), paths)
        for n, (domain, paths) in enumerate(sorted(blocklist.items()), 1)
    ]


def display_blocklist(blocklist: dict[str, list[str]], options: list[str] | None = None, clear: bool = True) -> None:
    if clear:
        screen.clear()
    widgets.section_header("DOMAIN BLOCKLIST")
    widgets.blank()
    widgets.tree_list(domain_sections(blocklist), empty_message="No domains blocked.")
    widgets.blank()
    if options:
        screen.divider()
        widgets.blank()
        widgets.options_menu(options)
        widgets.blank()