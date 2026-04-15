# Instagram Agent - Complete Deployment Guide

## Prerequisites

Before starting, ensure you have:

- ✅ Git installed: https://git-scm.com/download/win
- ✅ GitHub account: https://github.com/signup
- ✅ GitHub CLI (optional but recommended): https://cli.github.com/
- ✅ All API keys in your `.env` file
- ✅ Railway.app account: https://railway.app (sign up with GitHub)

---

## Step 1: Initialize Git & Commit

Run these commands in order in your terminal (PowerShell or Command Prompt):

```powershell
# Navigate to project folder
cd D:\Projects\instagram-agent

# Initialize git repository
git init

# Configure git (replace with your info)
git config user.name "Your Name"
git config user.email "your.email@gmail.com"

# Add all files (automatically respects .gitignore)
git add .

# Verify files to be committed
git status

# Commit with message
git commit -m "Initial Instagram agent - AI and Tech news automation"
```

**Expected output:**
```
[main (root-commit) 1a2b3c4] Initial Instagram agent - AI and Tech news automation
 12 files changed, 1234 insertions(+)
 create mode 100644 main.py
 create mode 100644 fetcher.py
 create mode 100644 generator.py
 create mode 100644 poster.py
 create mode 100644 scheduler.py
 create mode 100644 requirements.txt
 create mode 100644 .gitignore
 create mode 100644 Procfile
 create mode 100644 runtime.txt
 create mode 100644 README.md
```

---

## Step 2: Create GitHub Repository

### Option A: Using GitHub CLI (Recommended)

```powershell
# Create public repo on GitHub and push code
gh repo create instagram-agent --source=. --remote=origin --push --public

# Verify it was pushed
git remote -v
```

Expected output:
```
origin  https://github.com/YOUR_USERNAME/instagram-agent.git (fetch)
origin  https://github.com/YOUR_USERNAME/instagram-agent.git (push)
```

### Option B: Manual Steps (No CLI)

1. Go to https://github.com/new
2. Enter repository name: `instagram-agent`
3. Select "Public"
4. **DO NOT** initialize with README (you already have one)
5. Click "Create repository"
6. Copy the HTTPS URL (looks like: `https://github.com/YOUR_USERNAME/instagram-agent.git`)
7. Run these commands:

```powershell
# Rename branch to main (if needed)
git branch -M main

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/instagram-agent.git

# Push code
git push -u origin main
```

**Expected output:**
```
Enumerating objects: 12, done.
Counting objects: 100% (12/12), done.
Delta compression using up to 8 threads
Compressing objects: 100% (11/11), done.
Writing objects: 100% (12/12), 4.56 KiB | 4.56 MiB/s, done.
Total 12 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/YOUR_USERNAME/instagram-agent.git
 * [new branch]      main -> main
Branch 'main' is set up to track remote branch 'main' from 'origin'.
```

✅ Code is now on GitHub!

---

## Step 3: Deploy to Railway.app

### 3.1: Connect GitHub to Railway

1. Go to https://railway.app/dashboard
2. Sign in with GitHub (if not already logged in)
3. Click **"New Project"** (top right)
4. Select **"Deploy from GitHub repo"**
5. Click **"Configure GitHub App"** if prompted
6. Authorize Railway to access your GitHub account
7. Select your `instagram-agent` repository from the list
8. Click **"Deploy"**

⏳ **Wait 2-3 minutes** for Railway to build and deploy

### 3.2: Check Deployment Status

1. After deployment completes, you'll see your project dashboard
2. You should see:
   - Green checkmark ✓ (deployment successful)
   - Service named "instagram-agent" 
   - "Logs" tab showing output
   - "Settings" or "Variables" tab

### 3.3: Add Environment Variables

**This is critical!** Without these, your agent won't work.

1. In Railway dashboard, click **"Variables"** tab
   - Or click the gear icon → "Settings" → "Variables"

2. Click **"New Variable"** for each of these:

```
Variable Name: GEMINI_API_KEY
Value: [your actual Gemini API key]
Click "Add"

Variable Name: INSTAGRAM_ACCOUNT_ID
Value: [your Instagram business account ID]
Click "Add"

Variable Name: INSTAGRAM_ACCESS_TOKEN
Value: [your long-lived Meta access token]
Click "Add"

Variable Name: FACEBOOK_APP_ID
Value: [your Facebook app ID]
Click "Add"

Variable Name: FACEBOOK_APP_SECRET
Value: [your Facebook app secret]
Click "Add"

Variable Name: POST_TIME_MORNING
Value: 09:00
Click "Add"

Variable Name: POST_TIME_EVENING
Value: 18:00
Click "Add"
```

✅ **After adding each variable, Railway automatically restarts** the service

### 3.4: Verify Deployment

1. Go to **"Logs"** tab
2. You should see output like:

