import io
from collections.abc import Collection, Sized
from typing import Final, Protocol

import discord
from discord import app_commands
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


def should_handle_reply_message(
    message: MessageContent,
    bot_user: BotUser,
    target_author_id: int | None = None,
) -> bool:
    if message.reference is None:
        return False

    if message.mention_everyone:
        return False

    mentioned_user_ids = {mention.id for mention in message.mentions}
    if bot_user.id not in mentioned_user_ids:
        return False

    if target_author_id is None:
        return len(mentioned_user_ids) == 1

    return mentioned_user_ids.issubset({bot_user.id, target_author_id})


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


async def resolve_app_command_target(message: discord.Message) -> discord.Message:
    target_message = await resolve_reply_target(message)
    if target_message is not None:
        return target_message

    return message


def extract_message_content(
    target_message: MessageContent,
    invoking_message: MessageContent | None,
    bot_user: BotUser,
) -> str | None:
    content = target_message.clean_content
    if invoking_message is not None and target_message is invoking_message:
        content = strip_bot_mentions(content, bot_user)

    if content:
        return truncate_content(content)

    if has_media(target_message):
        return None

    return EMPTY_CONTENT


async def create_funeral_file(
    target_message: MessageContent,
    invoking_message: MessageContent | None,
    bot_user: BotUser,
) -> discord.File | None:
    content = extract_message_content(target_message, invoking_message, bot_user)
    if content is None:
        return None

    avatar_bytes = await read_avatar_bytes(target_message.author)
    canvas = generate_funeral_image(
        target_message.author.display_name,
        content,
        avatar_bytes=avatar_bytes,
    )

    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(buffer, filename="funeral.png")


async def send_funeral_result(
    destination: discord.abc.Messageable,
    target_message: MessageContent,
    invoking_message: MessageContent | None,
    bot_user: BotUser,
    *,
    reference: discord.Message | None = None,
) -> None:
    try:
        file = await create_funeral_file(target_message, invoking_message, bot_user)
        if file is None:
            await destination.send(NO_TEXT_MESSAGE, reference=reference)
            return

        await destination.send(file=file, reference=reference)
    except (OSError, UnicodeError, ValueError, discord.DiscordException) as error:
        print(f"Error: {error}")
        try:
            await destination.send(IMAGE_ERROR_MESSAGE, reference=reference)
        except discord.DiscordException:
            pass


async def send_funeral_followup_result(
    interaction: discord.Interaction,
    target_message: MessageContent,
    invoking_message: MessageContent | None,
    bot_user: BotUser,
) -> None:
    try:
        file = await create_funeral_file(target_message, invoking_message, bot_user)
        if file is None:
            await interaction.followup.send(NO_TEXT_MESSAGE)
            return

        await interaction.followup.send(file=file)
    except (OSError, UnicodeError, ValueError, discord.DiscordException) as error:
        print(f"Error: {error}")
        try:
            await interaction.followup.send(IMAGE_ERROR_MESSAGE)
        except discord.DiscordException:
            pass


class FuneralClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(
            self,
            allowed_contexts=app_commands.AppCommandContext(
                guild=True,
                dm_channel=True,
                private_channel=True,
            ),
            allowed_installs=app_commands.AppInstallationType(guild=True, user=True),
        )
        self._app_command_synced = False
        self._register_app_commands()

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def setup_hook(self) -> None:
        if self._app_command_synced:
            return

        try:
            await self.tree.sync()
        except (app_commands.MissingApplicationID, discord.Forbidden, discord.HTTPException) as error:
            print(f"Error syncing app commands: {error}")
            return

        self._app_command_synced = True

    def _register_app_commands(self) -> None:
        @self.tree.context_menu(name="Goodbye")
        async def goodbye(
            interaction: discord.Interaction,
            message: discord.Message,
        ) -> None:
            bot_user = self.user
            if bot_user is None:
                return

            channel = interaction.channel
            if channel is None:
                return

            await interaction.response.defer()
            target_message = await resolve_app_command_target(message)
            await send_funeral_followup_result(interaction, target_message, None, bot_user)

    async def on_message(self, message):
        if message.author.bot:
            return

        bot_user = self.user
        if bot_user is None:
            return

        if message.reference is None:
            return

        target_message = await resolve_reply_target(message)
        if target_message is None:
            return

        if not should_handle_reply_message(message, bot_user, target_message.author.id):
            return

        await send_funeral_result(message.channel, target_message, message, bot_user, reference=message)


client = FuneralClient()

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN is not set in .env file.")
    else:
        client.run(TOKEN)
