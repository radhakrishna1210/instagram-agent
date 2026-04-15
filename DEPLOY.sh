#!/bin/bash
# Instagram Agent - Deployment Quick Start Script
# Run these commands in order to deploy to Railway

echo "======================================================================="
echo "Instagram Agent - Git & Deployment Setup"
echo "======================================================================="
echo ""

# Step 1: Initialize git repository
echo "[1/5] Initializing git repository..."
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
echo "✓ Git initialized"
echo ""

# Step 2: Add all files (respecting .gitignore)
echo "[2/5] Adding files to git (respecting .gitignore)..."
git add .
echo "✓ Files staged"
echo ""

# Step 3: Show what will be committed
echo "[3/5] Files to be committed:"
git status
echo ""

# Step 4: Commit
echo "[4/5] Creating commit..."
git commit -m "Initial Instagram agent - AI & Tech news automation"
echo "✓ Commit created"
echo ""

# Step 5: Create GitHub repo using GitHub CLI
echo "[5/5] Creating GitHub repository..."
echo "This will open your browser to create the repo at github.com"
echo ""
echo "After creating the repo, run these commands:"
echo ""
echo "  git branch -M main"
echo "  git remote add origin https://github.com/YOUR_USERNAME/instagram-agent.git"
echo "  git push -u origin main"
echo ""
echo "======================================================================="
echo "Deployment Instructions:"
echo "======================================================================="
echo ""
echo "1. Go to https://railway.app"
echo "2. Sign up with GitHub"
echo "3. Create new project → Deploy from GitHub repo"
echo "4. Select 'instagram-agent' repository"
echo "5. Wait for deployment to complete"
echo "6. Go to Variables tab and add all .env variables"
echo "7. Watch Logs tab for real-time output"
echo ""
echo "======================================================================="