```
======================================================================
Instagram Agent - Scheduler
======================================================================

✓ Environment validated
✓ Logging to: logs.txt
[Scheduler] Initialized with times: 09:00, 18:00
[Scheduler] Scheduled morning post at 09:00 daily
[Scheduler] Scheduled evening post at 18:00 daily
[Scheduler] ✓ Background scheduler started

[Scheduler] Next scheduled posts:
  Morning: 2026-04-16 09:00:00
  Evening: 2026-04-15 18:00:00
  Next run: 2026-04-15 18:00:00

[Scheduler] ✓ Ready. Press Ctrl+C to stop.
```

✅ **If you see this, deployment is successful!**

---

## Step 4: Monitor Your Agent

### Real-Time Logs

1. In Railway dashboard, stay in **"Logs"** tab
2. Watch for scheduled posts at your configured times:

```
[2026-04-15 18:00:00] INFO - ======================================================================
[Evening Post] Starting scheduled post...
[2026-04-15 18:00:05] INFO - [1/6] Fetching AI & Tech news...
[2026-04-15 18:00:07] INFO - ✓ Found 9 articles
[2026-04-15 18:00:08] INFO - [3/6] Selecting article...
[2026-04-15 18:00:10] INFO - [4/6] Generating Instagram caption...
[2026-04-15 18:00:15] INFO - ✓ Caption generated
[2026-04-15 18:00:16] INFO - [5/6] Generating image URL...
[2026-04-15 18:00:17] INFO - [6/6] Posting to Instagram...
[2026-04-15 18:00:22] INFO - ✓ Successfully posted to Instagram!
[2026-04-15 18:00:23] INFO - ✓ PASS: Post was successful
```

### Local Logs

Your logs are also stored in Railway's file system:
- Open Railway dashboard → Settings → File Storage
- Download `logs.txt` to see all posts

---

## Step 5: Troubleshooting

### ❌ "GEMINI_API_KEY not found"

**Cause:** Environment variable not set in Railway

**Fix:**
1. Go to Railway dashboard → Variables
2. Verify `GEMINI_API_KEY` exists with correct value
3. Railway will auto-restart after you add it

### ❌ "Instagram token validation failed"

**Cause:** Token may have expired (long-lived tokens last ~60 days)

**Fix:**
1. Regenerate token on https://developers.facebook.com/
2. Update `INSTAGRAM_ACCESS_TOKEN` in Railway Variables
3. Service auto-restarts

### ❌ "No articles found"

**Cause:** RSS feeds might be temporarily down or API rate limited

**Fix:**
- Wait a few minutes and check logs again
- Verify fetcher.py feed URLs are accessible
- Check that you have internet connectivity

### ❌ Service keeps restarting

**Cause:** Likely an error in code or missing .env variable

**Fix:**
1. Check Logs tab for error messages
2. Verify all required variables are set (see Step 3.3)
3. Test locally: `python main.py` to catch errors

---

## Step 6: Updates & Maintenance

### Push Code Updates

1. Make changes locally
2. Commit and push to GitHub:

```powershell
git add .
git commit -m "Fix: [description]"
git push origin main
```

3. Railway automatically redeploys within 1-2 minutes

### Update Environment Variables

1. Go to Railway dashboard → Variables
2. Click on variable to edit
3. Change value
4. Service auto-restarts

### Refresh Access Token

When your long-lived token expires (~60 days):

1. Go to https://developers.facebook.com/
2. Generate new long-lived token
3. Update `INSTAGRAM_ACCESS_TOKEN` in Railway Variables
4. Done!

---

## How It Works on Railway

```
Railway watches GitHub repo
           ↓
You push code → Railway auto-deploys
           ↓
Procfile says: "python scheduler.py"
           ↓
Scheduler starts & reads .env variables
           ↓
At 09:00 AM: Run agent (post)
At 06:00 PM: Run agent (post)
           ↓
Logs visible in Railway dashboard
           ↓
Posts appear on your Instagram! ✓
```

---

## Success Checklist

- ✅ Code pushed to GitHub
- ✅ Railway project created
- ✅ All environment variables set
- ✅ Logs show scheduler started successfully
- ✅ Next scheduled time is visible in logs
- ✅ At scheduled time, agent posts to Instagram
- ✅ Check your Instagram profile for the new post

---

## Costs

✅ **Completely FREE!**
- Railway: Free tier includes enough for this agent
- Gemini API: Free tier (1,500 requests/day)
- Pollinations.ai: Free tier
- Instagram Graph API: Free
- GitHub: Free public repos

---

## Need Help?

1. Check `logs.txt` (local) or Railway Logs (cloud)
2. Verify all environment variables are set
3. Test locally: `python main.py`
4. Check that RSS feeds are accessible
5. Ensure Instagram account is Creator/Business type

---

**You're all set! Your Instagram agent is now running 24/7 on Railway.app** 🚀📱
