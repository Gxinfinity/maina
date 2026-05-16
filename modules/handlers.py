modules/handlers.py

from future import annotations

import random
import time
import requests

from contextlib import suppress
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType

try:
from pyrogram.enums import ButtonStyle
BUTTONS_AVAILABLE = True
except Exception:
BUTTONS_AVAILABLE = False

from pyrogram.types import (
CallbackQuery,
InlineKeyboardMarkup,
InlineKeyboardButton,
Message
)

from ai.intent import IntentRouter
from services.tts_service import LANGUAGE_VOICES

=========================================================

APIs

=========================================================

truth_api_url = "https://api.truthordarebot.xyz/v1/truth"
dare_api_url = "https://api.truthordarebot.xyz/v1/dare"

=========================================================

FALLBACK QUESTIONS

=========================================================

TRUTHS = [
"Sach sach batao, crush hai kya? 🥺",
"Last time jhoot kab bola?",
"Biggest fear kya hai?"
]

DARES = [
"Ek cute voice note bhejo 😭",
"10 pushups karo 😂",
"Group me kisi ko compliment do 💖"
]

=========================================================

BUTTON HELPER

=========================================================

def btn(text, data=None, url=None, style=None):
if BUTTONS_AVAILABLE:
if url:
return InlineKeyboardButton(
text=text,
url=url,
style=style
)

    return InlineKeyboardButton(
        text=text,
        callback_data=data,
        style=style
    )

if url:
    return InlineKeyboardButton(
        text=text,
        url=url
    )

return InlineKeyboardButton(
    text=text,
    callback_data=data
)

=========================================================

HANDLERS

=========================================================

class TelegramHandlers:

def __init__(
    self,
    bot: Client,
    router: IntentRouter
):
    self.bot = bot
    self.router = router

# =====================================================
# REGISTER
# =====================================================

def register(self):

    @self.bot.on_message(
        filters.command(
            [
                "start",
                "help",
                "intro",
                "play",
                "pause",
                "resume",
                "skip",
                "stop",
                "queue",
                "join",
                "leave",
                "truth",
                "dare",
                "xoxo",
                "weather",
                "search",
                "ask",
                "lang"
            ],
            prefixes=["/", ".", "!"]
        )
    )
    async def commands(_, message: Message):
        await self._command(message)

    @self.bot.on_callback_query(
        filters.regex("^(intro_|music_)")
    )
    async def callbacks(_, callback: CallbackQuery):
        await self._callbacks(callback)

# =====================================================
# ADMIN CHECK
# =====================================================

async def _admin_ok(
    self,
    message: Message,
    command: str
):

    if message.chat.type == ChatType.PRIVATE:
        return True

    if command not in {
        "play",
        "pause",
        "resume",
        "skip",
        "stop",
        "join",
        "leave"
    }:
        return True

    member = await self.bot.get_chat_member(
        message.chat.id,
        message.from_user.id
    )

    return member.status in {
        ChatMemberStatus.OWNER,
        ChatMemberStatus.ADMINISTRATOR
    }

# =====================================================
# COMMANDS
# =====================================================

