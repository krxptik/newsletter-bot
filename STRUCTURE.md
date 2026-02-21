# Project Structure Guide

## Directory Layout
newsletter-bot/
├── ai/                    # AI integration (Gemini)
│   ├── prompt.py         # AI prompt functions
│   ├── throttle.py       # Rate limiting & retry
│   ├── sum_tag.txt       # Prompt template
│   └── final_sum.txt     # Newsletter summary prompt
├── cli/                   # User interface
│   └── menu.py           # Interactive article selection
├── data/                  # Data storage & access
│   ├── loader.py         # JSON file I/O
│   ├── feeds.json        # RSS/feed configuration
│   ├── urls.json         # Used article tracking
│   └── email_addrs.json  # Email groups
├── logs/                  # Log folder
│   └── feedbot.log       # Project log
├── models/               # Domain models
│   └── article.py        # Article data class
├── post_processing/      # Newsletter generation
│   ├── context.py        # Template context builder
│   ├── manage_articles.py # Save used articles
│   ├── render.py         # HTML generation
│   ├── send.py           # SMTP email sending
│   ├── send_menu.py      # Email configuration UI
│   └── templates/
│       └── index.html    # Newsletter HTML template
├── setup/                # First-run configuration
│   ├── run.py            # Setup orchestration
│   ├── env_config.py     # .env file management
│   ├── feed_operations.py # Feed CRUD operations
│   ├── validators.py     # Input validation
│   ├── url_helpers.py    # URL/regex helpers
│   └── ui/
│       ├── display.py    # Terminal UI helpers
│       └── input_helpers.py # Input prompts
├── sources/              # Article fetching & parsing
│   ├── main_parser.py    # Parser orchestrator
│   ├── rss_parser.py     # RSS feed parser
│   ├── hybrid_parser.py  # RSS + web scraping
│   ├── non_rss_parser.py # Pure web scraping
│   └── prune.py          # Article filtering
├── utils/                # Shared utilities
│   ├── banner.py         # ASCII art banner
│   ├── clear_terminal.py # Screen clearing
│   ├── datefuncs.py      # Date parsing helpers
│   ├── safe_gen.py       # AI call wrapper
│   └── safe_request.py   # HTTP request wrapper
├── main.py               # Application entry point
├── .env                  # Environment variables (create this)
└── requirements.txt      # Python dependencies (create this)

## Data Flow

1. **Initialization** (main.py)
   - Load environment variables
   - Run setup if first time
   - Load feeds from data/feeds.json

2. **Article Fetching** (sources/)
   - main_parser.parse_all() orchestrates
   - Calls appropriate parser based on feed type
   - Returns list of Article objects

3. **Filtering** (sources/prune.py)
   - Remove previously used articles
   - Limit to ARTICLE_LIMIT articles
   - Sort by pub_date

4. **AI Processing** (ai/)
   - throttle() processes all articles
   - For each: sum_tag_prompt() generates summary & tags
   - Handles rate limits and retries

5. **User Selection** (cli/menu.py)
   - Interactive menu to select articles
   - Returns list of selected articles

6. **Newsletter Generation** (post_processing/)
   - Generate title & summary with AI
   - Build template context
   - Render HTML with Jinja2
   - Save to file

7. **Email Sending** (post_processing/)
   - Configure recipients with send_menu()
   - Send via SMTP

8. **Cleanup** (post_processing/manage_articles.py)
   - Save used article URLs
   - Prevent duplicates in future runs

## Key Files to Know

### main.py
Entry point. Orchestrates entire workflow. Read this first.

### models/article.py
Core data model. All parsers return Article objects.

### sources/main_parser.py
Routing logic for different parser types.

### ai/throttle.py
Handles AI rate limiting. Critical for avoiding quota issues.

### cli/menu.py
Complex state machine. UI logic for article selection.

### post_processing/render.py
Jinja2 template rendering. Look here for HTML issues.

## Common Tasks

### Adding a new feed type:
1. Create parser in sources/ (follow rss_parser.py pattern)
2. Add type to main_parser.py routing
3. Update setup/feed_operations.py UI

### Changing AI prompts:
1. Edit ai/sum_tag.txt or ai/final_sum.txt
2. No code changes needed (templates loaded at runtime)

### Modifying email template:
1. Edit post_processing/templates/index.html
2. Update context in post_processing/context.py if adding fields

### Adding logging:
1. Import logging in each module
2. Get logger: logger = logging.getLogger(__name__)
3. Replace print() with logger.info/warning/error()