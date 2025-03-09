# Telegram Bot для веб-сайта

A bot for Softalyx that handles requests through both Telegram and website integration.

## Features

- Interactive conversation flow in Telegram
- Website integration via REST API
- Collects user information step by step
- Supports multiple contact methods (Telegram/Email)
- Secure message forwarding to admin

## Installation

1. Install required system packages:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-dev build-essential git
```

2. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

3. Create a .env file in the project root and add:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_telegram_id_here
FLASK_SECRET_KEY=generate_random_key  # Run: python3 -c "import secrets; print(secrets.token_hex(32))"
WEBHOOK_URL=https://your-domain.com/webhook  # Optional, for production
```

## Running the Bot

1. Start the bot:
```bash
python3 bot.py
```

2. Start the web server:
```bash
python3 web_app.py
```

## Website Integration

To send requests from your website, use the following endpoint:

```
POST /api/send-request
Content-Type: application/json

{
    "name": "Client Name",
    "email": "client@example.com",
    "contact_preference": "Telegram",  // Must be either "Telegram" or "Email"
    "message": "Request details"
}
```

### Response Format

Success Response:
```json
{
    "success": true,
    "message": "Request sent successfully"
}
```

Error Response:
```json
{
    "success": false,
    "error": "Error description"
}
```

## Project Structure
```
├── requirements.txt
├── .env
├── README.md
├── bot.py
├── web_app.py
├── config.py
└── states.py
```

## Security Note

The FLASK_SECRET_KEY is used for session security. Generate it using:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
``` 