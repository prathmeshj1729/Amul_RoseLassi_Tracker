# Amul Rose Lassi Stock Tracker

Monitors Amul High Protein Rose Lassi stock and sends Telegram notifications when available.

## Features

- ✅ Automatic Cloudflare bypass using cloudscraper
- ✅ Auto-refresh cookies when expired
- ✅ Telegram notifications
- ✅ Retry logic with exponential backoff
- ✅ Checks every 5 minutes with random jitter

## Quick Deploy to Railway (Recommended)

1. **Push to GitHub:**

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Railway:**

   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select this repository
   - Add environment variables:
     - `TELEGRAM_TOKEN` = your_bot_token
     - `CHAT_ID` = your_chat_id
     - `CHECK_INTERVAL` = 300
     - `CF_CLEARANCE` = your_cloudflare_cookie
     - `JSESSIONID` = your_session_cookie
     - `CFUVID` = your_cfuvid_cookie
     - `CF_BM` = your_cf_bm_cookie
     - `EXT_NAME` = ojplmecpdpgccookcobabopnaifgidhf
   - Deploy!

3. **That's it!** Your tracker runs 24/7 in the cloud.

## Alternative: Render.com

1. **Push to GitHub** (same as above)
2. Go to [render.com](https://render.com)
3. New → Background Worker
4. Connect GitHub repo
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python tracker.py`
7. Add environment variables (same as Railway)
8. Create service!

## Local Testing

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run
python tracker.py
```

## Environment Variables

Required:

- `TELEGRAM_TOKEN` - Your Telegram bot token from @BotFather
- `CHAT_ID` - Your Telegram chat ID

Optional:

- `CHECK_INTERVAL` - Seconds between checks (default: 300)
- `CF_CLEARANCE`, `JSESSIONID`, `CFUVID`, `CF_BM`, `EXT_NAME` - Cloudflare cookies

## Monitoring

The tracker sends Telegram notifications for:

- ✅ Startup confirmation
- ✅ Product in stock (with price and link)
- ⚠️ Critical errors

Check logs for detailed monitoring.
