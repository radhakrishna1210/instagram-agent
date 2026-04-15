# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Instagram Agent is an automated content posting bot that fetches AI & Tech news, generates Instagram-ready captions and images, and posts to Instagram. It can run in three modes:
1. **Single execution** (`main.py`) - fetch, generate, and post one article
2. **Scheduled** (`scheduler.py`) - automated posts at configured times (morning/evening)
3. **Webhook** (`webhook_handler.py`) - manual posts triggered via Typeform or API

## Core Architecture

The pipeline has four independent modules that compose into a single flow:

- **`fetcher.py`** - Fetches AI/Tech news from 3 RSS feeds (TechCrunch, MIT Tech Review, The Verge). Filters articles by AI-related keywords. Returns list of article dicts with: `title`, `summary`, `url`, `source`.
  
- **`generator.py`** - Takes an article dict and generates two things: (1) Instagram caption using Google Gemini (up to 220 chars, 8 hashtags), (2) image URL from Pollinations.ai (always 1080x1080). Returns dict with `caption` and `image_url`.
  
- **`poster.py`** - Posts to Instagram via Meta Graph API. Two-step process: create media container → publish. Validates token, checks expiry, can refresh tokens. Requires Business/Creator Instagram account.
  
- **`main.py`** - Orchestrator that chains all modules: fetch → deduplicate → generate → post. Manages posted URL history in `posted_urls.json` (keeps last 50 to prevent duplicates). Logs all results to `logs.txt`.

- **`scheduler.py`** - Uses APScheduler to run `main.run_agent()` at two configurable times daily (POST_TIME_MORNING, POST_TIME_EVENING). Keeps scheduler process running indefinitely. Handles missed jobs with 10-minute grace period.

- **`webhook_handler.py`** - FastAPI app that accepts POST submissions (Typeform or manual). Creates article from form data and posts via generator + poster. Processes requests in background tasks for instant response.

## Key Implementation Details

### Duplicate Prevention
Posted URLs are stored in `posted_urls.json` as a dict with `urls` list and `last_updated` timestamp. The list is trimmed to 50 URLs to prevent unbounded growth. Always check `is_already_posted()` before generating/posting.

### Environment Variables Required
- `GEMINI_API_KEY` - Google Gemini API (free tier: 1,500 requests/day)
- `INSTAGRAM_ACCOUNT_ID` - 17-digit Instagram Business account ID
- `INSTAGRAM_ACCESS_TOKEN` - Long-lived Meta token (expires ~60 days)
- `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET` - For token refresh (optional but recommended)
- `POST_TIME_MORNING`, `POST_TIME_EVENING` - HH:MM format (optional, defaults to 09:00 and 18:00)

No `.env` is committed. `.env` must exist locally and in Railway's Variables tab for deployment.

### Logging Strategy
- **Console**: Info-level logs with timestamps and status indicators (✓, ✗, ⚠)
- **File (`logs.txt`)**: Simple format `[TIMESTAMP] STATUS | ARTICLE_TITLE` for tracking post history
- **Railway**: Same console output visible in "Logs" tab of Railway dashboard

### API Boundaries & Error Handling
- **Gemini failures** fall back to a generic caption template (doesn't fail the post)
- **Pollinations** is called but never fails (it's just a URL builder with randomized seed)
- **Instagram API failures** are explicit and fatal (token validation, container creation, publishing all checked)
- **Feed parsing failures** skip individual feeds but continue with others
- Always validate token before posting (`check_token_valid()`)

### Testing
Each module has a standalone `test_*` function:
- `test_fetcher.py` - Fetch articles from feeds and print first result
- `test_generator.py` - Generate caption and image for dummy article
- `poster.py` has inline `main()` that validates token and optionally refreshes it

Run with: `python test_*.py` or `python module.py`

## Common Commands

### Development & Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Test news fetching
python test_fetcher.py

# Test content generation (caption + image)
python test_generator.py

# Test Instagram posting credentials
python poster.py

# Run full pipeline once
python main.py

# Run scheduled posting (Ctrl+C to stop)
python scheduler.py

# Run webhook API server (for Typeform)
python webhook_handler.py
```

### Environment Setup
```bash
# Copy example to .env and edit
cp .env.example .env
# Then add your actual API keys to .env
```

## Deployment Notes

- **Local**: `.env` file in project root
- **Railway**: Add each variable individually in Variables tab (not in Procfile)
- **Procfile** defines entry point: `python scheduler.py` for production
- **runtime.txt** specifies Python 3.11+
- Railway auto-redeploys on git push to main branch

Token refresh is automatic but only if `FACEBOOK_APP_ID` and `FACEBOOK_APP_SECRET` are set. Long-lived tokens expire ~60 days; refresh before that or manually regenerate on developers.facebook.com.

## Code Style Notes

- Use print statements for user-facing messages (fetcher, generator)
- Use logging module for operational logs (main, scheduler, poster)
- Modules are designed to be importable and testable independently
- No circular imports; scheduler imports run_agent from main only when called
- Exception messages are user-friendly and include remediation hints
- All external API calls have timeouts (10-15 seconds)
