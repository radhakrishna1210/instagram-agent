# 🚀 Deploying Instagram AI Agent to Railway

Railway is a great platform for hosting this background scheduler. Since the project includes a `Procfile` and `requirements.txt`, deployment is almost entirely automatic.

## 📥 Prerequisite
Your code is already pushed to GitHub: `https://github.com/radhakrishna1210/instagram-agent.git`

---

## 🛠️ Step-by-Step Instructions

### 1. Create a Railway Project
1.  Go to [Railway.app](https://railway.app/) and sign in.
2.  Click **+ New Project**.
3.  Select **Deploy from GitHub repo**.
4.  Choose your repository: `radhakrishna1210/instagram-agent`.
5.  Click **Deploy Now**. 

### 2. Configure Environment Variables
Railway won't have your `.env` file, so you must add them manually:
1.  In your Railway project, click on the service (`instagram-agent`).
2.  Go to the **Variables** tab.
3.  Click **New Variable** and add the following keys with their values from your local `.env`:
    *   `GEMINI_API_KEY`
    *   `INSTAGRAM_ACCOUNT_ID`
    *   `INSTAGRAM_ACCESS_TOKEN`
    *   `CLOUDINARY_CLOUD_NAME`
    *   `CLOUDINARY_API_KEY`
    *   `CLOUDINARY_API_SECRET`
    *   `POST_TIME_MORNING` (e.g., `09:00`)
    *   `POST_TIME_EVENING` (e.g., `18:00`)
    *   `FACEBOOK_APP_ID` (optional)
    *   `FACEBOOK_APP_SECRET` (optional)

### 3. Set the Start Command
Railway should detect the `Procfile`, but to be safe, you can explicitly set the start command:
1.  Go to the **Settings** tab of your service.
2.  Under **Deploy**, look for **Start Command**.
3.  Set it to: `python scheduler.py`
4.  Railway will automatically redeploy.

### 4. Verify Deployment
1.  Go to the **View Logs** tab.
2.  You should see:
    *   `[Scheduler] Initialized with times: 09:00, 18:00`
    *   `[Scheduler] ✓ Background scheduler started`
    *   `[Scheduler] ✓ Ready. Press Ctrl+C to stop.`

---

## ⚡ Important Notes

> [!IMPORTANT]
> **Plan Type**: Ensure you are using a plan that allows background workers to run 24/7. The basic trial might sleep if there is no web traffic. 

> [!TIP]
> **Timezone**: Railway servers usually run on **UTC**. If your `POST_TIME` is set to `09:00`, it will post at 9:00 AM UTC. Adjust these variables in the Railway dashboard if you want it to post at specific times in your local timezone. (e.g., if you are in IST, UTC is 5.5 hours behind, so set morning to `03:30` for 9:00 AM IST).

> [!CAUTION]
> **Persistent Storage**: Railway's file system is ephemeral (resets on each deploy). The `posted_urls.json` file will reset when you update the code. For a production-ready solution, you would use a Railway Redis or Postgres database, but for now, it's fine for daily runs!
