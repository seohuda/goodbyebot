import io
from collections.abc import Collection, Sized
from typing import Final, Protocol

import discord
from config import TOKEN
from image_generator import generate_funeral_image

MAX_CONTENT_LENGTH: Final = 150
EMPTY_CONTENT: Final = "(내용 없음)"
NO_TEXT_MESSAGE: Final = "텍스트 메시지만 영정사진으로 만들 수 있습니다."
IMAGE_ERROR_MESSAGE: Final = "이미지 생성 중 오류가 발생했습니다."


class BotUser(Protocol):
    id: int
    display_name: str
    name: str


class AvatarAsset(Protocol):
    async def read(self) -> bytes: ...


class UserWithAvatar(BotUser, Protocol):
    display_avatar: AvatarAsset


class MessageReference(Protocol):
    resolved: object | None
    message_id: int | None


class MessageContent(Protocol):
    content: str
    clean_content: str
    attachments: Sized
    embeds: Sized
    mentions: Collection[BotUser]
    mention_everyone: bool
    reference: MessageReference | None
    author: BotUser
    channel: object


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


def should_handle_reply_message(message: MessageContent, bot_user: BotUser) -> bool:
    if message.reference is None:
        return False

    if message.mention_everyone:
        return False

    if len(message.mentions) != 1:
        return False

    return any(mention.id == bot_user.id for mention in message.mentions)


async def read_avatar_bytes(user: UserWithAvatar) -> bytes | None:
    try:
        return await user.display_avatar.read()
    except (OSError, discord.DiscordException, ValueError, TimeoutError):
        return None


async def resolve_reply_target(message: discord.Message) -> discord.Message | None:
    reference = message.reference
    if reference is None:
        return None

    resolved = reference.resolved
    if isinstance(resolved, discord.Message):
        return resolved

    if reference.message_id is None:
        return None

    try:
        return await message.channel.fetch_message(reference.message_id)
    except (discord.Forbidden, discord.NotFound, discord.HTTPException):
        return None


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

        if should_handle_reply_message(message, bot_user):
            target_message = await resolve_reply_target(message)
            if target_message is None:
                return

            content = extract_message_content(target_message, message, bot_user)
            if content is None:
                await message.channel.send(NO_TEXT_MESSAGE, reference=message)
                return

            try:
                avatar_bytes = await read_avatar_bytes(target_message.author)
                canvas = generate_funeral_image(
                    target_message.author.display_name,
                    content,
                    avatar_bytes=avatar_bytes,
                )

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
