# plugins/start.py
import psutil, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.parser import parse_command
from utils.decorators import error_handler
from database import upsert_user, upsert_chat
from config import Config

_START = time.time()

def _uptime():
    e = int(time.time() - _START)
    h, r = divmod(e, 3600); m, s = divmod(r, 60)
    return f"{h}ʜ {m}ᴍ {s}s"

def _disk():
    try:
        u = psutil.disk_usage("/"); return f"{u.used//1024**3}GB/{u.total//1024**3}GB"
    except Exception: return "ɴ/ᴀ"

def _cpu():
    try: return f"{psutil.cpu_percent(interval=0.1)}%"
    except Exception: return "ɴ/ᴀ"

def _ram():
    try:
        v = psutil.virtual_memory(); return f"{v.used//1024**2}MB/{v.total//1024**2}MB"
    except Exception: return "ɴ/ᴀ"

START_KB = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("⚡ ʜᴇʟᴘ", callback_data="help_main"),
        InlineKeyboardButton("💬 sᴜᴘᴘᴏʀᴛ", url=Config.SUPPORT_LINK),
    ],
    [
        InlineKeyboardButton("🔥 ᴅᴇᴠ", url=f"https://t.me/{Config.DEVELOPER}"),
    ]
])

@error_handler
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return
    cmd, _ = parse_command(msg.text)
    if cmd != "start":
        return

    user = update.effective_user
    chat = update.effective_chat
    upsert_user(user.id, user.username, user.first_name)
    if chat.type != "private":
        upsert_chat(chat.id, chat.title)

    mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    text = (
        "┌─── ˹ <b>ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b> ˼ ─── ⏤‌‌●\n"
        f"<emoji id=\"5262584944881855065\">😈</emoji> ┆ ʜєʏ, {mention}\n"
        f"<emoji id=\"5217890643321300022\">👑</emoji> ┆ ɪ ᴀᴍ ─ <b>𝐉ᴀᴇʜʏ ʙᴏᴛ</b>\n"
        "└──────────────────────•\n\n"
        "<emoji id=\"5262584944881855065\">💀</emoji> ᴛʜᴇ ᴍᴏsᴛ ᴘᴏᴡᴇʀғᴜʟ &amp; ғᴀsᴛᴇsᴛ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ!\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        f"<emoji id=\"608451817925666896\">⚡</emoji> ᴜᴘᴛɪᴍᴇ    » <code>{_uptime()}</code>\n"
        f"<emoji id=\"6294218338281200326\">💠</emoji> sᴛᴏʀᴀɢᴇ  » <code>{_disk()}</code>\n"
        f"<emoji id=\"5453970573082255590\">🔥</emoji> ᴄᴘᴜ ʟᴏᴀᴅ » <code>{_cpu()}</code>\n"
        f"<emoji id=\"6084423393623413254\">⭐</emoji> ʀᴀᴍ      » <code>{_ram()}</code>\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝\n\n"
        "•──────────────────────•\n"
        f"<emoji id=\"5262584944881855065\">💀</emoji> ✦ ᴘᴏᴡєʀєᴅ ʙʏ » ── <b>NotYourAnony-Dev</b>\n"
        "•──────────────────────•"
    )

    await msg.reply_text(text, parse_mode="HTML", reply_markup=START_KB)

def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start_handler), group=0)
