# plugins/antiraid.py
from telegram import Update, ChatPermissions, ChatMember
from telegram.ext import ContextTypes, MessageHandler, ChatMemberHandler, filters
from utils.parser import parse_command
from utils.decorators import admin_only, error_handler, group_only
from utils.logger import LOGGER
from database import check_raid, raid_active, set_raid
from config import Config

@error_handler
@group_only
@admin_only
async def antiraid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    _, args = parse_command(msg.text)
    action = args[0].lower() if args else ""
    cid = update.effective_chat.id
    if action == "on":
        set_raid(cid, True)
        await msg.reply_text(
            "<b>ʀᴀɪᴅ ᴍᴏᴅᴇ ᴇɴᴀʙʟᴇᴅ!</b>\nɴᴇᴡ ᴊᴏɪɴs ᴡɪʟʟ ʙᴇ ʀᴇsᴛʀɪᴄᴛᴇᴅ.",
            parse_mode="HTML")
    elif action == "off":
        set_raid(cid, False)
        await msg.reply_text("<b>ʀᴀɪᴅ ᴍᴏᴅᴇ ᴅɪsᴀʙʟᴇᴅ!</b>", parse_mode="HTML")
    else:
        active = raid_active(cid)
        status = "🔴 ᴀᴄᴛɪᴠᴇ" if active else "🟢 ɪɴᴀᴄᴛɪᴠᴇ"
        await msg.reply_text(
            f"<b>ʀᴀɪᴅ sᴛᴀᴛᴜs:</b> {status}\n"
            f"ᴜsᴀɢᴇ: <code>.antiraid on/off</code>",
            parse_mode="HTML")

@error_handler
async def raid_join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result:
        return
    chat = result.chat
    new_member = result.new_chat_member
    if not new_member:
        return
    if new_member.status not in (ChatMember.MEMBER, ChatMember.RESTRICTED):
        return
    cid = chat.id
    is_raid = check_raid(cid, Config.RAID_THRESHOLD, Config.RAID_WINDOW)
    if is_raid:
        LOGGER.info(f"RAID DETECTED | chat {cid}")
        try:
            perms = ChatPermissions(can_send_messages=False, can_send_media_messages=False,
                                    can_send_other_messages=False)
            await chat.restrict_member(new_member.user.id, perms)
            await context.bot.send_message(
                cid,
                "<b>ʀᴀɪᴅ ᴅᴇᴛᴇᴄᴛᴇᴅ!</b> ɴᴇᴡ ᴊᴏɪɴ ʀᴇsᴛʀɪᴄᴛᴇᴅ.",
                parse_mode="HTML")
        except Exception as e:
            LOGGER.error(f"Raid restrict error: {e}")
        return
    if raid_active(cid):
        try:
            perms = ChatPermissions(can_send_messages=False)
            await chat.restrict_member(new_member.user.id, perms)
            LOGGER.info(f"RAID MODE | Restricted {new_member.user.id} in {cid}")
        except Exception as e:
            LOGGER.error(f"Raid join restrict: {e}")

@error_handler
async def raid_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return
    cmd, _ = parse_command(msg.text)
    if cmd in ("antiraid", "raidstatus"):
        await antiraid_cmd(update, context)

def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, raid_router), group=4)
    app.add_handler(ChatMemberHandler(raid_join_handler, ChatMemberHandler.CHAT_MEMBER))
