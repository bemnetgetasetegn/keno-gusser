import os
import threading
import time
import requests
import logging
from urllib.parse import urlparse
from dotenv import load_dotenv
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://your-web-app-url.com")  # Replace with your hosted web app URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KEEP_ALIVE_INTERVAL = 300  # 5 minutes
HEALTH_CHECK_URL = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("RAILWAY_STATIC_URL") or "http://localhost:10000"

def is_valid_betting_url(url):
    if not url.startswith('http'):
        url = 'https://' + url
    parsed = urlparse(url)
    if not parsed.netloc.endswith('.bet'):
        return False
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Please insert the URL of a betting site:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text.strip()
    await update.message.reply_text("Analyzing...")
    if is_valid_betting_url(url):
        keyboard = [[InlineKeyboardButton("Open Keno Gusser", web_app=WebAppInfo(url=WEB_APP_URL))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Valid betting site URL. Click the button to open the Keno Gusser web app.", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Invalid URL. Please ensure it's a valid .bet domain and try again.")

# --- Keep Alive Functions ---

def start_keep_alive():
    """Start background thread to keep the bot alive by pinging health endpoint"""
    def keep_alive_worker():
        while True:
            try:
                # Ping the health endpoint to keep the service awake
                response = requests.get(f"{HEALTH_CHECK_URL}/health", timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ Keep-alive ping successful: {response.status_code}")
                else:
                    logger.warning(f"⚠️ Keep-alive ping returned: {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Keep-alive ping failed: {e}")
            
            # Wait for the specified interval
            time.sleep(KEEP_ALIVE_INTERVAL)
    
    # Start the keep-alive thread
    keep_alive_thread = threading.Thread(target=keep_alive_worker, daemon=True)
    keep_alive_thread.start()
    logger.info(f"🔄 Keep-alive service started (pinging every {KEEP_ALIVE_INTERVAL} seconds)")

def create_flask_app():
    """Create and configure Flask app for Render"""
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "🛍️ Telegram Product Bot is running!"
    
    @app.route('/health')
    def health():
        return "OK", 200
    
    @app.route('/ping')
    def ping():
        return "pong", 200
    
    @app.route('/keepalive')
    def keepalive():
        return "🔄 Bot is alive and refreshing every 5 minutes", 200
    
    return app

def run_flask_app():
    """Run Flask app in a separate thread"""
    app = create_flask_app()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def run_bot_with_flask():
    """Run both bot and Flask app"""
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    # Start keep-alive service
    start_keep_alive()
    
    # Run the bot in main thread
    main()

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    run_bot_with_flask()