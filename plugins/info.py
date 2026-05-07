# plugins/info.py
import time
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.parser import parse_command
from utils.decorators import error_handler
from database import get_stats, upsert_user

INFO_CMDS = {"id", "info", "ping", "uptime", "stats"}
START_TIME = time.time()

@error_handler
async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    target = msg.reply_to_message.from_user if msg.reply_to_message else update.effective_user
    await msg.reply_text(
        "<b>ɪᴅ ɪɴғᴏ</b>\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        f"  👤 ᴜsᴇʀ ɪᴅ: <code>{target.id}</code>\n"
        f"  💬 ᴄʜᴀᴛ ɪᴅ: <code>{chat.id}</code>\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝",
        parse_mode="HTML")

@error_handler
async def cmd_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    target = msg.reply_to_message.from_user if msg.reply_to_message else update.effective_user
    upsert_user(target.id, target.username, target.first_name)
    mention = f"<a href='tg://user?id={target.id}'>{target.first_name}</a>"
    uname = f"@{target.username}" if target.username else "ɴ/ᴀ"
    await msg.reply_text(
        "<b>ᴜsᴇʀ ɪɴғᴏ</b>\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        f"  👤 ɴᴀᴍᴇ: {mention}\n"
        f"  🆔 ɪᴅ  : <code>{target.id}</code>\n"
        f"  📎 ᴜsᴇʀ: {uname}\n"
        f"  🤖 ʙᴏᴛ : {'✅' if target.is_bot else '❌'}\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝",
        parse_mode="HTML")

@error_handler
async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import time as _t
    s = _t.monotonic()
    sent = await update.effective_message.reply_text("<b>ᴘɪɴɢɪɴɢ...</b>", parse_mode="HTML")
    ms = round((_t.monotonic() - s) * 1000, 2)
    await sent.edit_text(
        f"<b>ᴘᴏɴɢ!</b>\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        f"  🏓 ʟᴀᴛᴇɴᴄʏ: <code>{ms} ᴍs</code>\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝",
        parse_mode="HTML")

@error_handler
async def cmd_uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    e = int(time.time() - START_TIME)
    h, r = divmod(e, 3600); m, s = divmod(r, 60)
    await update.effective_message.reply_text(
        "<b>ᴜᴘᴛɪᴍᴇ</b>\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        f"  ⏱ {h}ʜ {m}ᴍ {s}s\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝",
        parse_mode="HTML")

@error_handler
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users, chats = get_stats()
    await update.effective_message.reply_text(
        "<b>ɢʟᴏʙᴀʟ sᴛᴀᴛs</b>\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        f"  👥 ᴜsᴇʀs: <code>{users}</code>\n"
        f"  💬 ᴄʜᴀᴛs: <code>{chats}</code>\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝",
        parse_mode="HTML")

_DISPATCH = {
    "id": cmd_id, "info": cmd_info, "ping": cmd_ping,
    "uptime": cmd_uptime, "stats": cmd_stats,
}

@error_handler
async def info_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return
    cmd, _ = parse_command(msg.text)
    if cmd not in INFO_CMDS:
        return
    fn = _DISPATCH.get(cmd)
    if fn:
        await fn(update, context)

def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, info_router), group=5)
