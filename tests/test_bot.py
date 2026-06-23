from dataclasses import dataclass, field

from bot import extract_message_content, should_handle_reply_message


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
class FakeMessage:
    content: str
    clean_content: str
    attachments: list[str] = field(default_factory=list)
    embeds: list[str] = field(default_factory=list)
    mentions: list["FakeBotUser"] = field(default_factory=list)
    mention_everyone: bool = False
    reference: FakeReference | None = None


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
