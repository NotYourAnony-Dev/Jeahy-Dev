# bot.py — Jaehy Bot | NotYourAnony-Dev | GroupAnony-Dev
import sys
import asyncio
from telegram import Update
from telegram.ext import Application, ContextTypes
from config import Config
from database import init_db
from loader import load_plugins
from utils.logger import LOGGER

async def error_handler_global(update: object, context: ContextTypes.DEFAULT_TYPE):
    LOGGER.error(f"Global error: {context.error}")

def main():
    if Config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not Config.BOT_TOKEN:
        LOGGER.error("BOT_TOKEN not set! Edit config.py or set env var BOT_TOKEN.")
        sys.exit(1)

    LOGGER.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    LOGGER.info("  Jaehy Bot  |  NotYourAnony-Dev")
    LOGGER.info("  Project    |  GroupAnony-Dev")
    LOGGER.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Init SQLite
    LOGGER.info("Initialising database (SQLite)...")
    init_db()
    LOGGER.info("Database ready.")

    # Build application (polling, Termux-friendly)
    app = (
        Application.builder()
        .token(Config.BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # Load all plugins
    LOGGER.info("Loading plugins...")
    load_plugins(app)

    # Global error handler
    app.add_error_handler(error_handler_global)

    LOGGER.info("Bot is running! Press Ctrl+C to stop.")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
