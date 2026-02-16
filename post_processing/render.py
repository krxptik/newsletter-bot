from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime

def render_newsletter(context):
    env = Environment(
        loader=FileSystemLoader("newsletter_email/templates"),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')
    html = template.render(context)

    return html

def save_newsletter(html: str, title: str):
    date = datetime.now().strftime('%d%m%Y')
    filename = date + '_' + title.lower().replace(' ', '_')
    path = 'newsletter/' + filename

    with open(path, 'w') as f:
        f.write(html)

    return path