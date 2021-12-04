from nextcord.ext import commands
from bot.logging import get_logger

log = get_logger("kkst-bot")


class NoPrivateMessages(commands.CheckFailure):
    def __init__(self, ctx: commands.Context) -> None:
        super().__init__(message="Hey, no DMs!")
        log.warn(f"{ctx.author} tried sending a private message")


def guild_only():
    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            raise NoPrivateMessages(ctx)
        return True

    return commands.check(predicate)
