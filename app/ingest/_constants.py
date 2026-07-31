TRUNCATION_MARKERS = [
    "continue reading",
    "read more",
    "read the full",
    "[...]",
]

FEEDPARSER_FAIL_COUNT = 3
MIN_CONTENT_LENGTH = 200

# Cap on how much (cleaned) HTML gets sent to the AI fallback prompt.
# ~20000 chars is roughly 5000 tokens by the shared/token_bucket.py
# estimate — comfortably under Gemma's 16000 TPM ceiling even before
# accounting for other concurrent calls sharing that budget.
MAX_HTML_CHARS = 20000

# Tags stripped before HTML is sent to the AI fallback — these are pure
# token cost with no extraction value (nav/footer/scripts/etc.), unlike
# <title>/<meta>/<time> tags which the model may still need for title/date.
AI_STRIP_TAGS = ("script", "style", "noscript", "svg", "iframe", "nav", "footer", "aside")

FEED_WORKERS = 8
SCRAPE_WORKERS = 8
PER_DOMAIN_CONCURRENCY = 2