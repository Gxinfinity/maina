from __future__ import annotations
import asyncio
import os
from collections import defaultdict, deque
import google.generativeai as genai
from openai import OpenAI
from core.config import Settings
from database.repository import Repository

PERSONA = """
You are Ruhi/Roohi, a cute emotionally expressive Hinglish AI girl inside Telegram voice chats.
Only identify as Ruhi or Roohi.
Keep replies short, warm, natural, and emotional.
""".strip()

class AIService:
    def __init__(self, settings: Settings, repo: Repository):
        self.settings = settings
        self.repo = repo
        self.memory: dict[int, deque[str]] = defaultdict(lambda: deque(maxlen=8))

        self.model = None
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")

        self.openrouter = None
        if getattr(settings, "openrouter_api_key", ""):
            self.openrouter = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.openrouter_api_key
            )

    async def load(self) -> None:
        self.memory.update(await self.repo.load_memories())

    async def reply(self, chat_id: int, text: str) -> str:

        context = "\n".join(self.memory[chat_id])

        prompt = f"""
{PERSONA}

Recent chat:
{context}

User: {text}
Ruhi:
""".strip()

        answer = ""

        if self.model:
            try:
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    prompt
                )
                answer = (getattr(response, "text", "") or "").strip()

            except Exception as e:
                print(f"GEMINI ERROR => {e}", flush=True)

        if not answer and self.openrouter:
            try:
                r = await asyncio.to_thread(
                    self.openrouter.chat.completions.create,
                    model="openai/gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": PERSONA},
                        {"role": "user", "content": text}
                    ]
                )

                answer = (r.choices[0].message.content or "").strip()

            except Exception as e:
                print(f"OPENROUTER ERROR => {e}", flush=True)

        if not answer:
            answer = "Main yahi hu 😭 bas thoda network drama chal raha hai."

        answer = answer[:420]

        self.memory[chat_id].append(
            f"U:{text[:160]} | R:{answer[:220]}"
        )

        await self.repo.save_memory(
            chat_id,
            self.memory[chat_id]
        )

        return answer
