# plugins/ai.py
import re
import asyncio
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.decorators import error_handler
from utils.permissions import is_admin
from utils.logger import LOGGER
from database import add_warn, clear_warns
from config import Config

def _build_pattern():
    escaped = [re.escape(w) for w in Config.TOXIC_WORDS]
    return re.compile(r"\b(" + "|".join(escaped) + r")\b", re.IGNORECASE)

TOXIC_RE = _build_pattern()

@error_handler
async def ai_moderation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return
    chat = update.effective_chat
    if chat.type == "private":
        return
    user = update.effective_user
    if not user:
        return
    if await is_admin(update):
        return
    if not TOXIC_RE.search(msg.text):
        return
    try:
        await msg.delete()
    except Exception:
        pass
    count = add_warn(chat.id, user.id, "ᴀɪ: ᴛᴏxɪᴄ ʟᴀɴɢᴜᴀɢᴇ")
    LOGGER.info(f"AI MOD | Toxic by {user.id} in {chat.id} (warn {count}/{Config.MAX_WARNS})")
    notice = await chat.send_message(
        f"<a href='tg://user?id={user.id}'>{user.first_name}</a> "
        f"<b>ᴛᴏxɪᴄ ʟᴀɴɢᴜᴀɢᴇ ᴅᴇᴛᴇᴄᴛᴇᴅ!</b> ⚠️ ᴡᴀʀɴ: <b>{count}/{Config.MAX_WARNS}</b>",
        parse_mode="HTML")
    if count >= Config.MAX_WARNS:
        try:
            await chat.ban_member(user.id)
            clear_warns(chat.id, user.id)
            await chat.send_message(
                f"<a href='tg://user?id={user.id}'>{user.first_name}</a> "
                f"<b>ᴀᴜᴛᴏ-ʙᴀɴɴᴇᴅ</b> ᴀғᴛᴇʀ {Config.MAX_WARNS} ᴡᴀʀɴs.",
                parse_mode="HTML")
        except Exception as e:
            LOGGER.error(f"AI auto-ban error: {e}")
    else:
        await asyncio.sleep(6)
        try:
            await notice.delete()
        except Exception:
            pass

def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_moderation), group=6)
