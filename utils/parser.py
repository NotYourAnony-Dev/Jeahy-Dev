from config import Config

def parse_command(text: str) -> tuple[str, list[str]]:
    """Parse a prefixed command into (cmd, args)."""
    if not text:
        return "", []
    for prefix in Config.PREFIXES:
        if text.startswith(prefix):
            parts = text[len(prefix):].strip().split()
            if not parts:
                return "", []
            cmd = parts[0].lower().split("@")[0]
            args = parts[1:]
            return cmd, args
    return "", []

def has_prefix(text: str) -> bool:
    if not text:
        return False
    return any(text.startswith(p) for p in Config.PREFIXES)

def mention_html(user_id: int, name: str) -> str:
    safe = name.replace("<", "&lt;").replace(">", "&gt;")
    return f'<a href="tg://user?id={user_id}">{safe}</a>'
