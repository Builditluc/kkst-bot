from nextcord.ext import commands
from bot.logging import get_logger
from bot.checks import guild_allowed

log = get_logger("kkst-bot")


class Info(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    @guild_allowed()
    async def repo(self, ctx: commands.Context):
        log.info(f"{ctx.author} executed info.repo")
        await ctx.send("You can find my source code here: https://github.com/builditluc/kkst-bot")

    @commands.command()
    @guild_allowed()
    async def hello(self, ctx: commands.Context):
        log.info(f"{ctx.author} executed info.test")
        await ctx.send("Hello there...")

    @repo.error
    @hello.error
    async def handle_error(self, ctx: commands.Context, error):
        await ctx.send(error)


def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))
