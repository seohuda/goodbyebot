from typing import Protocol


class BotUser(Protocol):
    id: int


class ChannelPermissions(Protocol):
    view_channel: bool
    send_messages: bool
    read_message_history: bool


class PermissionedChannel(Protocol):
    def permissions_for(self, member: object) -> ChannelPermissions | None: ...


class PermissionedInteraction(Protocol):
    guild: object | None
    channel: PermissionedChannel | None


def should_use_channel_message(interaction: PermissionedInteraction, bot_user: BotUser) -> bool:
    guild = interaction.guild
    if guild is None:
        return False

    member = getattr(guild, "me", None)
    if member is not None:
        bot_member = member
    else:
        get_member = getattr(guild, "get_member", None)
        if not callable(get_member):
            return False

        bot_member = get_member(bot_user.id)
        if bot_member is None:
            return False

    channel = interaction.channel
    if channel is None:
        return False

    permissions = channel.permissions_for(bot_member)
    if permissions is None:
        return False

    return all(
        getattr(permissions, permission_name, False)
        for permission_name in ("view_channel", "send_messages", "read_message_history")
    )
