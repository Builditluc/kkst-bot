from nextcord.ext import commands

__all__ = ["Cog"]


class Cog(commands.Cog):
    def __init__(self, name: str, bot: commands.Bot):
        self.name = name
        self.bot = bot

    def setup(self):
        self.bot.add_cog(self, override=True)
