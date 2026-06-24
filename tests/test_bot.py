import asyncio
from dataclasses import dataclass, field

import bot as bot_module
from bot import (
    extract_message_content,
    FuneralClient,
    read_avatar_bytes,
    resolve_app_command_target,
    send_funeral_interaction_result,
    should_use_channel_message,
    should_handle_reply_message,
)


@dataclass(frozen=True, slots=True)
class FakeBotUser:
    id: int = 1
    display_name: str = "Goodbye"
    name: str = "goodbyebot"


@dataclass(frozen=True, slots=True)
class FakeReference:
    resolved: object | None = None
    message_id: int | None = 1


@dataclass(slots=True)
class FakeChannel:
    target: object | None = None
    permissions: object | None = None

    async def fetch_message(self, message_id: int) -> object | None:
        return self.target

    def permissions_for(self, member: object) -> object | None:
        return self.permissions


@dataclass(slots=True)
class FakeFollowup:
    sent_kwargs: list[dict[str, object]] = field(default_factory=list)

    async def send(self, **kwargs: object) -> None:
        self.sent_kwargs.append(kwargs)


@dataclass(slots=True)
class FakeResponse:
    sent_kwargs: list[dict[str, object]] = field(default_factory=list)

    async def send_message(self, **kwargs: object) -> None:
        self.sent_kwargs.append(kwargs)


@dataclass(frozen=True, slots=True)
class FakeChannelPermissions:
    view_channel: bool = False
    send_messages: bool = False
    read_message_history: bool = False


@dataclass(slots=True)
class FakeInteraction:
    response: FakeResponse = field(default_factory=FakeResponse)
    followup: FakeFollowup = field(default_factory=FakeFollowup)
    guild: object | None = None
    channel: object | None = None


@dataclass(slots=True)
class FakeGuild:
    me: object | None = None
    member: object | None = None

    def get_member(self, user_id: int) -> object | None:
        return self.member


@dataclass(slots=True)
class FakeMessage:
    content: str
    clean_content: str
    attachments: list[str] = field(default_factory=list)
    embeds: list[str] = field(default_factory=list)
    mentions: list["FakeBotUser"] = field(default_factory=list)
    mention_everyone: bool = False
    reference: FakeReference | None = None
    channel: object = field(default_factory=FakeChannel)
    author: FakeBotUser = field(default_factory=FakeBotUser)


@dataclass(frozen=True, slots=True)
class FakeAvatar:
    async def read(self) -> bytes:
        raise OSError("boom")


@dataclass(frozen=True, slots=True)
class FakeAvatarUser:
    display_avatar: FakeAvatar = FakeAvatar()


def test_extract_message_content_rejects_attachment_only_invocation() -> None:
    # Given: a user mentions the bot with only an attachment and no real text.
    bot_user = FakeBotUser()
    message = FakeMessage(
        content="@Goodbye",
        clean_content="@Goodbye",
        attachments=["image.png"],
    )

    # When: the bot extracts text for the memorial image.
    content = extract_message_content(message, message, bot_user)

    # Then: the message is rejected instead of rendering "(내용 없음)".
    assert content is None


def test_extract_message_content_strips_self_mentions() -> None:
    # Given: the invoking message contains a bot mention plus user text.
    bot_user = FakeBotUser()
    message = FakeMessage(
        content="@Goodbye 마지막 한마디",
        clean_content="@Goodbye 마지막 한마디",
    )

    # When: the content is extracted from the invoking message.
    content = extract_message_content(message, message, bot_user)

    # Then: only the user's text remains.
    assert content == "마지막 한마디"


def test_extract_message_content_keeps_mentions_for_app_command() -> None:
    # Given: a selected message that mentions the bot as part of the original text.
    bot_user = FakeBotUser()
    message = FakeMessage(
        content="@Goodbye 마지막 한마디",
        clean_content="@Goodbye 마지막 한마디",
    )

    # When: the content is extracted without a separate invoking message.
    content = extract_message_content(message, None, bot_user)

    # Then: the original text is preserved for the app command path.
    assert content == "@Goodbye 마지막 한마디"


def test_resolve_app_command_target_uses_replied_to_message() -> None:
    # Given: a reply message that points at an original target.
    original_message = FakeMessage(content="원본", clean_content="원본")
    reply_message = FakeMessage(
        content="답장",
        clean_content="답장",
        reference=FakeReference(resolved=None, message_id=1),
        channel=FakeChannel(target=original_message),
    )

    # When: the app command target is resolved.
    target_message = asyncio.run(resolve_app_command_target(reply_message))

    # Then: the original message is used instead of the reply itself.
    assert target_message is original_message


def test_send_funeral_interaction_result_uses_initial_response(monkeypatch) -> None:
    # Given: an app-command interaction and a message with text content.
    bot_user = FakeBotUser()
    interaction = FakeInteraction()
    target_message = FakeMessage(content="원본", clean_content="원본")

    async def fake_create_funeral_file(*args, **kwargs) -> object:
        return object()

    monkeypatch.setattr(bot_module, "create_funeral_file", fake_create_funeral_file)

    # When: the bot sends the generated result.
    asyncio.run(send_funeral_interaction_result(interaction, target_message, None, bot_user))

    # Then: the response is sent through the interaction response.
    assert len(interaction.response.sent_kwargs) == 1
    assert "file" in interaction.response.sent_kwargs[0]


