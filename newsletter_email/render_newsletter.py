from jinja2 import Environment, FileSystemLoader, select_autoescape

# Sample articles
articles = [
    {
        "title": "The Evolution of English in the Digital Age",
        "link": "https://example.com/article1",
        "summary": (
            "Digital communication transforms English through slang, hybrid dialects, and global exposure, "
            "sparking debates over standards while illustrating how language adapts alongside technology and culture."
        ),
        "source": "All Things Linguistic"
    },
    {
        "title": "Social Media Slang Trends",
        "link": "https://example.com/article2",
        "summary": (
            "Social media drives rapid slang creation, reflecting youth identity, creativity, and memes, "
            "while challenging traditional grammar and revealing how online communities accelerate linguistic innovation globally."
        ),
        "source": "Language Log (UPenn)"
    },
    {
        "title": "Global English and Code-Switching",
        "link": "https://example.com/article3",
        "summary": (
            "Global digital spaces encourage code-switching and hybrid English forms, blending dialects and registers "
            "while reshaping identity, comprehension, and cultural exchange in online communication."
        ),
        "source": "The Guardian"
    }
]

context = {
    "title": "From Texts to Threads: English Today",
    "date": "January 18, 2026",
    "summary": (
        "This newsletter examines how digital platforms reshape English, from social media slang to code-switching, "
        "revealing how technology, culture, and identity drive linguistic change."
    ),
    "article_rows": articles
}

def render_newsletter(context):
    env = Environment(
        loader=FileSystemLoader("newsletter_email/templates"),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')
    html = template.render(context)

    with open('meow.html', 'w') as f:
        f.write(html)
    return html

if __name__ == '__main__':
    render_newsletter(context)