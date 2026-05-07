# plugins/antiflood.py
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.parser import parse_command
from utils.decorators import admin_only, error_handler, group_only
from utils.permissions import is_admin
from utils.logger import LOGGER
from database import check_flood, reset_flood
from config import Config

@error_handler
@group_only
@admin_only
async def antiflood_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    _, args = parse_command(msg.text)
    action = args[0].lower() if args else ""
    if action == "on":
        context.chat_data["flood_enabled"] = True
        await msg.reply_text("<b>ᴀɴᴛɪ-ғʟᴏᴏᴅ ᴇɴᴀʙʟᴇᴅ!</b>", parse_mode="HTML")
    elif action == "off":
        context.chat_data["flood_enabled"] = False
        await msg.reply_text("<b>ᴀɴᴛɪ-ғʟᴏᴏᴅ ᴅɪsᴀʙʟᴇᴅ!</b>", parse_mode="HTML")
    else:
        status = "ᴏɴ" if context.chat_data.get("flood_enabled", True) else "ᴏғғ"
        await msg.reply_text(
            f"<b>ᴀɴᴛɪ-ғʟᴏᴏᴅ:</b> <code>{status}</code>\n"
            f"ᴜsᴀɢᴇ: <code>.antiflood on/off</code>",
            parse_mode="HTML")

@error_handler
async def flood_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return
    chat = update.effective_chat
    if chat.type == "private":
        return
    user = update.effective_user
    if not user:
        return
    if not context.chat_data.get("flood_enabled", True):
        return
    if await is_admin(update):
        return
    flooded = check_flood(chat.id, user.id, Config.FLOOD_LIMIT, Config.FLOOD_TIME)
    if flooded:
        try:
            perms = ChatPermissions(can_send_messages=False)
            await chat.restrict_member(user.id, perms)
            reset_flood(chat.id, user.id)
            await msg.reply_text(
                f"<a href='tg://user?id={user.id}'>{user.first_name}</a> "
                "<b>ᴍᴜᴛᴇᴅ ғᴏʀ ғʟᴏᴏᴅɪɴɢ!</b>",
                parse_mode="HTML")
            LOGGER.info(f"FLOOD MUTE | {user.id} in {chat.id}")
        except Exception as e:
            LOGGER.error(f"Flood mute error: {e}")

@error_handler
async def flood_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return
    cmd, _ = parse_command(msg.text)
    if cmd == "antiflood":
        await antiflood_cmd(update, context)

def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, flood_router), group=3)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, flood_checker), group=7)
