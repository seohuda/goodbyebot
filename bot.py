import io
from collections.abc import Sized
from typing import Final, Protocol

import discord
from config import TOKEN
from image_generator import generate_funeral_image

MAX_CONTENT_LENGTH: Final = 150
EMPTY_CONTENT: Final = "(내용 없음)"
NO_TEXT_MESSAGE: Final = "텍스트 메시지만 영정사진으로 만들 수 있습니다."
IMAGE_ERROR_MESSAGE: Final = "이미지 생성 중 오류가 발생했습니다."


class BotUser(Protocol):
    display_name: str
    name: str


class MessageContent(Protocol):
    content: str
    clean_content: str
    attachments: Sized
    embeds: Sized


def strip_bot_mentions(content: str, bot_user: BotUser) -> str:
    stripped_content = content
    for mention in (f"@{bot_user.display_name}", f"@{bot_user.name}"):
        stripped_content = stripped_content.replace(mention, "")
    return stripped_content.strip()


def truncate_content(content: str) -> str:
    if len(content) <= MAX_CONTENT_LENGTH:
        return content
    return f"{content[: MAX_CONTENT_LENGTH - 3]}..."


def has_media(message: MessageContent) -> bool:
    return len(message.attachments) > 0 or len(message.embeds) > 0


def extract_message_content(
    target_message: MessageContent,
    invoking_message: MessageContent,
    bot_user: BotUser,
) -> str | None:
    content = target_message.clean_content
    if target_message is invoking_message:
        content = strip_bot_mentions(content, bot_user)

    if content:
        return truncate_content(content)

    if has_media(target_message):
        return None

    return EMPTY_CONTENT


class FuneralClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message):
        if message.author.bot:
            return

        bot_user = self.user
        if bot_user is None:
            return

        if bot_user.mentioned_in(message):
            target_message = message
            if message.reference and isinstance(message.reference.resolved, discord.Message):
                target_message = message.reference.resolved

            content = extract_message_content(target_message, message, bot_user)
            if content is None:
                await message.channel.send(NO_TEXT_MESSAGE, reference=message)
                return

            try:
                canvas = generate_funeral_image(target_message.author.display_name, content)

                buffer = io.BytesIO()
                canvas.save(buffer, format="PNG")
                buffer.seek(0)

                file = discord.File(buffer, filename="funeral.png")
                await message.channel.send(file=file, reference=message)
            except (OSError, UnicodeError, ValueError, discord.DiscordException) as error:
                print(f"Error: {error}")
                await message.channel.send(IMAGE_ERROR_MESSAGE, reference=message)


client = FuneralClient()

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN is not set in .env file.")
    else:
        client.run(TOKEN)
