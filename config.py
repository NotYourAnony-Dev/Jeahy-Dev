import os

class Config:
    # ── Bot Credentials ──────────────────────────────────
    BOT_TOKEN    = os.getenv("BOT_TOKEN", "8636562149:AAHaRFAvVcLQJEswSb_ZxL4-IxLWR2RYWBE")
    OWNER_ID     = int(os.getenv("OWNER_ID", "8695322751"))

    # ── Identity ─────────────────────────────────────────
    BOT_NAME     = "Jaehy Bot"
    BOT_VERSION  = "1.0.0"
    DEVELOPER    = "NotYourAnony-Dev"
    PROJECT      = "GroupAnony-Dev"
    SUPPORT_LINK = "https://t.me/GroupAnony_Dev"

    # ── Database ─────────────────────────────────────────
    DATABASE_PATH = "bot.db"

    # ── Behaviour ────────────────────────────────────────
    PREFIXES        = [".", "/", "!", "?"]
    MAX_WARNS       = 3
    FLOOD_LIMIT     = 5      # messages
    FLOOD_TIME      = 5      # seconds window
    RAID_LIMIT      = 10     # joins
    RAID_TIME       = 30     # seconds window
    SPAM_CHAR_LIMIT = 200

    # ── Lightweight Toxic Word List ───────────────────────
    TOXIC_WORDS = [
        "fuck", "shit", "bitch", "bastard", "asshole",
        "idiot", "kys", "kill yourself", "retard", "faggot",
        "whore", "slut", "nigger", "cunt", "dick",
    ]

    # ── Premium Emoji IDs ─────────────────────────────────
    EMOJI = {
        "fire":   "5453970573082255590",
        "star":   "6084423393623413254",
        "crown":  "5217890643321300022",
        "shield": "6147565374289220368",
        "sword":  "5373020661574826232",
        "bolt":   "6244326696795774172",
        "gem":    "5262584944881855065",
        "ban":    "6294218338281200326",
        "heart":  "608451817925666896",
        "robot":  "5226852504901277698",
    }

    @staticmethod
    def pe(name: str, fallback: str = "⚡") -> str:
        """Return HTML premium emoji tag."""
        eid = Config.EMOJI.get(name)
        if not eid:
            return fallback
        return f'<emoji id="{eid}">{fallback}</emoji>'
