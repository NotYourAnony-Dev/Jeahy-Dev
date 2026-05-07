# plugins/games.py
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.parser import parse_command
from utils.decorators import error_handler, group_only
from database import get_game, set_game

GAME_CMDS = {"wordchain", "word", "endgame"}

@error_handler
@group_only
async def start_wordchain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game = get_game(chat_id)
    if game["active"]:
        await update.effective_message.reply_text(
            "<emoji id=\"5373020661574826232\">⚔️</emoji> <b>ɢᴀᴍᴇ ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ!</b>\n"
            f"ʟᴀsᴛ ᴡᴏʀᴅ: <code>{game['last_word']}</code>",
            parse_mode="HTML"
        )
        return
    set_game(chat_id, "", 1)
    await update.effective_message.reply_text(
        "<emoji id=\"5373020661574826232\">⚔️</emoji> <b>ᴡᴏʀᴅ ᴄʜᴀɪɴ sᴛᴀʀᴛᴇᴅ!</b>\n\n"
        "╔═══❖•ೋ° °ೋ•❖═══╗\n"
        "  ᴜsᴇ <code>.word &lt;ᴡᴏʀᴅ&gt;</code> ᴛᴏ ᴘʟᴀʏ\n"
        "  ᴇᴀᴄʜ ᴡᴏʀᴅ ᴍᴜsᴛ sᴛᴀʀᴛ ᴡɪᴛʜ ᴛʜᴇ\n"
        "  ʟᴀsᴛ ʟᴇᴛᴛᴇʀ ᴏғ ᴛʜᴇ ᴘʀᴇᴠɪᴏᴜs ᴡᴏʀᴅ!\n"
        "╚═══❖•ೋ° °ೋ•❖═══╝",
        parse_mode="HTML"
    )

@error_handler
@group_only
async def play_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    _, args = parse_command(msg.text)
    if not args:
        await msg.reply_text(
            "<emoji id=\"5373020661574826232\">⚔️</emoji> <b>ᴜsᴀɢᴇ:</b> <code>.word &lt;ʏᴏᴜʀ ᴡᴏʀᴅ&gt;</code>",
            parse_mode="HTML"
        )
        return

    chat_id = update.effective_chat.id
    game = get_game(chat_id)
    if not game["active"]:
        await msg.reply_text(
            "<emoji id=\"5262584944881855065\">👻</emoji> <b>ɴᴏ ɢᴀᴍᴇ ʀᴜɴɴɪɴɢ.</b> ᴜsᴇ <code>.wordchain</code>",
            parse_mode="HTML"
        )
        return

    word = args[0].lower().strip()
    if not word.isalpha():
        await msg.reply_text(
            "<emoji id=\"5262584944881855065\">👻</emoji> <b>ᴡᴏʀᴅs ᴏɴʟʏ — ɴᴏ ɴᴜᴍʙᴇʀs/sʏᴍʙᴏʟs!</b>",
            parse_mode="HTML"
        )
        return

    last = game["last_word"]
    user = update.effective_user

    if last and word[0] != last[-1]:
        await msg.reply_text(
            f"<emoji id=\"5262584944881855065\">👻</emoji> ❌ <b>ɪɴᴠᴀʟɪᴅ!</b>\n"
            f"ᴡᴏʀᴅ ᴍᴜsᴛ sᴛᴀʀᴛ ᴡɪᴛʜ <b>'{last[-1].upper()}'</b>",
            parse_mode="HTML"
        )
        return

    set_game(chat_id, word, 1)
    await msg.reply_text(
        f"<emoji id=\"5373020661574826232\">⚔️</emoji> ✅ <a href='tg://user?id={user.id}'>{user.first_name}</a> "
        f"ᴘʟᴀʏᴇᴅ: <b>{word}</b>\n"
        f"ɴᴇxᴛ ᴍᴜsᴛ sᴛᴀʀᴛ ᴡɪᴛʜ: <b>'{word[-1].upper()}'</b>",
        parse_mode="HTML"
    )

@error_handler
@group_only
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game = get_game(chat_id)
    if not game["active"]:
        await update.effective_message.reply_text(
            "<emoji id=\"5262584944881855065\">👻</emoji> <b>ɴᴏ ɢᴀᴍᴇ ʀᴜɴɴɪɴɢ!</b>",
            parse_mode="HTML"
        )
        return
    set_game(chat_id, "", 0)
    await update.effective_message.reply_text(
        "<emoji id=\"5217890643321300022\">👑</emoji> <b>ɢᴀᴍᴇ ᴇɴᴅᴇᴅ!</b>",
        parse_mode="HTML"
    )

@error_handler
async def games_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return
    cmd, _ = parse_command(msg.text)
    if cmd not in GAME_CMDS:
        return
    dispatch = {"wordchain": start_wordchain, "word": play_word, "endgame": end_game}
    handler = dispatch.get(cmd)
    if handler:
        await handler(update, context)

def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, games_router), group=9)
