# Amul Rose Lassi Stock Tracker 🥛

Automated 24/7 stock monitoring for **Amul High Protein Rose Lassi** with instant Telegram notifications.

## ✨ Features

- ✅ **Automatic Cloudflare bypass** using cloudscraper
- ✅ **Auto-refresh cookies** when expired (401/403 handling)
- ✅ **Instant Telegram notifications** when product is in stock
- ✅ **Smart retry logic** with exponential backoff
- ✅ **Random jitter** to avoid detection
- ✅ **Checks every 5 minutes** (configurable)
- ✅ **Free 24/7 cloud hosting** on Render

---

## 🚀 Quick Deploy to Render.com (Recommended)

### Prerequisites

- GitHub account
- Telegram bot token (get from [@BotFather](https://t.me/BotFather))
- Telegram chat ID (get from [@userinfobot](https://t.me/userinfobot))

### Deployment Steps

1. **Fork/Clone this repository to GitHub**

2. **Sign up on Render:**

   - Go to https://render.com
   - Sign up with GitHub (free account)

3. **Create a New Background Worker:**

   - Click **"New +"** → **"Background Worker"**
   - Select this repository
   - Render auto-detects settings from `render.yaml`

4. **Add Environment Variables:**
   Go to "Environment" tab and add:

   | Variable         | Value                              | Description                    |
   | ---------------- | ---------------------------------- | ------------------------------ |
   | `TELEGRAM_TOKEN` | `your_bot_token`                   | From @BotFather                |
   | `CHAT_ID`        | `your_chat_id`                     | From @userinfobot              |
   | `CHECK_INTERVAL` | `300`                              | Seconds between checks (5 min) |
   | `CF_CLEARANCE`   | `your_cookie`                      | Cloudflare clearance cookie    |
   | `JSESSIONID`     | `your_cookie`                      | Session cookie                 |
   | `CFUVID`         | `your_cookie`                      | Cloudflare UUID                |
   | `CF_BM`          | `your_cookie`                      | Cloudflare bot management      |
   | `EXT_NAME`       | `ojplmecpdpgccookcobabopnaifgidhf` | Extension name                 |

5. **Deploy!**
   - Click "Create Background Worker"
   - Monitor logs to verify it's running
   - You'll receive a Telegram notification confirming startup

---

## 🍪 How to Get Cloudflare Cookies

1. **Open Browser DevTools** (F12)
2. **Go to Network tab**
3. **Visit** https://shop.amul.com/
4. **Find any request** to `shop.amul.com`
5. **Copy cookies from Request Headers:**
   - `cf_clearance`
   - `jsessionid`
   - `_cfuvid`
   - `__cf_bm`

**Note:** These cookies expire periodically. The tracker has auto-refresh logic, but you may need to update them manually if you see repeated 401 errors.

---

## 📊 Monitoring

### On Render:

- **Logs:** Dashboard → Your service → Logs
- **Restart:** Dashboard → Your service → Manual Deploy → Deploy latest commit

### Telegram Notifications:

- ✅ **Startup confirmation** when tracker starts
- ✅ **Product in stock** alert with price and link
- ⚠️ **Error alerts** for critical issues

### Log Messages:

```
2025-10-02 04:42:34 - INFO - Amul Rose Lassi Stock Tracker Started
2025-10-02 04:42:35 - INFO - Check #1 at 2025-10-02 04:42:35
2025-10-02 04:42:35 - INFO - Product still out of stock: Amul High Protein Rose Lassi
```

---

## 🛠️ Local Development

### Setup

```bash
# Clone repository
git clone https://github.com/prathmeshj1729/Amul_RoseLassi_Tracker.git
cd Amul_RoseLassi_Tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
TELEGRAM_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
CHECK_INTERVAL=300
CF_CLEARANCE=your_cloudflare_cookie
JSESSIONID=your_session_cookie
CFUVID=your_cfuvid_cookie
CF_BM=your_cf_bm_cookie
EXT_NAME=ojplmecpdpgccookcobabopnaifgidhf
EOF

# Run tracker
python tracker.py
```

### Testing

Monitor the logs to ensure:

- ✅ Cookies initialized successfully
- ✅ Telegram notification sent on startup
- ✅ API requests returning 200 status
- ✅ Product data being fetched correctly

---

## 📁 Project Structure

```
Amul_RoseLassi_Tracker/
├── tracker.py           # Main tracker script
├── requirements.txt     # Python dependencies
├── render.yaml         # Render deployment config
├── .env               # Local environment variables (git ignored)
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

---

**Made with ❤️ for Amul Rose Lassi lovers**
