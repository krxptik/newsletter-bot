```
        _____      __
  ___  / / (_)__  / /
 / _ \/ / / / _ \/ / 
/  __/ / / /  __/_/  
\___/_/_/_/\___(_)   
```

# ellie! — AI-Powered Newsletter Aggregation and Delivery System

ellie! is a Python CLI program that scrapes articles from RSS and non-RSS feeds, enriches them with AI-generated summaries and tags, lets you hand-pick articles for your newsletter, and sends a formatted HTML email to your recipients — all from your terminal.

> **Note:** ellie! currently supports Windows only. Mac/Linux support is planned for a future release.

---

## Requirements

- Windows
- Python 3.14+
- A [Google AI API key](https://aistudio.google.com/apikey) (free tier is fine)
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) set up for sending

---

## Getting Started

### 1. Download

Click the green **Code** button on the GitHub page and select **Download ZIP**. Extract the folder somewhere on your computer.

### 2. Run

Double-click `run.bat` inside the extracted folder.

This will automatically create a virtual environment, install dependencies, and launch the program.

### 3. First Launch — Setup Wizard

On first launch, ellie! will walk you through a one-time setup. It will ask for your credentials and configure everything for you — no manual file editing required.

| Step | What you'll need |
|---|---|
| **AI** | Your Google AI API key |
| **Sender** | Your Gmail address and App Password |
| **Feeds** | RSS or non-RSS feed URLs you want to pull articles from |
| **Recipients** | Email addresses and/or groups to send to |

**Tips for feeds:**
- Most news sites and blogs have an RSS feed — look for an RSS icon or try appending `/feed` or `/rss` to the URL
- For sites without RSS, ellie! supports non-RSS scraping with a URL pattern — you'll need two example article URLs from the same site during setup

---

## How It Works

```
Fetch feeds → Filter articles → AI enrichment → You select articles → Generate newsletter → Send
```

1. **Ingest** — ellie! fetches articles from all your configured feeds
2. **Filter** — already-sent articles are excluded; batch size is capped by your daily AI quota
3. **Enrich** — each article is summarised and tagged by AI (runs concurrently for speed)
4. **Select** — you browse and pick which articles to include via a CLI menu
5. **Compose** — AI generates a newsletter title and summary based on your selection
6. **Render** — a formatted HTML email is generated from a template
7. **Deliver** — you review email details, manage recipients, and send

---

## AI Models

ellie! uses Google GenAI models via the Google AI API. By default it runs on **Gemma** (`gemma-4-31b-it`), which offers 1500 requests/day on the free tier — plenty for regular use.

Gemini support is also available in the codebase but requires modifying the source code directly. This is intended for developers who want to experiment with different models.

---

## Tagging

ellie! currently tags articles according to the A-Level English Language and Linguistics (ELL) 9508 syllabus, specifically:

- **P2SA** — Language Variation and Change
- **P2SB** — Language, Culture, and Identity

Support for custom, user-defined tag systems is planned for a future release.

---

## Settings

After first launch, you can access settings from the main menu to:
- Add or remove feeds
- Manage your address book (recipients and groups)
- Update your sender email or AI key

---

## Version

`v1.1.0`