def test_should_use_channel_message_requires_bot_presence() -> None:
    # Given: an interaction from a guild without the bot member cached.
    interaction = FakeInteraction(guild=FakeGuild(me=None, member=None))
    bot_user = FakeBotUser()

    # When: the app decides how to send the result.
    should_use_channel = should_use_channel_message(interaction, bot_user)

    # Then: the app falls back to the interaction response path.
    assert should_use_channel is False


def test_should_use_channel_message_uses_bot_channel_when_present() -> None:
    # Given: an interaction from a guild where the bot is present.
    interaction = FakeInteraction(
        guild=FakeGuild(me=object(), member=None),
        channel=FakeChannel(permissions=FakeChannelPermissions(view_channel=True, send_messages=True, read_message_history=True)),
    )
    bot_user = FakeBotUser()

    # When: the app decides how to send the result.
    should_use_channel = should_use_channel_message(interaction, bot_user)

    # Then: the bot can send the generated image as a normal channel message.
    assert should_use_channel is True


def test_should_use_channel_message_requires_channel_permissions() -> None:
    # Given: an interaction from a guild where the bot is cached but cannot send messages in-channel.
    interaction = FakeInteraction(
        guild=FakeGuild(me=object(), member=None),
        channel=FakeChannel(permissions=FakeChannelPermissions()),
    )
    bot_user = FakeBotUser()

    # When: the app decides how to send the result.
    should_use_channel = should_use_channel_message(interaction, bot_user)

    # Then: the app falls back to the interaction response path instead of hitting Missing Access.
    assert should_use_channel is False


def test_funeral_client_supports_both_install_contexts() -> None:
    # Given: the client is initialized for app commands.
    client = FuneralClient()

    # When: the app command tree configuration is inspected.
    allowed_installs = client.tree.allowed_installs
    allowed_contexts = client.tree.allowed_contexts

    # Then: the app is available both as a guild install and a user install.
    assert allowed_installs.guild is True
    assert allowed_installs.user is True
    assert allowed_contexts.guild is True
    assert allowed_contexts.dm_channel is True
    assert allowed_contexts.private_channel is True


def test_extract_message_content_truncates_long_text() -> None:
    # Given: a target message is longer than the image layout supports.
    bot_user = FakeBotUser()
    target_message = FakeMessage(content="a" * 200, clean_content="a" * 200)
    invoking_message = FakeMessage(content="@Goodbye", clean_content="@Goodbye")

    # When: the content is extracted.
    content = extract_message_content(target_message, invoking_message, bot_user)

    # Then: it is capped at 150 characters with an ellipsis.
    assert content == ("a" * 147) + "..."


def test_should_handle_reply_message_ignores_everyone_ping() -> None:
    # Given: a reply that pings everyone and the bot.
    bot_user = FakeBotUser()
    message = FakeMessage(
        content="@everyone @Goodbye",
        clean_content="@everyone @Goodbye",
        mentions=[bot_user],
        mention_everyone=True,
        reference=FakeReference(),
    )

    # When: the bot checks whether to process the reply.
    should_handle = should_handle_reply_message(message, bot_user)

    # Then: the bot ignores the message.
    assert should_handle is False


def test_should_handle_reply_message_requires_bot_only_mention() -> None:
    # Given: a reply that mentions the bot and another user.
    bot_user = FakeBotUser()
    other_user = FakeBotUser(id=2, display_name="Other", name="other")
    message = FakeMessage(
        content="@Goodbye @Other",
        clean_content="@Goodbye @Other",
        mentions=[bot_user, other_user],
        reference=FakeReference(),
    )

    # When: the bot checks whether to process the reply.
    should_handle = should_handle_reply_message(message, bot_user)

    # Then: the bot ignores the message because the mention is not bot-only.
    assert should_handle is False


def test_should_handle_reply_message_accepts_bot_only_reply() -> None:
    # Given: a reply that mentions only the bot.
    bot_user = FakeBotUser()
    message = FakeMessage(
        content="@Goodbye",
        clean_content="@Goodbye",
        mentions=[bot_user],
        reference=FakeReference(),
    )

    # When: the bot checks whether to process the reply.
    should_handle = should_handle_reply_message(message, bot_user)

    # Then: the bot handles the reply.
    assert should_handle is True


def test_should_handle_reply_message_allows_target_author_mention_on_reply() -> None:
    # Given: a reply that mentions the bot and the original message author.
    bot_user = FakeBotUser()
    target_user = FakeBotUser(id=2, display_name="Other", name="other")
    message = FakeMessage(
        content="@Goodbye @Other",
        clean_content="@Goodbye @Other",
        mentions=[bot_user, target_user],
        reference=FakeReference(),
    )

    # When: the bot checks whether to process the reply with the target author known.
    should_handle = should_handle_reply_message(message, bot_user, target_author_id=target_user.id)

    # Then: the bot handles the reply.
    assert should_handle is True


def test_read_avatar_bytes_falls_back_when_cdn_is_unreachable() -> None:
    # Given: the avatar CDN fetch fails with a client error.
    user = FakeAvatarUser()

    # When: the bot tries to read the avatar bytes.
    avatar_bytes = asyncio.run(read_avatar_bytes(user))

    # Then: the bot falls back to a placeholder avatar.
    assert avatar_bytes is None
