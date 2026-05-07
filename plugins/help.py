# plugins/help.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from utils.parser import parse_command
from utils.decorators import error_handler

HELP_DATA = {
    "admin": (
        "<emoji id=\"5453970573082255590\">🔥</emoji> <b>ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs</b>\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        "  <b>.ban</b> — ʙᴀɴ ᴀ ᴜsᴇʀ\n"
        "  <b>.unban</b> — ᴜɴʙᴀɴ ᴀ ᴜsᴇʀ\n"
        "  <b>.kick</b> — ᴋɪᴄᴋ ᴀ ᴜsᴇʀ\n"
        "  <b>.mute</b> — ᴍᴜᴛᴇ ᴀ ᴜsᴇʀ\n"
        "  <b>.unmute</b> — ᴜɴᴍᴜᴛᴇ ᴀ ᴜsᴇʀ\n"
        "  <b>.warn</b> — ᴡᴀʀɴ ᴀ ᴜsᴇʀ\n"
        "  <b>.warns</b> — sʜᴏᴡ ᴡᴀʀɴs\n"
        "  <b>.clearwarns</b> — ᴄʟᴇᴀʀ ᴡᴀʀɴs\n"
        "  <b>.pin</b> — ᴘɪɴ ᴍᴇssᴀɢᴇ\n"
        "  <b>.unpin</b> — ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇ\n"
        "  <b>.promote</b> — ᴘʀᴏᴍᴏᴛᴇ ᴜsᴇʀ\n"
        "  <b>.demote</b> — ᴅᴇᴍᴏᴛᴇ ᴜsᴇʀ\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝"
    ),
    "locks": (
        "<emoji id=\"6147565374289220368\">🔒</emoji> <b>ʟᴏᴄᴋ ᴄᴏᴍᴍᴀɴᴅs</b>\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        "  <b>.lock links</b> — ʙʟᴏᴄᴋ ᴜʀʟs\n"
        "  <b>.lock spam</b> — ʙʟᴏᴄᴋ ʟᴏɴɢ ᴍsɢs\n"
        "  <b>.lock all</b> — ʟᴏᴄᴋ ᴇᴠᴇʀʏᴛʜɪɴɢ\n"
        "  <b>.unlock links/spam/all</b> — ᴜɴʟᴏᴄᴋ\n"
        "  <b>.locks</b> — sʜᴏᴡ ʟᴏᴄᴋ sᴛᴀᴛᴜs\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝"
    ),
    "info": (
        "<emoji id=\"6084423393623413254\">⭐</emoji> <b>ɪɴғᴏ ᴄᴏᴍᴍᴀɴᴅs</b>\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        "  <b>.id</b> — ɢᴇᴛ ᴜsᴇʀ / ᴄʜᴀᴛ ɪᴅ\n"
        "  <b>.info</b> — ᴜsᴇʀ ɪɴғᴏ\n"
        "  <b>.ping</b> — ᴄʜᴇᴄᴋ ʟᴀᴛᴇɴᴄʏ\n"
        "  <b>.uptime</b> — ʙᴏᴛ ᴜᴘᴛɪᴍᴇ\n"
        "  <b>.stats</b> — ɢʟᴏʙᴀʟ sᴛᴀᴛs\n"
        "  <b>.system</b> — sʏsᴛᴇᴍ ɪɴғᴏ\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝"
    ),
    "games": (
        "<emoji id=\"5373020661574826232\">⚔️</emoji> <b>ɢᴀᴍᴇ ᴄᴏᴍᴍᴀɴᴅs</b>\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        "  <b>.wordchain</b> — sᴛᴀʀᴛ ᴡᴏʀᴅ ᴄʜᴀɪɴ\n"
        "  <b>.word &lt;word&gt;</b> — ᴘʟᴀʏ ᴀ ᴡᴏʀᴅ\n"
        "  <b>.endgame</b> — ᴇɴᴅ ᴛʜᴇ ɢᴀᴍᴇ\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝"
    ),
    "system": (
        "<emoji id=\"5226852504901277698\">💎</emoji> <b>sʏsᴛᴇᴍ ᴄᴏᴍᴍᴀɴᴅs</b>\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        "  <b>.antiflood on/off</b> — ᴛᴏɢɢʟᴇ ғʟᴏᴏᴅ\n"
        "  <b>.antiraid on/off</b> — ᴛᴏɢɢʟᴇ ʀᴀɪᴅ\n"
        "  <b>.raidstatus</b> — ʀᴀɪᴅ sᴛᴀᴛᴜs\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝"
    ),
}

HELP_MAIN = (
    "<emoji id=\"5453970573082255590\">🔥</emoji> <b>ᴊᴀᴇʜʏ ʙᴏᴛ — ʜᴇʟᴘ ᴍᴇɴᴜ</b>\n\n"
    "╔═══❖•ೋ° °ೋ•❖═══╗\n"
    "  ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ\n"
    "╚═══❖•ೋ° °ೋ•❖═══╝\n\n"
    "<emoji id=\"6244326696795774172\">🛡️</emoji> <b>ᴅᴇᴠ:</b> <code>NotYourAnony-Dev</code>"
)

def _main_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚡ ᴀᴅᴍɪɴ", callback_data="help_admin"),
            InlineKeyboardButton("🔐 ʟᴏᴄᴋs", callback_data="help_locks"),
        ],
        [
            InlineKeyboardButton("ℹ️ ɪɴғᴏ", callback_data="help_info"),
            InlineKeyboardButton("🎮 ɢᴀᴍᴇs", callback_data="help_games"),
        ],
        [InlineKeyboardButton("🧪 sʏsᴛᴇᴍ", callback_data="help_system")],
    ])

def _back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data="help_main")]])

@error_handler
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return
    cmd, _ = parse_command(msg.text)
    if cmd != "help":
        return
    await msg.reply_text(HELP_MAIN, parse_mode="HTML", reply_markup=_main_kb())

@error_handler
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "help_main":
        await q.edit_message_text(HELP_MAIN, parse_mode="HTML", reply_markup=_main_kb())
    else:
        key = q.data.replace("help_", "")
        if key in HELP_DATA:
            await q.edit_message_text(HELP_DATA[key], parse_mode="HTML", reply_markup=_back_kb())

def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, help_handler), group=10)
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help_"))
