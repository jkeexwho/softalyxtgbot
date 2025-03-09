from dotenv import load_dotenv
import os

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# Admin's Telegram ID (you will receive notifications here)
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
# Webhook settings (for production)
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
# Flask settings
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key') 