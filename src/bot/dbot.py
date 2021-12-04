from bot.logging import get_logger
from nextcord.ext import commands

log = get_logger("kkst-bot")


class Bot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)


def init_events(bot: commands.Bot):
    @bot.event
    async def on_ready():
        log.info(f"Logged on as {bot.owner_id}")
