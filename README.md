# Amul Rose Lassi Stock Tracker

Background service that monitors Amul Rose Lassi product availability and sends Telegram notifications when stock is detected.

## Features

- Automated Cloudflare challenge bypass using cloudscraper
- Self-healing session management with automatic cookie refresh
- Configurable check intervals with random jitter to avoid detection
- Telegram notifications for stock availability and system events
- Exponential backoff retry logic with error handling
- Containerized deployment ready

## Architecture

- **Language**: Python 3.11
- **Dependencies**: cloudscraper, python-telegram-bot, python-dotenv
- **Deployment**: Docker container (single service)
- **Resource Usage**: ~50-100MB RAM, <0.5% CPU

## Prerequisites

- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram Chat ID (from [@userinfobot](https://t.me/userinfobot))

## Local Development

### Setup

```bash
# Clone repository
git clone https://github.com/prathmeshj1729/Amul_RoseLassi_Tracker.git
cd Amul_RoseLassi_Tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cat > .env << EOF
TELEGRAM_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
CHECK_INTERVAL=300
EOF
```

### Run

```bash
python tracker.py
```

Expected output:

```
INFO - Successfully obtained fresh session with 6 cookies
INFO - Amul Rose Lassi Stock Tracker Started
INFO - Telegram notification sent successfully
INFO - Check #1 at 2025-10-02 12:00:00
INFO - Product still out of stock: Amul High Protein Rose Lassi
```

## Docker Deployment

### Build Image

```bash
# Build
docker build -t amul-tracker:latest .

# Verify
docker images | grep amul-tracker
```

Image size: ~150MB

### Run Container

```bash
# Create .env file first (see Local Development section)

# Run with auto-restart
docker run -d \
  --name amul-tracker \
  --restart unless-stopped \
  --env-file .env \
  amul-tracker:latest

# Check logs
docker logs -f amul-tracker

# Check status
docker ps | grep amul-tracker
```

### Export/Import (for remote deployment)

```bash
# Export
docker save amul-tracker:latest | gzip > amul-tracker.tar.gz

# Transfer to remote host
scp amul-tracker.tar.gz user@remote-host:~/

# On remote host - Import and run
gunzip -c amul-tracker.tar.gz | docker load
docker run -d --name amul-tracker --restart unless-stopped --env-file .env amul-tracker:latest
```

## Production Deployment

### Environment Variables

| Variable         | Required | Default | Description                        |
| ---------------- | -------- | ------- | ---------------------------------- |
| `TELEGRAM_TOKEN` | Yes      | -       | Telegram bot authentication token  |
| `CHAT_ID`        | Yes      | -       | Telegram chat ID for notifications |
| `CHECK_INTERVAL` | No       | 300     | Seconds between stock checks       |

### Container Management

```bash
# View logs
docker logs -f amul-tracker

# Check resource usage
docker stats amul-tracker --no-stream

# Restart
docker restart amul-tracker

# Stop
docker stop amul-tracker

# Remove
docker stop amul-tracker && docker rm amul-tracker
```

### Health Checks

Monitor logs for:

- `Successfully obtained fresh session` - Session management working
- `Telegram notification sent successfully` - Notifications working
- `Product still out of stock` or `PRODUCT IN STOCK!` - Monitoring active
- `401/403` errors followed by `Refreshing session` - Auto-healing working

## How It Works

1. **Initialization**: Loads environment variables, initializes cloudscraper session
2. **Session Setup**: Visits Amul shop to obtain fresh cookies and solve Cloudflare challenges
3. **Monitoring Loop**: Polls product API at configured intervals with random jitter
4. **Error Handling**: Automatically refreshes session on 401/403 errors
5. **Notifications**: Sends Telegram alerts on stock detection, startup, and errors
6. **Termination**: Stops monitoring once product is found in stock

## Project Structure

```
.
├── tracker.py          # Main application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container definition
├── .dockerignore      # Docker build exclusions
├── .gitignore         # Git exclusions
└── README.md          # This file
```

## Technical Details

### Cookie Management

- Automatic Cloudflare challenge solving via cloudscraper
- Session cookies obtained from shop.amul.com homepage
- Auto-refresh on authentication failures (401/403)
- No manual cookie updates required

### API Integration

- Target: Amul Shop Product API
- Method: GET with custom headers (TID, Base_Url, Frontend)
- Response: JSON with product availability data
- Rate limiting: Configurable interval + random jitter (±10%)

### Error Handling

- Retry logic: 3 attempts with exponential backoff
- Session refresh on auth errors (unlimited retries)
- Graceful shutdown on KeyboardInterrupt
- Crash notifications via Telegram

**Made with ❤️ for Amul Rose Lassi lovers**
