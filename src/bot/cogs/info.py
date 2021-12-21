from datetime import datetime
from nextcord.ext import commands
from bot.checks import guild_allowed
from bot.cogs.cog import Cog
from bot.helpers import logContext, ok, error
from log import init_logger, LogLevel

__all__ = ["Info"]

log = init_logger(__name__, LogLevel.DEBUG)
SOURCE_URL = "https://github.com/builditluc/kkst-bot"


class Info(Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__("info", bot)
        self.startup = datetime.now()
        log.info("Created an instance of the Info cog")
        log.info(f"Started the bot at: {self.startup}")

    @commands.command()
    @guild_allowed()
    async def repo(self, ctx: commands.Context):
        log.info(f"{ctx.author} executed Info.repo")
        logContext(log, ctx)

        await ctx.reply(f"You can find my source code at: {SOURCE_URL}")
        await ok(log, ctx.message)

        log.info("Successfully finished Info.repo")

    @commands.command()
    @guild_allowed()
    async def uptime(self, ctx: commands.Context):
        log.info(f"{ctx.author} executed Info.uptime")
        logContext(log, ctx)

        await ctx.reply(
            f"I'm online since: {self.startup.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await ok(log, ctx.message)

        log.info("Successfully finished Info.uptime")
