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
    bot_user = FakeBotUser()
    message = FakeMessage(
        content="@Goodbye",
        clean_content="@Goodbye",
        attachments=["image.png"],
    )

    content = extract_message_content(message, message, bot_user)

    assert content is None


def test_extract_message_content_strips_self_mentions() -> None:
    bot_user = FakeBotUser()
    message = FakeMessage(
        content="@Goodbye 마지막 한마디",
        clean_content="@Goodbye 마지막 한마디",
    )

    content = extract_message_content(message, message, bot_user)

    assert content == "마지막 한마디"


def test_extract_message_content_keeps_mentions_for_app_command() -> None:
    bot_user = FakeBotUser()
    message = FakeMessage(
        content="@Goodbye 마지막 한마디",
        clean_content="@Goodbye 마지막 한마디",
    )

    content = extract_message_content(message, None, bot_user)

    assert content == "@Goodbye 마지막 한마디"


def test_resolve_app_command_target_uses_replied_to_message() -> None:
    original_message = FakeMessage(content="원본", clean_content="원본")
    reply_message = FakeMessage(
        content="답장",
        clean_content="답장",
        reference=FakeReference(resolved=None, message_id=1),
        channel=FakeChannel(target=original_message),
    )

    target_message = asyncio.run(resolve_app_command_target(reply_message))

    assert target_message is original_message


def test_send_funeral_interaction_result_uses_initial_response(monkeypatch) -> None:
    bot_user = FakeBotUser()
    interaction = FakeInteraction()
    target_message = FakeMessage(content="원본", clean_content="원본")

    async def fake_create_funeral_file(*args, **kwargs) -> object:
        return object()

    monkeypatch.setattr(bot_module, "create_funeral_file", fake_create_funeral_file)

    asyncio.run(send_funeral_interaction_result(interaction, target_message, None, bot_user))

    assert len(interaction.response.sent_kwargs) == 1
    assert "file" in interaction.response.sent_kwargs[0]


def test_should_use_channel_message_requires_bot_presence() -> None:
    interaction = FakeInteraction(guild=FakeGuild(me=None, member=None))
    bot_user = FakeBotUser()

    should_use_channel = should_use_channel_message(interaction, bot_user)

    assert should_use_channel is False


def test_should_use_channel_message_uses_bot_channel_when_present() -> None:
    interaction = FakeInteraction(
        guild=FakeGuild(me=object(), member=None),
        channel=FakeChannel(permissions=FakeChannelPermissions(view_channel=True, send_messages=True, read_message_history=True)),
    )
    bot_user = FakeBotUser()

    should_use_channel = should_use_channel_message(interaction, bot_user)

    assert should_use_channel is True


def test_should_use_channel_message_requires_channel_permissions() -> None:
    interaction = FakeInteraction(
        guild=FakeGuild(me=object(), member=None),
        channel=FakeChannel(permissions=FakeChannelPermissions()),
    )
    bot_user = FakeBotUser()

    should_use_channel = should_use_channel_message(interaction, bot_user)

    assert should_use_channel is False


def test_funeral_client_supports_both_install_contexts() -> None:
    client = FuneralClient()

    allowed_installs = client.tree.allowed_installs
    allowed_contexts = client.tree.allowed_contexts

    assert allowed_installs.guild is True
    assert allowed_installs.user is True
    assert allowed_contexts.guild is True
    assert allowed_contexts.dm_channel is True
    assert allowed_contexts.private_channel is True


def test_extract_message_content_truncates_long_text() -> None:
    bot_user = FakeBotUser()
    target_message = FakeMessage(content="a" * 200, clean_content="a" * 200)
    invoking_message = FakeMessage(content="@Goodbye", clean_content="@Goodbye")

    content = extract_message_content(target_message, invoking_message, bot_user)

    assert content == ("a" * 147) + "..."


def test_should_handle_reply_message_ignores_everyone_ping() -> None:
    bot_user = FakeBotUser()
    message = FakeMessage(
        content="@everyone @Goodbye",
        clean_content="@everyone @Goodbye",
        mentions=[bot_user],
        mention_everyone=True,
        reference=FakeReference(),
    )

    should_handle = should_handle_reply_message(message, bot_user)

    assert should_handle is False


def test_should_handle_reply_message_requires_bot_only_mention() -> None:
    bot_user = FakeBotUser()
    other_user = FakeBotUser(id=2, display_name="Other", name="other")
    message = FakeMessage(
        content="@Goodbye @Other",
        clean_content="@Goodbye @Other",
        mentions=[bot_user, other_user],
        reference=FakeReference(),
    )

    should_handle = should_handle_reply_message(message, bot_user)

    assert should_handle is False


def test_should_handle_reply_message_accepts_bot_only_reply() -> None:
    bot_user = FakeBotUser()
    message = FakeMessage(
        content="@Goodbye",
        clean_content="@Goodbye",
        mentions=[bot_user],
        reference=FakeReference(),
    )

    should_handle = should_handle_reply_message(message, bot_user)

    assert should_handle is True


def test_should_handle_reply_message_allows_target_author_mention_on_reply() -> None:
    bot_user = FakeBotUser()
    target_user = FakeBotUser(id=2, display_name="Other", name="other")
    message = FakeMessage(
        content="@Goodbye @Other",
        clean_content="@Goodbye @Other",
        mentions=[bot_user, target_user],
        reference=FakeReference(),
    )

    should_handle = should_handle_reply_message(message, bot_user, target_author_id=target_user.id)

    assert should_handle is True


def test_read_avatar_bytes_falls_back_when_cdn_is_unreachable() -> None:
    user = FakeAvatarUser()

    avatar_bytes = asyncio.run(read_avatar_bytes(user))

    assert avatar_bytes is None
