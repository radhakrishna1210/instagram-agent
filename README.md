# 🤖 Instagram AI Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange?logo=google&logoColor=white)
![Instagram](https://img.shields.io/badge/Instagram%20API-Graph%20v19-purple?logo=instagram&logoColor=white)
![Cloudinary](https://img.shields.io/badge/Cloudinary-Image%20Hosting-blue?logo=cloudinary&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**A fully automated Instagram content pipeline for AI & Tech news.**  
Fetches trending articles → generates carousel posts with AI captions → posts to Instagram — on a schedule, hands-free.

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Carousel Post Design](#-carousel-post-design)
- [Scheduling](#-scheduling)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

Instagram AI Agent is a Python-based automation tool that runs a complete Instagram content pipeline:

1. **Fetches** the latest AI & Tech news from top RSS feeds (TechCrunch, MIT Tech Review, The Verge)
2. **Generates** an engaging caption with 30 viral hashtags using Google Gemini AI
3. **Creates** a multi-slide carousel post:  
   - **Slide 1**: Cinematic AI-generated cover photo with headline overlay  
   - **Slides 2+**: Topic-relevant background image + bullet-point text from the caption
4. **Uploads** all images to Cloudinary for public hosting
5. **Posts** the carousel to Instagram via Meta Graph API
6. **Schedules** automated posts twice daily (morning & evening)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗞️ **Multi-source news** | Pulls from TechCrunch, MIT Tech Review, The Verge simultaneously |
| 🤖 **AI captions** | Google Gemini 2.5 Flash generates hook-driven, viral captions |
| #️⃣ **Hybrid hashtag system** | 15 article-specific tags (Gemini) + 15 randomly sampled from a curated 2025 AI/tech pool = 30 total, rotated every post |
| 🖼️ **AI image generation** | Pollinations.ai generates cinematic, article-relevant visuals |
| 📸 **Carousel posts** | 3–5 swipeable slides per post for maximum engagement |
| 🎨 **Professional design** | Pillow-generated overlays: gradient, blue accent bars, bullet points |
| ☁️ **Cloud image hosting** | Cloudinary hosts all images for public Instagram-compatible URLs |
| 🔄 **Duplicate prevention** | Tracks posted URLs in `posted_urls.json` — never reposts the same article |
| ⏰ **Auto-scheduler** | APScheduler runs posts at configurable times (default: 9 AM & 6 PM) |
| 🔑 **Dual API keys** | Use separate Gemini keys for morning/evening to double daily quota |
| 🔁 **Token management** | Checks token validity and supports long-lived token refresh |
| 🛡️ **Fallback safety** | Every step has graceful fallbacks — if carousel fails, posts single image |
| 📐 **Dynamic text fitting** | Pixel-accurate word wrap + font-size descent (88→72→60→50px) — text never overflows or gets cut off on any slide |
| 🔁 **Rate-limit resilient** | Batch-round API polling + 403 publish verification — correctly handles Meta's rate limits without false failures |

---

## 🔄 How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    INSTAGRAM AI AGENT PIPELINE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. FETCH      RSS Feeds → Filter AI/Tech keywords             │
│     ↓          (TechCrunch, MIT Tech Review, The Verge)        │
│                                                                 │
│  2. DEDUPE     Check posted_urls.json → skip already-posted    │
│     ↓                                                           │
│                                                                 │
│  3. GENERATE   Gemini AI → Caption body (hook + CTA)           │
│     ↓          Gemini AI → 15 article-specific hashtags        │
│                Curated pool → 15 trending 2025 base hashtags   │
│                                                                 │
│  4. IMAGES     Pollinations.ai → Topic-relevant photo          │
│     ↓          Pillow → Add headline + source overlay          │
│                Pillow → Text slides with BG image + bullets    │
│                                                                 │
│  5. HOST       Cloudinary upload → Get public HTTPS URLs       │
│     ↓                                                           │
│                                                                 │
│  6. POST       Meta Graph API → Create carousel containers     │
│     ↓          Meta Graph API → Publish carousel post          │
│                                                                 │
│  7. LOG        Save URL to history + write to logs.txt         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
instagram-agent/
│
├── main.py              # 🎯 Main orchestrator — runs the full pipeline
├── fetcher.py           # 🗞️  News fetcher — RSS feeds + AI keyword filter
├── generator.py         # 🎨 Content generator — captions, images, carousel slides
├── poster.py            # 📤 Instagram poster — Meta Graph API integration
├── scheduler.py         # ⏰ Scheduler — APScheduler for automated posting
├── webhook_handler.py   # 🔗 FastAPI webhook handler (optional)
│
├── .env                 # 🔐 Environment variables (never commit this!)
├── .env.example         # 📋 Template for environment variables
├── requirements.txt     # 📦 Python dependencies
├── posted_urls.json     # 📝 Duplicate prevention history (auto-generated)
├── logs.txt             # 📊 Execution logs (auto-generated)
│
├── Procfile             # 🚀 Railway/Render entry point
├── runtime.txt          # 🐍 Python version pin
└── README.md            # 📖 This file
```

---

## 📦 Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed ([Download](https://python.org/downloads))
- **Instagram Business or Creator account** (personal accounts won't work)
- **Facebook Developer App** with Instagram Basic Display or Graph API
- **Google AI Studio account** for Gemini API key
- **Cloudinary account** for image hosting (free tier works)

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/radhakrishna1210/instagram-agent.git
cd instagram-agent
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Then edit `.env` with your credentials (see [Configuration](#-configuration) below).

---

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```env
# ── Google Gemini AI ──────────────────────────────────────────────
# Get your free API key at: https://aistudio.google.com/app/apikeys
# Free tier: 20 requests/day per key (gemini-2.5-flash)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: second Gemini key for evening posts (doubles daily quota)
# Morning post uses GEMINI_API_KEY, Evening post uses GEMINI_API_KEY_2
# If not set, evening post falls back to GEMINI_API_KEY
GEMINI_API_KEY_2=your_second_gemini_api_key_here

# ── Instagram Graph API ───────────────────────────────────────────
# Requires Instagram Business or Creator account
# Setup guide: https://developers.facebook.com/docs/instagram-api/getting-started
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token

# ── Facebook App Credentials (optional — for token refresh) ──────
# Get from: https://developers.facebook.com/apps
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# ── Cloudinary (image hosting) ────────────────────────────────────
# Free account at: https://cloudinary.com
# Required: Instagram needs a public HTTPS URL for images
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# ── Scheduler ────────────────────────────────────────────────────
# 24-hour format (HH:MM) — posts happen at these times daily
POST_TIME_MORNING=09:00
POST_TIME_EVENING=18:00
```

### Getting API Credentials

<details>
<summary><b>📱 Instagram Graph API Setup</b></summary>

1. Go to [Facebook Developers](https://developers.facebook.com/apps)
2. Create a new App → Select **Business** type
3. Add **Instagram Graph API** product
4. Connect your Instagram Business/Creator account
5. Generate a **Long-Lived User Access Token** (valid for 60 days)
6. Find your **Instagram Account ID** via:  
   `GET https://graph.facebook.com/v19.0/me/accounts?access_token=YOUR_TOKEN`

</details>

<details>
<summary><b>🤖 Google Gemini API Setup</b></summary>

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key to your `.env` file
5. Free tier includes 60 requests/min and 1,500 requests/day

</details>

<details>
<summary><b>☁️ Cloudinary Setup</b></summary>

1. Sign up at [cloudinary.com](https://cloudinary.com) (free tier: 25GB storage, 25GB bandwidth/month)
2. Go to your **Dashboard**
3. Copy your **Cloud Name**, **API Key**, and **API Secret**
4. Add them to your `.env` file

</details>

---

## 🎮 Usage

### Run once (manual post)

```bash
python main.py
```

This runs the full pipeline once — fetches news, generates content, posts to Instagram immediately.

### Run the auto-scheduler

```bash
python scheduler.py
```

Starts the background scheduler. Posts automatically at the configured morning and evening times every day. Keep this running in a terminal or deploy it to a server.

### Test individual components

```bash
# Test news fetching only
python fetcher.py

# Test content generation (caption + images)
python test_generator.py

# Test Instagram API connection
python poster.py
```

### Example output

```
======================================================================
Instagram Agent - AI & Tech Content Automation
======================================================================

[2026-04-15 09:00:00] INFO - ✓ Environment validated
[2026-04-15 09:00:00] INFO - [1/6] Fetching AI & Tech news...
[2026-04-15 09:00:02] INFO - ✓ Found 9 articles
[2026-04-15 09:00:02] INFO - [2/6] Checking for duplicates...
[2026-04-15 09:00:02] INFO - ✓ Found new article to post
[2026-04-15 09:00:02] INFO - [3/6] Selected: GPT-5 Released with Reasoning Capabilities
[2026-04-15 09:00:05] INFO - [4/6] Generating caption + carousel slides...
[2026-04-15 09:00:08] INFO - ✓ Caption: 187 chars, 30 hashtags
[2026-04-15 09:00:35] INFO - ✓ Carousel ready: 4 slides
[2026-04-15 09:00:35] INFO - [5/6] Image URLs ready...
[2026-04-15 09:00:35] INFO - ✓ Cover image: https://res.cloudinary.com/...
[2026-04-15 09:00:35] INFO - ✓ Text slides: 3 additional slides
[2026-04-15 09:00:36] INFO - [6/6] Posting carousel to Instagram...
[2026-04-15 09:00:40] INFO - ✓ Carousel published! Slides: 4
[2026-04-15 09:00:40] INFO - 📱 View post: https://www.instagram.com/p/ABC123/
```

---

## 🎨 Carousel Post Design

Each post is automatically a **multi-slide Instagram carousel**:

### Slide 1 — Cover Photo
- Cinematic AI-generated image relevant to the article topic (via Pollinations.ai)
- Dark gradient overlay on bottom half for text legibility
- **Bold white headline** with pixel-accurate word wrap and dynamic font sizing (88→72→60→50px) so long titles always fit fully — no cut-off, no overflow
- Blue accent bar `#1E90FF` on the left edge
- Source label at bottom (`AI & Tech • TechCrunch`)

### Slides 2+ — Text Slides
- **Topic-relevant background image** (same subject, different seed = visual variety)
- **65% dark overlay** for text contrast
- `AI & TECH` pill badge centred at top
- **Bullet points** (●) for each sentence from the caption — text pixel-wrapped to always stay within the canvas
- Slide counter at bottom-right (e.g. `3 / 4`)

> **Note:** Hashtags appear only in the Instagram caption text — never on any image slide.

### Color Palette

| Element | Color | Hex |
|---------|-------|-----|
| Accent / bullets | Dodger Blue | `#1E90FF` |
| Body text | Near-white | `#F5F5F5` |
| Labels / counters | Muted blue-grey | `#7890D2` |
| Overlay | Semi-black | `rgba(0,0,0,0.65)` |

---

## ⏰ Scheduling

The scheduler (`scheduler.py`) posts automatically using **APScheduler** with cron triggers.

### Default schedule
- **Morning post**: 9:00 AM daily
- **Evening post**: 6:00 PM daily

### Customize times

Edit your `.env` file:

```env
POST_TIME_MORNING=08:30   # 8:30 AM
POST_TIME_EVENING=20:00   # 8:00 PM
```

### Deploy for 24/7 operation

For always-on operation, deploy to:
- **Railway** or **Render** (free tier available)
- **Heroku** (using `Procfile`)
- **Ubuntu VPS** with `systemd` or `screen`

```bash
# Keep running on a VPS using screen
screen -S instagram-agent
python scheduler.py
# Press Ctrl+A then D to detach
```

---

## 📡 API Reference

| Module | Class / Function | Description |
|--------|-----------------|-------------|
| `fetcher.py` | `NewsFetcher.fetch_latest_ai_news()` | Returns list of article dicts from all RSS feeds |
| `fetcher.py` | `NewsFetcher.get_random_article()` | Returns one random AI/Tech article |
| `generator.py` | `ContentGenerator.generate_caption()` | Generates caption + 30 hashtags via Gemini |
| `generator.py` | `ContentGenerator.generate_carousel_content()` | Returns `{caption, image_urls}` for full carousel |
| `generator.py` | `ContentGenerator.generate_content()` | Returns `{caption, image_url}` for single-image post |
| `poster.py` | `InstagramPoster.post_carousel_to_instagram()` | Posts carousel, falls back to single-image |
| `poster.py` | `InstagramPoster.post_to_instagram()` | Posts a single image |
| `poster.py` | `InstagramPoster.check_token_valid()` | Validates the access token |
| `poster.py` | `InstagramPoster.refresh_access_token()` | Refreshes long-lived token |
| `scheduler.py` | `InstagramScheduler.run()` | Starts the background scheduler |

---

## 🚨 Troubleshooting

### `Missing or incomplete environment variables`
→ Check that your `.env` file exists and all required keys are filled in. Values like `your_key_here` are detected as placeholders.

### `Token validation failed`
→ Your Instagram access token may have expired (tokens last ~60 days).  
Run `python poster.py` to test and refresh.  
Get a new token from [Meta API Explorer](https://developers.facebook.com/tools/explorer/).

### `Cloudinary upload failed`
→ Verify `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET` in `.env`. Check your Cloudinary dashboard for usage limits.

### `No articles found`
→ RSS feeds may be temporarily down. The agent retries across multiple sources (TechCrunch, MIT Tech Review, The Verge).

### `All fetched articles were already posted`
→ All recent articles have been posted. The agent skips duplicates. Wait for new articles to be published, or delete `posted_urls.json` to reset history.

### `Carousel container failed`
→ Instagram has strict requirements on image aspect ratios (1:1 for carousels). The agent automatically falls back to a single-image post.

### `Application request limit reached` (403) on publish
→ This is a known Meta API quirk — the post usually goes live even when the API response returns 403. The bot automatically verifies by querying your account's most recent media. If confirmed live within 2 minutes, it counts as a success and the article is marked as posted so it won't be re-attempted.

### Text cut off or overflowing on carousel images
→ Fixed in the current version. All text rendering now uses pixel-accurate word wrapping via `draw.textlength()` with dynamic font-size descent (88→72→60→50px). Text is guaranteed to stay within the 1080×1080 canvas.

### Gemini quota exceeded (429 error)
→ The `gemini-2.5-flash` free tier allows **1,500 requests/day**. Each post uses ~4 requests (caption body + hashtags + cover image prompt + slide BG prompt).  
**Fix:** Add a `GEMINI_API_KEY_2` in your `.env` (or Railway Variables) so morning and evening posts use separate keys, doubling your daily quota.  
Alternatively, upgrade to a paid Gemini plan at [Google AI Studio](https://aistudio.google.com).

---

## 🔒 Security Notes

> [!CAUTION]
> **Never commit your `.env` file to version control.** It contains your private API keys and access tokens. The `.gitignore` already excludes it, but double-check before pushing.

- Rotate your Instagram access token every 60 days (or use the built-in refresh)
- Do not share your `FACEBOOK_APP_SECRET` or `CLOUDINARY_API_SECRET`
- Use environment variables on deployment platforms instead of `.env` files

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

### Ideas for contributions
- [ ] Support for video Reels generation
- [ ] Multi-language caption support
- [ ] Analytics tracking (likes, comments, reach)
- [ ] Web dashboard for monitoring
- [ ] Support for Twitter/X cross-posting

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License — free to use, modify, and distribute with attribution.
```

---

## 🙏 Acknowledgements

- [Google Gemini](https://deepmind.google/technologies/gemini/) — AI caption & hashtag generation
- [Pollinations.ai](https://pollinations.ai) — Free AI image generation
- [Cloudinary](https://cloudinary.com) — Image hosting & CDN
- [Meta Graph API](https://developers.facebook.com/docs/instagram-api/) — Instagram posting
- [APScheduler](https://apscheduler.readthedocs.io/) — Python job scheduling
- [Pillow](https://pillow.readthedocs.io/) — Image processing & design

---

<div align="center">

Made with ❤️ for the AI & Tech community

⭐ **Star this repo if it helped you!** ⭐

</div>
