# plugins/admin.py
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.parser import parse_command
from utils.decorators import admin_only, error_handler, group_only
from utils.logger import LOGGER
from database import add_warn, get_warns, clear_warns
from config import Config

ADMIN_CMDS = {
    "ban","unban","kick","mute","unmute",
    "warn","warns","clearwarns","pin","unpin","promote","demote"
}

async def _target(update: Update):
    msg = update.effective_message
    if msg.reply_to_message:
        return msg.reply_to_message.from_user
    return None

def _mention(user):
    return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

def _err(e):
    return f"<b>ᴇʀʀᴏʀ:</b> <code>{e}</code>"

@error_handler
@group_only
@admin_only
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    t = await _target(update)
    if not t:
        return await msg.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴛᴏ ʙᴀɴ.</b>", parse_mode="HTML")
    if t.id == Config.OWNER_ID:
        return await msg.reply_text("<b>ᴄᴀɴ'ᴛ ʙᴀɴ ᴏᴡɴᴇʀ!</b>", parse_mode="HTML")
    try:
        await update.effective_chat.ban_member(t.id)
        await msg.reply_text(
            f"<emoji id=\"6244326696795774172\">🛡</emoji> <b>ʙᴀɴɴᴇᴅ</b> {_mention(t)}\n"
            f"<code>{t.id}</code>", parse_mode="HTML")
        LOGGER.info(f"BAN | {t.id} in {update.effective_chat.id}")
    except Exception as e:
        await msg.reply_text(_err(e), parse_mode="HTML")

@error_handler
@group_only
@admin_only
async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    t = await _target(update)
    if not t:
        return await msg.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.</b>", parse_mode="HTML")
    try:
        await update.effective_chat.unban_member(t.id)
        await msg.reply_text(f"<b>ᴜɴʙᴀɴɴᴇᴅ</b> {_mention(t)}", parse_mode="HTML")
    except Exception as e:
        await msg.reply_text(_err(e), parse_mode="HTML")

@error_handler
@group_only
@admin_only
async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    t = await _target(update)
    if not t:
        return await msg.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.</b>", parse_mode="HTML")
    try:
        await update.effective_chat.ban_member(t.id)
        await update.effective_chat.unban_member(t.id)
        await msg.reply_text(f"<b>ᴋɪᴄᴋᴇᴅ</b> {_mention(t)}", parse_mode="HTML")
        LOGGER.info(f"KICK | {t.id} in {update.effective_chat.id}")
    except Exception as e:
        await msg.reply_text(_err(e), parse_mode="HTML")

@error_handler
@group_only
@admin_only
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    t = await _target(update)
    if not t:
        return await msg.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.</b>", parse_mode="HTML")
    try:
        perms = ChatPermissions(can_send_messages=False, can_send_media_messages=False,
                                can_send_polls=False, can_send_other_messages=False)
        await update.effective_chat.restrict_member(t.id, perms)
        await msg.reply_text(f"<b>ᴍᴜᴛᴇᴅ</b> {_mention(t)}", parse_mode="HTML")
    except Exception as e:
        await msg.reply_text(_err(e), parse_mode="HTML")

@error_handler
@group_only
@admin_only
async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    t = await _target(update)
    if not t:
        return await msg.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.</b>", parse_mode="HTML")
    try:
        perms = ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                can_send_polls=True, can_send_other_messages=True,
                                can_add_web_page_previews=True)
        await update.effective_chat.restrict_member(t.id, perms)
        await msg.reply_text(f"<b>ᴜɴᴍᴜᴛᴇᴅ</b> {_mention(t)}", parse_mode="HTML")
    except Exception as e:
        await msg.reply_text(_err(e), parse_mode="HTML")

