from typing import List
from nextcord.ext import commands
from nextcord.message import Message

from bot.logging import get_logger

log = get_logger("kkst-bot")


class Utils(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    async def get_reaction(self, message: Message, reactions: List[str], user) -> int:
        def check(reaction, _user) -> bool:
            return _user == user and str(reaction.emoji) in reactions        

        log.info(f"waiting for a reaction ({reactions}) from {user.name} on the message {message.id}")
        reaction, _ = await self.bot.wait_for("reaction_add", check=check)

        return reactions.index(reaction)



def setup(bot: commands.Bot):
    bot.add_cog(Utils(bot))
