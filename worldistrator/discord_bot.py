import os

import discord
from dotenv import load_dotenv

from worldistrator.service import run_worldistrator

load_dotenv()

DISCORD_MAX_MESSAGE_LENGTH = 2000


def _split_message(text: str, limit: int = DISCORD_MAX_MESSAGE_LENGTH) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    while text:
        chunks.append(text[:limit])
        text = text[limit:]
    return chunks


class WorldistratorBot(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self) -> None:
        print(f"Worldistrator logged in as {self.user} (id={self.user.id})")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        is_dm = message.guild is None
        is_mention = self.user in message.mentions if self.user else False

        if not is_dm and not is_mention:
            return

        prompt = message.content
        for mention in message.mentions:
            prompt = prompt.replace(f"<@{mention.id}>", "").replace(
                f"<@!{mention.id}>", ""
            )
        prompt = prompt.strip()

        if not prompt:
            await message.reply(
                "Hi, I am a chief executive for the worldism intelligence department 6."
                "I can do a lot, just ask."
            )
            return

        async with message.channel.typing():
            try:
                reply = await run_worldistrator(
                    user_id=str(message.author.id),
                    session_id=str(message.channel.id),
                    message=prompt,
                )
            except Exception as exc:
                print(exc)
                if "RESOURCE_EXHAUSTED" in str(exc):
                    reply = f"Please excuse my behaviour, dear worldist. I must have ran out of quota or reached an excess of requests. Contact the worldism government's software engineering agency."
                else:
                    reply = f"Error. I am not sure what though."

        for chunk in _split_message(reply):
            await message.reply(chunk)


def run_discord_bot() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN is not set in the environment.")

    bot = WorldistratorBot()
    bot.run(token)
