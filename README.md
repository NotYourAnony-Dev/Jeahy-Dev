# Jaehy Bot
### By NotYourAnony-Dev | GroupAnony-Dev

---

## Termux Setup

```bash
# 1. Update packages
pkg update -y && pkg upgrade -y

# 2. Install dependencies
pkg install python git -y

# 3. Clone the project
git clone https://github.com/YOUR_USERNAME/JaehyBot
cd JaehyBot

# 4. Install Python packages
pip install -r requirements.txt

# 5. Configure your bot
nano config.py
# Set: BOT_TOKEN and OWNER_ID

# 6. Run
python bot.py
```

---

## Configuration (config.py)

| Key | Description |
|-----|-------------|
| `BOT_TOKEN` | Your bot token from @BotFather |
| `OWNER_ID` | Your Telegram user ID |

---

## Commands

### Admin
| Command | Description |
|---------|-------------|
| `.ban` | Ban a user (reply) |
| `.unban` | Unban a user (reply) |
| `.kick` | Kick a user (reply) |
| `.mute` | Mute a user (reply) |
| `.unmute` | Unmute a user (reply) |
| `.warn` | Warn a user (reply) |
| `.warns` | Show user warns (reply) |
| `.clearwarns` | Clear user warns (reply) |
| `.pin` | Pin a message (reply) |
| `.unpin` | Unpin last message |
| `.promote` | Promote a user (reply) |
| `.demote` | Demote a user (reply) |

### Locks
| Command | Description |
|---------|-------------|
| `.lock links` | Block URLs |
| `.lock spam` | Block long messages |
| `.lock all` | Lock everything |
| `.unlock links/spam/all` | Unlock |
| `.locks` | Show lock status |

### System
| Command | Description |
|---------|-------------|
| `.antiflood on/off` | Toggle flood protection |
| `.antiraid on/off` | Toggle raid mode |
| `.start` | Start message |
| `.help` | Help menu |
| `.ping` | Latency check |
| `.id` | Get user/chat ID |
| `.info` | User info |
| `.uptime` | Bot uptime |
| `.stats` | Global stats |
| `.system` | System info |

### Games
| Command | Description |
|---------|-------------|
| `.wordchain` | Start word chain game |
| `.word <word>` | Play a word |
| `.endgame` | End the game |

---

## Features

- SQLite database (no MongoDB, no Docker)
- Multi-prefix support: `.` `/` `!` `?`
- Anti-flood auto-mute
- Anti-raid auto-restrict
- Auto-ban after 3 warns
- AI toxic word detection
- Link & spam locking
- Word chain game
- Premium emoji UI
- Fully Termux compatible
- Low RAM / Low CPU

---

## Project Structure

```
JaehyBot/
├── bot.py          ← Entry point
├── config.py       ← Configuration
├── database.py     ← SQLite layer
├── loader.py       ← Plugin auto-loader
├── requirements.txt
├── plugins/
│   ├── start.py
│   ├── help.py
│   ├── admin.py
│   ├── locks.py
│   ├── antiflood.py
│   ├── antiraid.py
│   ├── moderation.py
│   ├── games.py
│   ├── info.py
│   ├── system.py
│   └── ai.py
└── utils/
    ├── parser.py
    ├── permissions.py
    ├── logger.py
    └── decorators.py
```

---

**Powered by NotYourAnony-Dev**
