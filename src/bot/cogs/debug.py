from nextcord.ext import commands
from bot.checks import guild_allowed
from bot.cogs.cog import Cog
from log import init_logger, LogLevel

__all__ = ["Debug"]

log = init_logger(__name__, LogLevel.DEBUG)


class Debug(Cog):
    def __init__(self, bot: commands.Bot, enabled=False) -> None:
        super().__init__("debug", bot)
        self.enabled = enabled

    @commands.command()
    @guild_allowed()
    async def getLog(self, ctx: commands.Context):
        pass
