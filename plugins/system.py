# plugins/system.py
import psutil, time, os
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.parser import parse_command
from utils.decorators import error_handler

START_TIME = time.time()

def _uptime_str():
    elapsed = int(time.time() - START_TIME)
    h, rem = divmod(elapsed, 3600)
    m, s = divmod(rem, 60)
    return f"{h}ʜ {m}ᴍ {s}s"

def _disk_str():
    try:
        usage = psutil.disk_usage("/")
        used = usage.used // (1024**3)
        total = usage.total // (1024**3)
        return f"{used}GB / {total}GB"
    except Exception:
        return "ɴ/ᴀ"

def _cpu_str():
    try:
        return f"{psutil.cpu_percent(interval=0.1)}%"
    except Exception:
        return "ɴ/ᴀ"

def _ram_str():
    try:
        vm = psutil.virtual_memory()
        used = vm.used // (1024**2)
        total = vm.total // (1024**2)
        return f"{used}MB / {total}MB"
    except Exception:
        return "ɴ/ᴀ"

@error_handler
async def system_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return
    cmd, _ = parse_command(msg.text)
    if cmd not in ("system", "sysinfo"):
        return
    await msg.reply_text(
        "<emoji id=\"5226852504901277698\">💎</emoji> <b>sʏsᴛᴇᴍ ɪɴғᴏ</b>\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        f"  ⏱ ᴜᴘᴛɪᴍᴇ  : <code>{_uptime_str()}</code>\n"
        f"  💾 sᴛᴏʀᴀɢᴇ : <code>{_disk_str()}</code>\n"
        f"  ☠️ ᴄᴘᴜ     : <code>{_cpu_str()}</code>\n"
        f"  🐾 ʀᴀᴍ     : <code>{_ram_str()}</code>\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝",
        parse_mode="HTML"
    )

def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, system_router), group=11)
