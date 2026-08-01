import os
from pathlib import Path

from ._parser import parse_draft, DraftParsingError

from path_config import RUNTIME_DIR
from shared.prompts import confirmation
from shared.ui import widgets

DRAFT_FILE = RUNTIME_DIR / "draft.md"
INSTRUCTIONS = """HOW TO EDIT THIS NEWSLETTER
- Edit any text you like under a heading.
- Don't delete or reorder the lines starting with # or ##.
- Save and close this file, then go back to the program.
"""
REDO_MESSAGE = "Please manually undo changes, or undo all."


# ===== ENTRY POINT =====

def run_markdown_edit(context: dict) -> dict:
    path = DRAFT_FILE
    rewrite = True

    while True:
        if rewrite:
            path.write_text(_render_draft(context), encoding="utf-8")
            _open_for_editing(path)
            rewrite = False

        if not confirmation("Finished editing?"):
            continue

        try:
            return parse_draft(path.read_text(encoding="utf-8"))
        except DraftParsingError as e:
            widgets.text(f"ERROR: {e}")
            widgets.text(REDO_MESSAGE)
            rewrite = confirmation("Undo all changes?")


# ===== DRAFT RENDERING =====

def _render_draft(context: dict) -> str:
    lines = [INSTRUCTIONS, f"# {context['title']}", "", context["summary"], ""]
    for row in context["article_rows"]:
        lines += [
            f"## {row['title']}", "",
            row["summary"], "",
            f"Source: {row['source']}",
            f"Link: {row['link']}", "",
        ]
    return "\n".join(lines)


def _open_for_editing(path: Path) -> None:
    os.startfile(path)