async def _command(
    self,
    message: Message
):

    cmd = message.command[0].lower()

    args = " ".join(
        message.command[1:]
    ).strip()

    if not await self._admin_ok(message, cmd):
        return await message.reply(
            "❌ Sirf admins VC control kar sakte hain."
        )

    # =================================================
    # START
    # =================================================

    if cmd == "start":

        START_TEXT = """

✨ 𝗥𝘂𝗵𝗶 𝗦𝘂𝗽𝗿𝗲𝗺𝗲 𝗔𝗜 💫

╭━━━━━━━━━━━━━━━╮
┃ 🧠 AI Assistant
┃ 📚 Quiz System
┃ 🎮 Games
┃ 🎵 VC Music
┃ 🌦 Weather
┃ 🎤 Voice AI
╰━━━━━━━━━━━━━━━╯

⚡ Fast • Smart • Powerful
🔥 Ultimate Telegram AI Experience
"""

        return await message.reply_photo(
            photo="https://graph.org/file/2f8e61c55d311070339c8-17b572b5c7c8ad0907.jpg",
            caption=START_TEXT,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        btn(
                            "🧠 AI",
                            "intro_ai",
                            style=getattr(ButtonStyle, "PRIMARY", None)
                        ),
                        btn(
                            "📚 Quiz",
                            "intro_quiz",
                            style=getattr(ButtonStyle, "SUCCESS", None)
                        )
                    ],
                    [
                        btn(
                            "🎵 Music",
                            "intro_music",
                            style=getattr(ButtonStyle, "DANGER", None)
                        ),
                        btn(
                            "🎮 Games",
                            "intro_games",
                            style=getattr(ButtonStyle, "SECONDARY", None)
                        )
                    ],
                    [
                        btn(
                            "⚡ Features",
                            "intro_features",
                            style=getattr(ButtonStyle, "PRIMARY", None)
                        )
                    ]
                ]
            )
        )

    # =================================================
    # HELP
    # =================================================

    if cmd == "help":

        return await message.reply(
            "📚 Use /intro for full commands."
        )

    # =================================================
    # INTRO
    # =================================================

    if cmd == "intro":

        return await message.reply(
            """

🔥 RUHI SUPREME AI

🧠 AI Assistant
📚 Quiz System
🎵 Music System
🎮 Multiplayer Games
🌦 Weather
🎤 Voice AI
""",
reply_markup=InlineKeyboardMarkup(
[
[
btn("🧠 AI", "intro_ai"),
btn("📚 Quiz", "intro_quiz")
],
[
btn("🎵 Music", "intro_music"),
btn("🎮 Games", "intro_games")
],
[
btn("⚡ Features", "intro_features")
]
]
)
)

    # =================================================
    # MUSIC
    # =================================================

    if cmd == "play":

        if not args:
            return await message.reply(
                "🎵 Song name do."
            )

        return await message.reply(
            f"🎶 Playing: {args}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        btn("⏸ Pause", "music_pause"),
                        btn("▶ Resume", "music_resume")
                    ],
                    [
                        btn("⏭ Skip", "music_skip"),
                        btn("⏹ Stop", "music_stop")
                    ]
                ]
            )
        )

    if cmd == "pause":
        return await message.reply("⏸ Music Paused")

    if cmd == "resume":
        return await message.reply("▶ Music Resumed")

    if cmd == "skip":
        return await message.reply("⏭ Song Skipped")

    if cmd == "stop":
        return await message.reply("⏹ Music Stopped")

    if cmd == "queue":
        return await message.reply("📜 Queue Empty")

    if cmd == "join":
        return await message.reply("🎙 Joined VC")

    if cmd == "leave":
        return await message.reply("👋 Left VC")

    # =================================================
    # TRUTH
    # =================================================

    if cmd == "truth":

        try:
            r = requests.get(truth_api_url, timeout=10)

            if r.status_code == 200:
                data = r.json()

                question = (
                    data.get("question")
                    or random.choice(TRUTHS)
                )

            else:
                question = random.choice(TRUTHS)

        except Exception:
            question = random.choice(TRUTHS)

        return await message.reply(
            f"🤔 **Truth**\n\n{question}"
        )

    # =================================================
    # DARE
    # =================================================

    if cmd == "dare":

        try:
            r = requests.get(dare_api_url, timeout=10)

            if r.status_code == 200:
                data = r.json()

                question = (
                    data.get("question")
                    or random.choice(DARES)
                )

            else:
                question = random.choice(DARES)

        except Exception:
            question = random.choice(DARES)

        return await message.reply(
            f"🔥 **Dare**\n\n{question}"
        )

    # =================================================
    # XOXO
    # =================================================

    if cmd == "xoxo":

        return await message.reply(
            "🎮 TicTacToe Coming Soon 🙂"
        )

    # =================================================
    # AI
    # =================================================

    if cmd == "weather":

        return await message.reply(
            await self.router.weather.weather(args)
        )

    if cmd == "search":

        return await message.reply(
            await self.router.search.search(args)
        )

    if cmd == "ask":

        return await message.reply(
            await self.router.ai.reply(
                message.chat.id,
                args
            )
        )

    if cmd == "lang":

        ok = self.router.tts.set_language(
            message.chat.id,
            args
        )

        return await message.reply(
            "🌐 Voice Changed"
            if ok else
            f"Supported: {', '.join(LANGUAGE_VOICES)}"
        )

