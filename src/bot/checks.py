from nextcord.ext import commands
from bot.logging import get_logger
from bot.config import CONFIG

log = get_logger("kkst-bot")


class NoPrivateMessages(commands.CheckFailure):
    def __init__(self, ctx: commands.Context) -> None:
        super().__init__(message="Hey, no DMs!")
        log.warn(f"{ctx.author} tried sending a private message")


class GuildNotAllowed(commands.CheckFailure):
    def __init__(self, ctx: commands.Context) -> None:
        super().__init__(message="It seems like you're on the wrong server! (GUILD_NOT_ALLOWED)")
        log.warn(f"{ctx.author} tried executing a command on a disallowed server. name: '{ctx.guild.name}' id: '{ctx.guild.id}'")


def guild_allowed():
    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            raise NoPrivateMessages(ctx)
        if ctx.guild.id not in CONFIG.allowed_guilds:
            raise GuildNotAllowed(ctx)

        return True

    return commands.check(predicate)
