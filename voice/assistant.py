from __future__ import annotations
import asyncio
import logging
import subprocess
import time
import uuid
from contextlib import suppress
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel
from core.config import Settings
from music.player import MusicPlayer
from services.tts_service import TTSService

log = logging.getLogger("ruhi.voice")

class VoiceAssistant:
    def __init__(self, settings: Settings, music: MusicPlayer, tts: TTSService):
        self.settings = settings
        self.music = music
        self.tts = tts

        self.whisper = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )

        self.buffers = {}
        self.processing = set()
        self.locks = {}
        self.vad_threshold = 900

    def has_wake_word(self, text: str) -> bool:
        text = (text or "").lower()
        return any(x in text for x in ["ruhi","roohi","rui","rohe","lohi","rooji"])

    def strip_wake_word(self, text: str) -> str:
        text = (text or "").lower()
        for x in ["ruhi","roohi","rui","rohe","lohi","rooji"]:
            text = text.replace(x, "")
        return " ".join(text.split())


    async def transcribe_file(self, path: Path) -> str:

        segments, _ = await asyncio.to_thread(
            self.whisper.transcribe,
            str(path),
            language="en",
            task="transcribe",
            beam_size=1,
            best_of=1,
            vad_filter=True
        )

        text = " ".join(seg.text for seg in segments).strip()

        fixes = {
            "rohe": "ruhi",
            "roohi": "ruhi",
            "rui": "ruhi",
            "lohi": "ruhi",
            "rooji": "ruhi",
            "manmeera": "man mera",
            "manmira": "man mera",
            "egg jokes": "joke",
            "joksa": "joke",
            "rohi": "ruhi",
            "jog sena": "joke suna",
            "one joke sanaa": "joke suna",
            "egg joke sana": "joke suna",
            "play music": "play trending hindi songs",
        }

        low = text.lower()

        for k, v in fixes.items():
            low = low.replace(k, v)

        print(f"VOICE TEXT => {low}", flush=True)

        return low

    async def transcribe_pcm(self, pcm: bytes, chat_id: int) -> str:

        raw = self.settings.temp_dir / f"raw_{chat_id}_{uuid.uuid4().hex}.raw"
        wav = self.settings.temp_dir / f"vc_{chat_id}_{uuid.uuid4().hex}.wav"

        raw.write_bytes(pcm)

        try:
            await asyncio.to_thread(
                subprocess.run,
                [
                    "ffmpeg",
                    "-f","s16le",
                    "-ar","48000",
                    "-ac","1",
                    "-i",str(raw),

                    "-af",
                    "highpass=f=200,lowpass=f=3000,volume=2",

                    "-ar","16000",
                    "-ac","1",

                    str(wav),
                    "-y",
                    "-loglevel","quiet"
                ],
                check=True
            )

            return await self.transcribe_file(wav)

        finally:
            with suppress(Exception):
                raw.unlink(missing_ok=True)

            with suppress(Exception):
                wav.unlink(missing_ok=True)

    async def speak(self, chat_id: int, text: str):

        lock = self.locks.setdefault(chat_id, asyncio.Lock())

        async with lock:

            path = await self.tts.synthesize(chat_id, text)

            try:
                await self.music.calls.play(chat_id, str(path))
                await asyncio.sleep(max(2, min(10, len(text.split()) // 2)))

            finally:
                with suppress(Exception):
                    path.unlink(missing_ok=True)

    def ingest_raw_frame(self, chat_id: int, frame: bytes):

        audio = np.frombuffer(frame, dtype=np.int16)

        if not len(audio):
            return None

        energy = float(
            np.sqrt(np.mean(audio.astype(np.float32) ** 2))
        )

        buf = self.buffers.setdefault(chat_id, [])

        if energy > self.vad_threshold:
            buf.append(frame)

            if len(buf) > 260:
                del buf[:80]

            return None

        if len(buf) > 25:
            data = b"".join(buf)
            buf.clear()
            return data

        return None