# =====================================================
# CALLBACKS
# =====================================================

async def _callbacks(
    self,
    callback: CallbackQuery
):

    data = callback.data

    # =================================================
    # INTRO AI
    # =================================================

    if data == "intro_ai":

        return await callback.message.edit_caption(
            caption="""

🧠 RUHI AI COMMANDS

/ask
/search
/weather
/lang

🔥 Smart AI Enabled
""",
reply_markup=InlineKeyboardMarkup(
[
[
btn("🔙 Back", "intro_back")
]
]
)
)

    # =================================================
    # QUIZ
    # =================================================

    elif data == "intro_quiz":

        return await callback.message.edit_caption(
            caption="""

📚 QUIZ COMMANDS

/quizhub
/test
/pollquiz
/voicequiz
/mocktest

🏆 Competitive Quiz Mode
""",
reply_markup=InlineKeyboardMarkup(
[
[
btn("🔙 Back", "intro_back")
]
]
)
)

    # =================================================
    # MUSIC
    # =================================================

    elif data == "intro_music":

        return await callback.message.edit_caption(
            caption="""

🎵 MUSIC COMMANDS

/play
/pause
/resume
/skip
/stop
/queue

🎶 High Quality VC Music
""",
reply_markup=InlineKeyboardMarkup(
[
[
btn("⏸ Pause", "music_pause"),
btn("▶ Resume", "music_resume")
],
[
btn("⏭ Skip", "music_skip"),
btn("⏹ Stop", "music_stop")
],
[
btn("🔙 Back", "intro_back")
]
]
)
)

    # =================================================
    # GAMES
    # =================================================

    elif data == "intro_games":

        return await callback.message.edit_caption(
            caption="""

🎮 FUN & GAMES

/truth
/dare
/xoxo

😂 Multiplayer Fun
""",
reply_markup=InlineKeyboardMarkup(
[
[
btn("🎲 Truth", "intro_truth"),
btn("🔥 Dare", "intro_dare")
],
[
btn("🔙 Back", "intro_back")
]
]
)
)

    # =================================================
    # FEATURES
    # =================================================

    elif data == "intro_features":

        return await callback.message.edit_caption(
            caption="""

⚡ RUHI FEATURES

✅ AI Chat
✅ Voice AI
✅ Music System
✅ Quiz System
✅ Multiplayer Games
✅ Admin Controls
""",
reply_markup=InlineKeyboardMarkup(
[
[
btn("🔙 Back", "intro_back")
]
]
)
)

    # =================================================
    # BACK
    # =================================================

    elif data == "intro_back":

        return await callback.message.edit_caption(
            caption="""

✨ 𝗥𝘂𝗵𝗶 𝗦𝘂𝗽𝗿𝗲𝗺𝗲 𝗔𝗜 💫

🧠 AI Assistant
📚 Quiz System
🎮 Games
🎵 Music
🌦 Weather
🎤 Voice AI

⚡ Fast • Smart • Powerful
🔥 Ultimate Telegram AI Experience
""",
reply_markup=InlineKeyboardMarkup(
[
[
btn("🧠 AI", "intro_ai"),
btn("📚 Quiz", "intro_quiz")
],
[
btn("🎵 Music", "intro_music"),
btn("🎮 Games", "intro_games")
],
[
btn("⚡ Features", "intro_features")
]
]
)
)

    # =================================================
    # MUSIC BUTTONS
    # =================================================

    elif data == "music_pause":

        await callback.answer(
            "⏸ Music Paused"
        )

    elif data == "music_resume":

        await callback.answer(
            "▶ Music Resumed"
        )

    elif data == "music_skip":

        await callback.answer(
            "⏭ Song Skipped"
        )

    elif data == "music_stop":

        await callback.answer(
            "⏹ Music Stopped"
        )

    else:

        await callback.answer(
            "🔥 Feature Active",
            show_alert=False
        )