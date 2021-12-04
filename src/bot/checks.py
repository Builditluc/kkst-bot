from nextcord.ext import commands
from nextcord import utils

from bot.logging import get_logger
from bot.config import CONFIG, Role

log = get_logger("kkst-bot")


class NoPrivateMessages(commands.CheckFailure):
    def __init__(self, ctx: commands.Context) -> None:
        super().__init__(message="Hey, no DMs!")
        log.warn(f"{ctx.author} tried sending a private message")


class GuildNotAllowed(commands.CheckFailure):
    def __init__(self, ctx: commands.Context) -> None:
        super().__init__(message="It seems like you're on the wrong server! (GUILD_NOT_ALLOWED)")
        log.warn(f"{ctx.author} tried executing a command on a disallowed server. name: '{ctx.guild.name}' id: '{ctx.guild.id}'")


class MissingRole(commands.CheckFailure):
    def __init__(self, ctx: commands.Context, role: Role) -> None:
        super().__init__(message=f"You can only execute this with the '{role.name}' role! (MISSING_ROLE)")
        log.warn(f"{ctx.author} tried executing a command without the right permissions. missing role: '{role.name}'")

class WrongChannel(commands.CheckFailure):
    def __init__(self, ctx: commands.Context, channel_id: int) -> None:
        super().__init__(message="Wrong Channel mate! (WRONG_CHANNEL)")
        log.warn(f"{ctx.author} tired executing a command in the wrong channel. channel: '{ctx.channel.id}' correct_channel: '{channel_id}'")


def guild_allowed():
    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            raise NoPrivateMessages(ctx)
        if ctx.guild.id not in CONFIG.allowed_guilds:
            raise GuildNotAllowed(ctx)

        return True

    return commands.check(predicate)


def has_role(role: Role):
    async def predicate(ctx: commands.Context):
        if utils.get(ctx.author.roles, id=role.id) is None:
            raise MissingRole(ctx, role)
        return True

    return commands.check(predicate)


def in_channel(channel_id: int):
    async def predicate(ctx: commands.Context):
        if ctx.channel.id != channel_id:
            raise WrongChannel(ctx, channel_id)
        return True

    return commands.check(predicate)