@error_handler
@group_only
@admin_only
async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    t = await _target(update)
    if not t:
        return await msg.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.</b>", parse_mode="HTML")
    _, args = parse_command(msg.text)
    reason = " ".join(args) if args else "ɴᴏ ʀᴇᴀsᴏɴ"
    chat_id = update.effective_chat.id
    count = add_warn(chat_id, t.id, reason)
    LOGGER.info(f"WARN | {t.id} in {chat_id} ({count}/{Config.MAX_WARNS})")
    if count >= Config.MAX_WARNS:
        try:
            await update.effective_chat.ban_member(t.id)
            clear_warns(chat_id, t.id)
            await msg.reply_text(
                f"{_mention(t)} <b>ᴀᴜᴛᴏ-ʙᴀɴɴᴇᴅ</b> ᴀғᴛᴇʀ {Config.MAX_WARNS} ᴡᴀʀɴs!",
                parse_mode="HTML")
        except Exception as e:
            await msg.reply_text(_err(e), parse_mode="HTML")
    else:
        await msg.reply_text(
            f"<b>ᴡᴀʀɴᴇᴅ</b> {_mention(t)}\n"
            f"ʀᴇᴀsᴏɴ: <i>{reason}</i>\n"
            f"ᴡᴀʀɴs: <b>{count}/{Config.MAX_WARNS}</b>",
            parse_mode="HTML")

@error_handler
@group_only
@admin_only
async def show_warns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    t = await _target(update)
    if not t:
        return await msg.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.</b>", parse_mode="HTML")
    rows = get_warns(update.effective_chat.id, t.id)
    if not rows:
        return await msg.reply_text(f"{_mention(t)} ʜᴀs <b>ɴᴏ ᴡᴀʀɴs</b>.", parse_mode="HTML")
    lines = "\n".join([f"  {i+1}. <i>{r['reason']}</i>" for i, r in enumerate(rows)])
    await msg.reply_text(
        f"<b>ᴡᴀʀɴs ғᴏʀ</b> {_mention(t)}:\n{lines}", parse_mode="HTML")

@error_handler
@group_only
@admin_only
async def clear_user_warns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    t = await _target(update)
    if not t:
        return await msg.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.</b>", parse_mode="HTML")
    clear_warns(update.effective_chat.id, t.id)
    await msg.reply_text(f"<b>ᴄʟᴇᴀʀᴇᴅ ᴡᴀʀɴs</b> ғᴏʀ {_mention(t)}.", parse_mode="HTML")

@error_handler
@group_only
@admin_only
async def pin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg.reply_to_message:
        return await msg.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ.</b>", parse_mode="HTML")
    try:
        await msg.reply_to_message.pin()
        await msg.reply_text("<b>ᴘɪɴɴᴇᴅ!</b>", parse_mode="HTML")
    except Exception as e:
        await msg.reply_text(_err(e), parse_mode="HTML")

@error_handler
@group_only
@admin_only
async def unpin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.effective_chat.unpin_message()
        await update.effective_message.reply_text("<b>ᴜɴᴘɪɴɴᴇᴅ!</b>", parse_mode="HTML")
    except Exception as e:
        await update.effective_message.reply_text(_err(e), parse_mode="HTML")

@error_handler
@group_only
@admin_only
async def promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    t = await _target(update)
    if not t:
        return await msg.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.</b>", parse_mode="HTML")
    try:
        await update.effective_chat.promote_member(
            t.id, can_delete_messages=True, can_restrict_members=True,
            can_invite_users=True, can_pin_messages=True, can_manage_chat=True)
        await msg.reply_text(f"<b>ᴘʀᴏᴍᴏᴛᴇᴅ</b> {_mention(t)}!", parse_mode="HTML")
    except Exception as e:
        await msg.reply_text(_err(e), parse_mode="HTML")

@error_handler
@group_only
@admin_only
async def demote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    t = await _target(update)
    if not t:
        return await msg.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.</b>", parse_mode="HTML")
    try:
        await update.effective_chat.promote_member(
            t.id, can_delete_messages=False, can_restrict_members=False,
            can_invite_users=False, can_pin_messages=False, can_manage_chat=False)
        await msg.reply_text(f"<b>ᴅᴇᴍᴏᴛᴇᴅ</b> {_mention(t)}.", parse_mode="HTML")
    except Exception as e:
        await msg.reply_text(_err(e), parse_mode="HTML")

_DISPATCH = {
    "ban": ban_user, "unban": unban_user, "kick": kick_user,
    "mute": mute_user, "unmute": unmute_user,
    "warn": warn_user, "warns": show_warns, "clearwarns": clear_user_warns,
    "pin": pin_message, "unpin": unpin_message,
    "promote": promote_user, "demote": demote_user,
}

@error_handler
async def admin_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return
    cmd, _ = parse_command(msg.text)
    if cmd not in ADMIN_CMDS:
        return
    fn = _DISPATCH.get(cmd)
    if fn:
        await fn(update, context)

def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_router), group=1)
