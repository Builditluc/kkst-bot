from nextcord.ext import commands
from bot.logging import get_logger
from bot.checks import guild_allowed, has_role
from bot.config import CONFIG

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

    @commands.command()
    @guild_allowed()
    @has_role(CONFIG.moderator)
    async def moderator_only(self, ctx: commands.Context):
        log.info(f"{ctx.author} executed info.moderator_only")
        await ctx.send("You're a Moderator, idiot")

    @commands.command()
    @guild_allowed()
    @has_role(CONFIG.developer)
    async def developer_only(self, ctx: commands.Context):
        log.info(f"{ctx.author} executed info.developer_only")
        await ctx.send("You're a Developer, nice")

    @repo.error
    @hello.error
    @moderator_only.error
    @developer_only.error
    async def handle_error(self, ctx: commands.Context, error):
        await ctx.send(error)


def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))
