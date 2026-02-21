from google import genai
from models.article import Article
from config import AI_DIR
import os

SUM_TAG_PATH = AI_DIR / "sum_tag.txt"
FINAL_SUM_PATH = AI_DIR / "final_sum.txt"

class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
    
    def sum_tag_prompt(self, article: Article) -> bool:
        tags = ["P2SA", "P2SB"]

        with open(SUM_TAG_PATH, 'r') as f:
            prompt = f.read() % (f"{', '.join(tags)}", f"{article.text}")

        response = self.client.models.generate_content(
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

    def final_sum_prompt(self, articles: list[Article]):
        summaries = [f"{i+1}. " + article.summary for i, article in enumerate(articles)]

        with open(FINAL_SUM_PATH, 'r') as f:
            prompt = f.read() % ('\n'.join(summaries))

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        raw_text = response.text.strip()

        _, _, after_title = raw_text.partition("TITLE:")
        title_block, _, summmary_part = after_title.partition("SUMMARY:")
        title_block = title_block.strip()
        summary_block = summmary_part.strip()
        
        return (title_block, summary_block)
        
# Inject at runtime:
def create_ai_client() -> GeminiClient:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    return GeminiClient(api_key)