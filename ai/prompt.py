from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
# You must set your Google AI Studio API Key as an environment variable for this to work.

client = genai.Client()

def summarise_and_tag(article):
    tags = ["P2SA", "P2SB"]
    prompt = (
        "You are an assistant helping tag and summarise articles for A-Level ELL according to the 9508 syllabus.\n\n"

        "Provided below is the required portion of the A-Level ELL 9508 syllabus.\n\n"

        "Section A (P2SA) covers Language Variation and Change, including:\n"
        "- reasons for language variation and change\n"
        "- notable examples of language change\n"
        "- terms/concepts related to variation\n"
        "- variation in English, attitudes to varieties\n"
        "- Standard Singapore English and Colloquial Singapore English\n"
        "- English as a world language\n"
        "- impact of technology on English use\n\n"

        "Section B (P2SB) covers Language, Culture, and Identity, including:\n"
        "- how culture and language influence each other\n"
        "- how language conveys, influences, and constructs social understanding\n"
        "- representing people, institutions, events, issues\n"
        "- shaping values and attitudes\n"
        "- inclusion and exclusion via language\n\n"

        "Your task is to make a 100-word summary of the article such that key ideas are still kept,\n"
        "and to label the following article with the **most relevant tag(s)** from this list:\n"
        f"{', '.join(tags)}\n\n"

        "Provided below is the scraped text from the article.\n\n"

        f"{article.text}\n\n"

        "Instructions:\n"
        "- Only include tags from the list above.\n"
        "- If only one tag, simply put '<tag1>' instead of '<tag1>,<tag2>'"
        "- Choose P2SA if the article focuses on language variation or change.\n"
        "- Choose P2SB if the article focuses on language, culture, or identity.\n"
        "- Do not invent new tags.\n"
        "- Do not explain your choices.\n"
        "- If unsure, choose the single closest tag.\n"
        "- If the article relates to both, include both tags.\n\n"

        "- The summary should not have multiple paragraphs. There should only be one.\n"
        "- The summary must not have newlines.\n"
        "- The summary must be 100 words in length at most.\n\n"

        "- Output should be exactly in this format, with no other text:\n\n"

        "SUMMARY:\n"
        "<100-word summary>\n\n"

        "TAGS:\n"
        "<tag1> OR <tag1>,<tag2>"
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )

    raw_text = response.text.strip()

    try:
        summary_block = raw_text.split("SUMMARY:")[1].split("TAGS:")[0].strip()
        tags_block = raw_text.split("TAGS:")[1].strip()
    except IndexError:
        return False
        
    article.summary = summary_block
    article.tags = [tag.strip() for tag in tags_block.split(",")]
    return True