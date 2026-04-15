# Instagram Agent - AI & Tech News Automation

Automatic Instagram posting bot that fetches AI & tech news, generates engaging captions with Gemini AI, creates images with Pollinations.ai, and posts to Instagram using the Meta Graph API.

**Features:**
- ✅ Automated daily posting (configurable times)
- ✅ AI-powered caption generation (Google Gemini)
- ✅ Intelligent image generation (Pollinations.ai)
- ✅ Duplicate post prevention
- ✅ Free tier compatible (all free APIs)
- ✅ One-click deployment to Railway.app

---

## Quick Start

### Prerequisites
- Python 3.11+
- Git
- Instagram Creator/Business account
- API keys (all free tier):
  - Google Gemini API key
  - Meta App ID & Access Token for Instagram Graph API

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/instagram-agent.git
   cd instagram-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```
   GEMINI_API_KEY=your_key_here
   INSTAGRAM_ACCOUNT_ID=your_account_id
   INSTAGRAM_ACCESS_TOKEN=your_token
   POST_TIME_MORNING=09:00
   POST_TIME_EVENING=18:00
   ```

5. **Test the agent**
   ```bash
   python main.py
   ```
   This will fetch news, generate content, and attempt to post (once).

6. **Run scheduler for continuous posting**
   ```bash
   python scheduler.py
   ```
   This schedules automatic posts at the configured times daily.

---

## File Structure

```
instagram-agent/
├── main.py              # Main orchestrator (fetch → generate → post)
├── fetcher.py           # Fetches AI/Tech news from RSS feeds
├── generator.py         # Generates captions (Gemini) + images (Pollinations)
├── poster.py            # Posts to Instagram via Meta Graph API
├── scheduler.py         # Schedules posts at configured times
├── requirements.txt     # Python dependencies
├── .env                 # Configuration (local only, not committed)
├── .gitignore           # Git ignore rules
├── Procfile             # Railway.app deployment
├── runtime.txt          # Python version for Railway
├── logs.txt             # Execution log (auto-created)
├── posted_urls.json     # Duplicate prevention (auto-created)
└── README.md            # This file
```

---

## API Keys - Where to Get Them

### 1. Google Gemini API Key (Free)
- Go to: https://aistudio.google.com/app/apikeys
- Click "Create API Key"
- Free tier: 60 requests/min, 1,500 requests/day
- Copy key to `.env`

### 2. Instagram Graph API Credentials
**Account Setup:**
1. Convert Instagram account to Creator or Business account
2. Create Facebook App: https://developers.facebook.com/apps
3. Add "Instagram Graph API" product
4. Get App ID and App Secret
5. Generate long-lived access token

**In your `.env`:**
```
INSTAGRAM_ACCOUNT_ID=your_account_id
INSTAGRAM_ACCESS_TOKEN=your_long_lived_token
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
```

### 3. Pollinations.ai (Free - No Key Needed)
- No API key required
- Free tier: unlimited image generation

---

## Configuration

Edit `.env` to customize:

```env
# Posting times (24-hour format)
POST_TIME_MORNING=09:00
POST_TIME_EVENING=18:00

# Only news containing these keywords are posted
# (configured in fetcher.py - AI, machine learning, GPT, LLM, robot, etc.)

# Duplicate prevention
# Keeps last 50 posted URLs in posted_urls.json
```

---

## Deployment to Railway.app (Free)

### Step 1: Prepare for Deployment

1. **Initialize git repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Instagram Agent setup"
   ```

2. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/yourusername/instagram-agent.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Railway

1. Go to https://railway.app/
2. Sign up (free with GitHub)
3. Click "New Project" → "Deploy from GitHub"
4. Select your `instagram-agent` repository
5. Railway automatically detects Python and reads `Procfile` + `runtime.txt`
6. Wait for deployment to complete

### Step 3: Add Environment Variables in Railway Dashboard

**After deployment:**

1. Go to your Railway project dashboard
2. Click on the "Variables" tab (or settings icon)
3. Add each environment variable **individually**:
   - Click "New Variable"
   - Enter key: `GEMINI_API_KEY`
   - Enter value: `your_actual_key_here`
   - Click "Add"
4. Repeat for all required variables:
   ```
   GEMINI_API_KEY
   INSTAGRAM_ACCOUNT_ID
   INSTAGRAM_ACCESS_TOKEN
   FACEBOOK_APP_ID
   FACEBOOK_APP_SECRET
   POST_TIME_MORNING
   POST_TIME_EVENING
   ```

5. After adding all variables, Railway will **automatically restart** the service

### Step 4: Monitor Logs

1. In Railway dashboard, go to "Logs" tab
2. You'll see real-time output from `scheduler.py`
3. Check for successful posts at scheduled times

---

## Troubleshooting

### "GEMINI_API_KEY not found in .env"
- Make sure `.env` file is in project root
- Check that variable name is exactly `GEMINI_API_KEY`
- On Railway: Add via Variables tab (not in Procfile)

### "Instagram token validation failed"
- Token may have expired (long-lived tokens last ~60 days)
- Regenerate token on developers.facebook.com
- Update in Railway Variables

### "No articles found"
- RSS feeds might be down
- Check `fetcher.py` - news sources are hardcoded
- Verify internet connectivity

### Scheduler not running posts
- Check Railway logs for errors
- Verify `POST_TIME_MORNING` and `POST_TIME_EVENING` format (HH:MM)
- Confirm timezone is set correctly (uses server timezone)

---

## Logs

- **Local**: `logs.txt` - Text log of all posting attempts
- **Railway**: View in "Logs" tab of Railway dashboard
- **Format**: `[YYYY-MM-DD HH:MM] STATUS | Article Title`

---

## Security Notes

⚠️ **Never commit `.env` to git!**
- `.env` is in `.gitignore` for this reason
- API keys should only live in:
  - Local `.env` (never commit)
  - Railway Variables (encrypted by Railway)

✅ **Safe to commit:**
- `main.py`, `fetcher.py`, `generator.py`, etc. (no secrets)
- `requirements.txt` (dependencies only)
- `Procfile`, `runtime.txt` (deployment config)

---

## How It Works

### Pipeline (6 Steps)
1. **Fetch** - Get latest AI/Tech news from 3 RSS feeds
2. **Filter** - Keep only articles with AI keywords
3. **Deduplicate** - Skip if URL already posted
4. **Generate Caption** - Use Gemini AI to write engaging caption
5. **Generate Image** - Create image with Pollinations.ai
6. **Post** - Upload to Instagram via Meta Graph API

### Scheduling
- Runs at `POST_TIME_MORNING` every day
- Runs at `POST_TIME_EVENING` every day
- Uses APScheduler for precise timing
- Automatically retries if a job is missed

### Duplicate Prevention
- Stores posted URLs in `posted_urls.json`
- Keeps last 50 URLs (prevents unbounded growth)
- Skips articles if URL already posted

---

## License

MIT

---

## Support

For issues:
1. Check `logs.txt` (local) or Railway logs (cloud)
2. Verify all environment variables are set
3. Ensure APIs are accessible (not rate-limited)
4. Check that Instagram account is Creator/Business type

---

## Next Steps

- [ ] Get API keys and update `.env`
- [ ] Test locally: `python main.py`
- [ ] Verify logs: check `logs.txt`
- [ ] Deploy to Railway
- [ ] Add Railway environment variables
- [ ] Monitor first scheduled post
- [ ] Adjust `POST_TIME_MORNING` and `POST_TIME_EVENING` as needed

Happy posting! 🚀📱
