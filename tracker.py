import cloudscraper
import time
import telegram
import logging
import os
import random
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))

# Validate required environment variables
if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("TELEGRAM_TOKEN and CHAT_ID must be set as environment variables")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Telegram bot
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Initialize cloudscraper session (automatically handles Cloudflare)
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'darwin',
        'desktop': True
    }
)

# Add session cookies from environment (if available)
def initialize_cookies():
    """Load cookies from environment into scraper session"""
    cf_clearance = os.getenv("CF_CLEARANCE", "")
    jsessionid = os.getenv("JSESSIONID", "")
    cfuvid = os.getenv("CFUVID", "")
    cf_bm = os.getenv("CF_BM", "")
    ext_name = os.getenv("EXT_NAME", "ojplmecpdpgccookcobabopnaifgidhf")
    
    cookies = {}
    if ext_name:
        cookies['ext_name'] = ext_name
    if cf_clearance:
        cookies['cf_clearance'] = cf_clearance
    if jsessionid:
        cookies['jsessionid'] = jsessionid
    if cfuvid:
        cookies['_cfuvid'] = cfuvid
    if cf_bm:
        cookies['__cf_bm'] = cf_bm
    
    for name, value in cookies.items():
        scraper.cookies.set(name, value, domain='.shop.amul.com')
    
    logger.info(f"Initialized {len(cookies)} cookies in session")

initialize_cookies()

# Amul API endpoint for Rose Lassi
URL = "https://shop.amul.com/api/1/entity/ms.products?q=%7B%22alias%22:%22amul-high-protein-rose-lassi-200-ml-or-pack-of-30%22%7D&limit=1"

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF = 5  # seconds

# Flask app for Render web service (keeps service alive)
app = Flask(__name__)

@app.route('/')
def home():
    return {
        "status": "running",
        "service": "Amul Rose Lassi Stock Tracker",
        "message": "Tracker is running in the background. Check logs for status."
    }

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

def run_flask():
    """Run Flask server in background thread"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def get_headers():
    """Build custom headers for Amul API (Cloudflare handled by cloudscraper)"""
    # Generate transaction ID (timestamp:random:hash format)
    tid = f"{int(time.time() * 1000)}:{random.randint(1, 99)}:{os.urandom(32).hex()}"
    
    return {
        "Accept": "application/json, text/plain, */*",
        "Base_Url": "https://shop.amul.com/en/product/amul-high-protein-rose-lassi-200-ml-or-pack-of-30",
        "Frontend": "1",
        "Referer": "https://shop.amul.com/",
        "TID": tid
    }

def send_telegram_notification(message):
    """Send Telegram message with retry logic"""
    for attempt in range(MAX_RETRIES):
        try:
            asyncio.run(bot.send_message(chat_id=CHAT_ID, text=message))
            logger.info("Telegram notification sent successfully")
            return True
        except Exception as e:
            logger.error(f"Telegram notification failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
    return False

def refresh_session():
    """Refresh cloudscraper session and cookies when they expire"""
    global scraper
    logger.info("Refreshing session and cookies...")
    
    # Create new scraper instance
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'darwin',
            'desktop': True
        }
    )
    
    # Reinitialize cookies
    initialize_cookies()
    logger.info("Session refreshed successfully")

def check_stock():
    """Check product stock with retry logic and exponential backoff"""
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            headers = get_headers()
            resp = scraper.get(URL, headers=headers, timeout=10, allow_redirects=True)
            
            # Check for HTTP errors - refresh session if unauthorized
            if resp.status_code == 401:
                logger.warning("401 Unauthorized - Session expired, refreshing...")
                refresh_session()
                # Don't count this as a retry attempt
                time.sleep(2)
                continue  # Retry immediately with refreshed session
            
            if resp.status_code == 403:
                logger.warning("403 Forbidden - Refreshing session...")
                refresh_session()
                # Don't count this as a retry attempt
                time.sleep(2)
                continue  # Retry immediately with refreshed session
            
            # Check for other error codes
            if resp.status_code != 200:
                logger.error(f"HTTP {resp.status_code} error")
                attempt += 1
                continue
            
            # Parse response
            data = resp.json()
            
            if not data.get("data") or len(data["data"]) == 0:
                logger.warning("No product data found in API response")
                return False
            
            product = data["data"][0]
            available = product.get("available", 0)
            name = product.get("name", "Unknown Product")
            price = product.get("price", "N/A")
            
            if available > 0:
                message = f"✅ IN STOCK: {name}\nAvailable: {available}\nPrice: ₹{price}\n👉 https://shop.amul.com/"
                logger.info(f"🎉 PRODUCT IN STOCK! {name} - {available} units available")
                send_telegram_notification(message)
                return True
            else:
                logger.info(f"Product still out of stock: {name}")
                return False
                
        except KeyError as e:
            logger.error(f"Unexpected API response format (attempt {attempt + 1}/{MAX_RETRIES}): Missing key {e}")
            attempt += 1
        except Exception as e:
            # Check if it's a 401/403 error - refresh session
            if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                if e.response.status_code == 401:
                    logger.warning("401 Unauthorized (exception) - Session expired, refreshing...")
                    refresh_session()
                    time.sleep(2)
                    continue  # Don't increment attempt, just retry
                elif e.response.status_code == 403:
                    logger.warning("403 Forbidden (exception) - Refreshing session...")
                    refresh_session()
                    time.sleep(2)
                    continue  # Don't increment attempt, just retry
                else:
                    logger.error(f"HTTP error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            elif "timeout" in str(e).lower():
                logger.error(f"Request timeout (attempt {attempt + 1}/{MAX_RETRIES})")
            elif "connection" in str(e).lower():
                logger.error(f"Connection error (attempt {attempt + 1}/{MAX_RETRIES})")
            else:
                logger.error(f"Unexpected error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            attempt += 1
        
        # Exponential backoff before retry (if we're retrying)
        if attempt > 0 and attempt < MAX_RETRIES:
            backoff_time = INITIAL_BACKOFF * (2 ** (attempt - 1))
            logger.info(f"Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)
    
    logger.error("All retry attempts failed")
    return False

def main():
    """Main execution loop with startup notification"""
    logger.info("=" * 50)
    logger.info("Amul Rose Lassi Stock Tracker Started")
    logger.info(f"Check Interval: {CHECK_INTERVAL} seconds ({CHECK_INTERVAL // 60} minutes)")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)
    
    # Send startup notification
    startup_msg = f"🤖 Stock Tracker Started\nMonitoring: Amul Rose Lassi\nCheck interval: {CHECK_INTERVAL // 60} minutes"
    send_telegram_notification(startup_msg)
    
    check_count = 0
    
    while True:
        check_count += 1
        logger.info(f"Check #{check_count} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if check_stock():
            logger.info("Product found in stock! Stopping tracker.")
            break
        
        # Add random jitter (±10%) to avoid detection
        jitter = random.uniform(-0.1, 0.1) * CHECK_INTERVAL
        sleep_time = CHECK_INTERVAL + jitter
        
        logger.info(f"Sleeping for {sleep_time:.0f} seconds until next check...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    # Start Flask server in background thread (for Render web service)
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask server started on background thread")
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Tracker stopped by user")
        send_telegram_notification("🛑 Stock tracker stopped manually")
    except Exception as e:
        error_msg = f"💥 Tracker crashed: {str(e)}"
        logger.critical(error_msg)
        send_telegram_notification(error_msg)
