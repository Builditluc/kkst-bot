from log import init_logger, LogLevel
from nextcord.ext import commands
from bot import cogs

__all__ = ["Bot"]

log = init_logger(__name__, LogLevel.DEBUG)


class Bot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)

        cogs.Info(self).setup()
        cogs.Exams(self).setup()
        cogs.Debug(self).setup()
        cogs.Utils(self).setup()


def init_events(bot: commands.Bot):
    @bot.event
    async def on_ready():
        log.info(f"Logged on as {bot.user.name} {bot.user.id}")
