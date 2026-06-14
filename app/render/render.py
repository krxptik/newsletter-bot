import os
import webbrowser
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from config import TEMPLATES_DIR, OUTPUT_DIR


def preview_newsletter(path: Path) -> None:
    webbrowser.open_new_tab(f"file://{os.path.abspath(path)}")


def render_newsletter(context: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')
    html = template.render(context)

    return html


def save_newsletter(html: str, title: str) -> Path:
    date = datetime.now().strftime('%d%m%Y')
    filename = date + '_' + title.lower().replace(' ', '_')
    path = OUTPUT_DIR / filename

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    return path