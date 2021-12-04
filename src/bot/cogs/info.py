from nextcord.ext import commands
from bot.logging import get_logger

log = get_logger("kkst-bot")


class Info(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def repo(self, ctx: commands.Context):
        log.info(f"{ctx.author} executed info.repo")
        await ctx.send("You can find my source code here: https://github.com/builditluc/kkst-bot")


def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))
