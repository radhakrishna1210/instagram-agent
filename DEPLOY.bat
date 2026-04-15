@echo off
REM Instagram Agent - Deployment Quick Start Script (Windows)
REM Run these commands in order to deploy to Railway

setlocal enabledelayedexpansion

echo ======================================================================
echo Instagram Agent - Git ^& Deployment Setup
echo ======================================================================
echo.

REM Step 1: Initialize git repository
echo [1/5] Initializing git repository...
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
echo.✓ Git initialized
echo.

REM Step 2: Add all files (respecting .gitignore)
echo [2/5] Adding files to git (respecting .gitignore)...
git add .
echo ✓ Files staged
echo.

REM Step 3: Show what will be committed
echo [3/5] Files to be committed:
git status
echo.

REM Step 4: Commit
echo [4/5] Creating commit...
git commit -m "Initial Instagram agent - AI and Tech news automation"
echo ✓ Commit created
echo.

REM Step 5: Next steps
echo [5/5] Next steps:
echo.
echo Before pushing, create a GitHub repository:
echo.
echo Option A - Using GitHub CLI (if installed):
echo   gh repo create instagram-agent --source=. --remote=origin --push
echo.
echo Option B - Manual steps:
echo   1. Go to https://github.com/new
echo   2. Create repo called "instagram-agent"
echo   3. Copy the HTTPS URL
echo   4. Run: git remote add origin HTTPS_URL_HERE
echo   5. Run: git branch -M main
echo   6. Run: git push -u origin main
echo.

echo ======================================================================
echo Railway.app Deployment Instructions
echo ======================================================================
echo.
echo 1. Go to https://railway.app
echo 2. Sign up with GitHub
echo 3. Click "New Project"
echo 4. Select "Deploy from GitHub"
echo 5. Authorize Railway to access your GitHub account
echo 6. Select "instagram-agent" repository
echo 7. Wait for deployment to complete (2-3 minutes)
echo 8. Click on your project, then "Variables" tab
echo 9. Add these environment variables:
echo.
echo    GEMINI_API_KEY = your_key_here
echo    INSTAGRAM_ACCOUNT_ID = your_account_id
echo    INSTAGRAM_ACCESS_TOKEN = your_token
echo    FACEBOOK_APP_ID = your_app_id
echo    FACEBOOK_APP_SECRET = your_app_secret
echo    POST_TIME_MORNING = 09:00
echo    POST_TIME_EVENING = 18:00
echo.
echo 10. Click "View Logs" to monitor in real-time
echo 11. Your agent will automatically post at scheduled times!
echo.
echo ======================================================================

pause
