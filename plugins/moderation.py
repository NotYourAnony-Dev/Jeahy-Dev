# plugins/moderation.py
"""
Unified moderation handler — runs as a high-priority group filter.
Covers: link deletion, spam deletion, toxic + flood cross-checks.
This plugin coordinates with locks.py, antiflood.py, and ai.py.
"""
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.decorators import error_handler
from utils.logger import LOGGER

@error_handler
async def mod_join_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome new members with a styled message."""
    msg = update.effective_message
    if not msg or not msg.new_chat_members:
        return
    chat = update.effective_chat
    for member in msg.new_chat_members:
        if member.is_bot:
            continue
        mention = f"<a href='tg://user?id={member.id}'>{member.first_name}</a>"
        try:
            await chat.send_message(
                f"<emoji id=\"6084423393623413254\">⭐</emoji> ᴡᴇʟᴄᴏᴍᴇ {mention}!\n\n"
                "╔═══❖•ೋ° °ೋ•❖═══╗\n"
                "  ᴘʟᴇᴀsᴇ ʀᴇᴀᴅ ᴛʜᴇ ʀᴜʟᴇs\n"
                "  ᴀɴᴅ ʙᴇ ʀᴇsᴘᴇᴄᴛғᴜʟ! 🙏\n"
                "╚═══❖•ೋ° °ೋ•❖═══╝",
                parse_mode="HTML"
            )
            LOGGER.info(f"JOIN | {member.id} joined {chat.id}")
        except Exception as e:
            LOGGER.error(f"Welcome error: {e}")

def register(app):
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, mod_join_welcome),
        group=12
    )
