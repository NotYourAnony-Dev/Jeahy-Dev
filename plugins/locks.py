# plugins/locks.py
import re
import asyncio
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.parser import parse_command
from utils.decorators import admin_only, error_handler, group_only
from utils.permissions import is_admin
from database import get_locks, set_lock
from config import Config

LOCK_CMDS = {"lock", "unlock", "locks"}
URL_RE = re.compile(r"(https?://|t\.me/|www\.)", re.IGNORECASE)

@error_handler
@group_only
@admin_only
async def lock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    _, args = parse_command(msg.text)
    if not args:
        return await msg.reply_text("<b>ᴜsᴀɢᴇ:</b> <code>.lock links/spam/all</code>", parse_mode="HTML")
    ltype = args[0].lower()
    cid = update.effective_chat.id
    if ltype == "links":
        set_lock(cid, "lock_links", 1)
        await msg.reply_text("<b>ʟɪɴᴋs ʟᴏᴄᴋᴇᴅ!</b>", parse_mode="HTML")
    elif ltype == "spam":
        set_lock(cid, "lock_spam", 1)
        await msg.reply_text("<b>sᴘᴀᴍ ʟᴏᴄᴋᴇᴅ!</b>", parse_mode="HTML")
    elif ltype == "all":
        set_lock(cid, "lock_links", 1)
        set_lock(cid, "lock_spam", 1)
        set_lock(cid, "lock_all", 1)
        await msg.reply_text("<b>ᴀʟʟ ʟᴏᴄᴋᴇᴅ!</b>", parse_mode="HTML")
    else:
        await msg.reply_text("<b>ᴜɴᴋɴᴏᴡɴ ᴛʏᴘᴇ.</b>", parse_mode="HTML")

@error_handler
@group_only
@admin_only
async def unlock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    _, args = parse_command(msg.text)
    if not args:
        return await msg.reply_text("<b>ᴜsᴀɢᴇ:</b> <code>.unlock links/spam/all</code>", parse_mode="HTML")
    ltype = args[0].lower()
    cid = update.effective_chat.id
    if ltype == "links":
        set_lock(cid, "lock_links", 0)
        await msg.reply_text("<b>ʟɪɴᴋs ᴜɴʟᴏᴄᴋᴇᴅ!</b>", parse_mode="HTML")
    elif ltype == "spam":
        set_lock(cid, "lock_spam", 0)
        await msg.reply_text("<b>sᴘᴀᴍ ᴜɴʟᴏᴄᴋᴇᴅ!</b>", parse_mode="HTML")
    elif ltype == "all":
        set_lock(cid, "lock_links", 0)
        set_lock(cid, "lock_spam", 0)
        set_lock(cid, "lock_all", 0)
        await msg.reply_text("<b>ᴀʟʟ ᴜɴʟᴏᴄᴋᴇᴅ!</b>", parse_mode="HTML")
    else:
        await msg.reply_text("<b>ᴜɴᴋɴᴏᴡɴ ᴛʏᴘᴇ.</b>", parse_mode="HTML")

@error_handler
@group_only
async def locks_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lk = get_locks(update.effective_chat.id)
    def st(v):
        return "🔒 <b>ᴏɴ</b>" if v else "🔓 <b>ᴏғғ</b>"
    await update.effective_message.reply_text(
        "<b>ʟᴏᴄᴋ sᴛᴀᴛᴜs</b>\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        f"  ʟɪɴᴋs  » {st(lk['lock_links'])}\n"
        f"  sᴘᴀᴍ   » {st(lk['lock_spam'])}\n"
        f"  ᴀʟʟ    » {st(lk['lock_all'])}\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝",
        parse_mode="HTML")

@error_handler
async def lock_enforcer(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    lk = get_locks(chat.id)
    if lk.get("lock_all"):
        try:
            await msg.delete()
        except Exception:
            pass
        return
    if lk.get("lock_links") and URL_RE.search(msg.text):
        try:
            await msg.delete()
            n = await chat.send_message("<b>🔒 ʟɪɴᴋs ᴀʀᴇ ʟᴏᴄᴋᴇᴅ!</b>", parse_mode="HTML")
            await asyncio.sleep(5)
            await n.delete()
        except Exception:
            pass
        return
    if lk.get("lock_spam") and len(msg.text) > Config.SPAM_LENGTH:
        try:
            await msg.delete()
            n = await chat.send_message("<b>🔒 sᴘᴀᴍ ɪs ʟᴏᴄᴋᴇᴅ!</b>", parse_mode="HTML")
            await asyncio.sleep(5)
            await n.delete()
        except Exception:
            pass

@error_handler
async def locks_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return
    cmd, _ = parse_command(msg.text)
    if cmd not in LOCK_CMDS:
        return
    dispatch = {"lock": lock_cmd, "unlock": unlock_cmd, "locks": locks_status}
    fn = dispatch.get(cmd)
    if fn:
        await fn(update, context)

def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, locks_router), group=2)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lock_enforcer), group=8)
