from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.config import settings
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    webapp_url = "https://your-domain.com/tg-app"  # Update this
    
    keyboard = [
        [InlineKeyboardButton("Open Assistant", web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton("Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome to Alfa Business Assistant! 🚀\n\n"
        "I'm here to help you manage your business.",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    user_message = update.message.text
    # Process with AI
    response = f"You said: {user_message}"
    await update.message.reply_text(response)

async def setup_telegram_bot():
    """Initialize Telegram bot"""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("No Telegram bot token provided")
        return
    
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    await application.initialize()
    await application.start()
    logger.info("Telegram bot started")