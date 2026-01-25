from google import genai
from models.article import Article

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
# You must set your Google AI Studio API Key as an environment variable for this to work.

client = genai.Client()

def sum_tag_prompt(article: Article) -> bool:
    """
    Generate a 100-word summary and relevant tag(s) for an Article object 
    according to the A-Level ELL 9508 syllabus.

    Args:
        article (Article): The article object to summarise and tag. 
                           Must have `text` attribute containing article content.

    Returns:
        bool: True if summarisation and tagging succeeded, False if parsing the AI response failed.
    """
    tags = ["P2SA", "P2SB"]

    with open('ai/sum_tag.txt', 'r') as f:
        prompt = f.read() % (f"{', '.join(tags)}", f"{article.text}")

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )

    raw_text = response.text.strip()

    # Safer parsing using partition
    summary_block = tags_block = None
    if "SUMMARY:" in raw_text and "TAGS:" in raw_text:
        _, _, after_summary = raw_text.partition("SUMMARY:")
        summary_block, _, tags_part = after_summary.partition("TAGS:")
        summary_block = summary_block.strip()
        tags_block = tags_part.strip()
    else:
        return False

    article.summary = summary_block
    article.tags = [tag.strip() for tag in tags_block.split(",")]
    return True

def final_sum_prompt(articles: list[Article]):
    summaries = [f"{i+1}. " + article.summary for i, article in enumerate(articles)]

    with open('ai/final_sum.txt', 'r') as f:
        prompt = f.read() % ('\n'.join(summaries))

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )

    raw_text = response.text.strip()

    _, _, after_title = raw_text.partition("TITLE:")
    title_block, _, summmary_part = after_title.partition("SUMMARY:")
    title_block = title_block.strip()
    summary_block = summmary_part.strip()
    
    return (title_block, summary_block)