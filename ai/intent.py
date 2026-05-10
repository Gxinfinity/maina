from __future__ import annotations

import asyncio
import re

from music.player import MusicPlayer
from services.ai_service import AIService
from services.search_service import SearchService
from services.tts_service import TTSService
from services.weather_service import WeatherService
from voice.assistant import VoiceAssistant


class IntentRouter:
    def __init__(
        self,
        ai: AIService,
        weather: WeatherService,
        search: SearchService,
        tts: TTSService,
        music: MusicPlayer,
        voice: VoiceAssistant
    ):
        self.ai = ai
        self.weather = weather
        self.search = search
        self.tts = tts
        self.music = music
        self.voice = voice

    def parse_seconds(self, text: str) -> int:
        m = re.search(r"\d+", text or "")
        return int(m.group()) if m else 0

    async def handle(self, chat_id: int, text: str, speak: bool = True) -> str:
        clean = (text or "").strip()
        low = clean.lower()
        response = ""

        music_words = [
            "play", "song", "music", "gaana", "baja", "bajao",
            "sing", "sunao", "listen"
        ]

        if any(x in low for x in music_words):

            query = low

            for word in [
                "ruhi", "roohi", "rui", "lohi", "rooji",
                "play", "song", "music", "gaana", "baja",
                "bajao", "sing", "sunao", "listen",
                "please", "karo"
            ]:
                query = re.sub(rf"\b{word}\b", "", query, flags=re.I)

            query = re.sub(r"[^a-zA-Z0-9\s]", " ", query)
            query = " ".join(query.split()).strip()

            if not query:
                query = "trending hindi songs"

            print(f"MUSIC QUERY => {query}", flush=True)

            response = f"Haan Ji, {query} laga diya 🎵"

            # 👉 Pehle TTS बोले
            if speak:
                await self.voice.speak(chat_id, response)

            # 👉 TTS finish hone ke baad small delay
            await asyncio.sleep(2)

            # 👉 Ab music play
            tracks = await self.music.add(chat_id, query)

            if tracks:
                response = f"Haan Ji, {tracks[0].title} laga diya 🎵"
            else:
                response = "Music nahi mila 😭"

            return response

        elif any(x in low for x in ("pause", "ruk", "ruko")):
            await self.music.pause(chat_id)
            response = "Pause kar diya 🥺"

        elif any(x in low for x in ("resume", "continue", "chalu")):
            await self.music.resume(chat_id)
            response = "Chalu kar diya ▶️"

        elif any(x in low for x in ("skip", "next", "agla")):
            old = await self.music.skip(chat_id)
            response = (
                f"Skip kar diya: {old.title}"
                if old else
                "Queue khali hai 😭"
            )

        elif any(x in low for x in ("stop", "band", "clear")):
            await self.music.stop(chat_id)
            response = "Music band kar diya 😭"

        elif "weather" in low or "mausam" in low:
            response = await self.weather.weather(clean)

        elif low.startswith(("search ", "google ", "dhundo ")):
            response = await self.search.search(clean)

        elif any(x in low for x in ("hello", "hi", "kaisi", "kaha", "doing")):
            response = await self.ai.reply(chat_id, clean)

        else:
            response = await self.ai.reply(chat_id, clean)

        if speak:
            await self.voice.speak(chat_id, response)

        return response
