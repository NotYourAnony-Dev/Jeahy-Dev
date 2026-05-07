from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from utils.permissions import is_admin, in_group
from utils.logger import log

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            if not in_group(update):
                await update.message.reply_text("❌ This command works in groups only.")
                return
            if not await is_admin(update):
                await update.message.reply_text("🔐 <b>Admins only!</b>", parse_mode="HTML")
                return
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            log.error(f"[admin_only] {e}")
    return wrapper

def group_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            if not in_group(update):
                await update.message.reply_text("❌ This command works in groups only.")
                return
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            log.error(f"[group_only] {e}")
    return wrapper

def safe(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            log.error(f"[{func.__name__}] Error: {e}")
    return wrapper
