from jinja2 import Environment, FileSystemLoader, select_autoescape

def render_newsletter(context):
    env = Environment(
        loader=FileSystemLoader("newsletter_email/templates"),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')
    html = template.render(context)

    return html