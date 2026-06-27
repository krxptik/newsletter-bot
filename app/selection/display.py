from models.article import Article
from shared.terminal import clear_terminal, divider, label_block, WIDTH
from app.selection.constants import ARTICLES_PER_PAGE, LIST_NO_WIDTH, LIST_SPACING, LIST_WIDTH
from app.selection.pager import Pager


# ===== HELPERS =====

def _truncate(text: str, width: int) -> str:
    return text[:width - 1] + "…" if len(text) > width else text

def _formatted_row(left: str, right: str) -> str:
    return left.ljust(LIST_WIDTH) + (" " * LIST_SPACING) + right


# ===== DISPLAY =====

def display_list(available: Pager, selected: Pager) -> None:
    clear_terminal()
    print(_formatted_row("Available articles", "Selected"))
    print(_formatted_row("=" * LIST_WIDTH, "=" * LIST_WIDTH))

    a_items, a_start = available.get_page_items()
    s_items, s_start = selected.get_page_items()

    for i in range(ARTICLES_PER_PAGE):
        left, right = "", ""

        if i < len(a_items):
            num = f"({a_start + i + 1})".ljust(LIST_NO_WIDTH)
            title = _truncate(a_items[i].title, LIST_WIDTH - LIST_NO_WIDTH)
            left = num + title

        if i < len(s_items):
            letter = f"({chr(ord('A') + s_start + i)})".ljust(LIST_NO_WIDTH)
            title = _truncate(s_items[i].title, LIST_WIDTH - LIST_NO_WIDTH)
            right = letter + title

        print(_formatted_row(left, right))

    print(_formatted_row("=" * LIST_WIDTH, "=" * LIST_WIDTH))
    print(_formatted_row(
        f"Page {available.page}/{available.max_page}",
        f"Page {selected.page}/{selected.max_page}"
    ))

def display_article_details(article: Article) -> None:
    pub_date = article.pub_date.strftime('%d/%m/%Y') if article.pub_date else 'Unknown'
    divider()
    print(label_block([
        "Title:",
        "Date:",
        "Source:",
        "Link:",
        "Tags:",
        "Summary:"
    ],
                [
        article.title,
        pub_date,
        article.source,
        article.link,
        ', '.join(article.tags or []),
        article.summary
    ]))
    divider()


def confirm_selection(selected: Pager) -> bool:
    clear_terminal()
    print("You have selected:")
    divider()
    for i, article in enumerate(selected.items, 1):
        print(f"({i}) {_truncate(article.title, WIDTH-4)}")
    divider()
    response = input("\nGenerate newsletter? (Y/N): ").strip().upper()
    return response == 'Y'