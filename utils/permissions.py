from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from config import Config

async def is_admin(update: Update, user_id: int = None) -> bool:
    try:
        uid = user_id or update.effective_user.id
        if uid == Config.OWNER_ID:
            return True
        member = await update.effective_chat.get_member(uid)
        return member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER)
    except Exception:
        return False

async def is_owner(update: Update) -> bool:
    return update.effective_user.id == Config.OWNER_ID

async def bot_is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        me = await context.bot.get_me()
        member = await update.effective_chat.get_member(me.id)
        return member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER)
    except Exception:
        return False

def in_group(update: Update) -> bool:
    return update.effective_chat.type in ("group", "supergroup")
