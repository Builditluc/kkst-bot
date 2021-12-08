from datetime import datetime
from typing import List, Optional, Tuple
from nextcord.ext import commands
from nextcord.message import Message
from bot.utils import wait_for

from emote import Emote
from bot.logging import get_logger

import asyncio

__all__ = [
    "Utils",
    "setup"
]

TIMEOUT = 200
    
log = get_logger("kkst-bot")


class Utils(commands.Cog, name="utils"):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    async def get_reaction(self, ctx: commands.Context, message: Message, reactions: List[Emote], user) -> Tuple[Optional[int], List[Message]]:
        messages: List[Message] = []

        for reaction in reactions:
            await message.add_reaction(reaction.emoji)

        def check(reaction, _user) -> bool:
            return _user == user and reaction in reactions        

        log.info(f"waiting for a reaction ({reactions}) from {user.name} on the message {message.id}")
        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=TIMEOUT)
        except asyncio.TimeoutError:
            msg = await ctx.send("You took to long to respond (TIMEOUT)")
            log.info(f"aborting command from {ctx.author} because TIMEOUT")
            messages.append(msg)

            await wait_for(seconds=2)
            return (None, messages)

        return (reactions.index(reaction), messages)

    async def get_string(self, ctx: commands.Context, message: str) -> Tuple[Optional[str], List[Message]]:
        messages: List[Message] = []

        msg = await ctx.send(message)
        messages.append(msg)

        def check(message: Message) -> bool:
            return ctx.author == message.author and ctx.channel == message.channel

        log.info(f"wating for a message from {ctx.author} in the channel {ctx.channel}")
        try:
            message_input: Message = await self.bot.wait_for("message", check=check, timeout=TIMEOUT)
        except asyncio.TimeoutError:
            msg = await ctx.send("You took to long to respond (TIMEOUT)")
            log.info(f"aborting command from {ctx.author} because TIMEOUT")
            messages.append(msg)

            await wait_for(seconds=2)
            return (None, messages)

        return (message_input.content, messages)

    async def get_date(self, ctx: commands.Context, past_allowed: bool) -> Tuple[Optional[datetime], List[Message]]:
        messages: List[Message] = []

        msg = await ctx.send(f"Please enter a valid date in the following format: 'dd-mm-yyyy'")
        messages.append(msg)

        #NOTE:This is a helper function, used in this function only
        def string_to_date(date_str: str) -> datetime:
            return datetime.strptime(date_str, "%d-%m-%Y")

        def check(message: Message) -> bool:
            if message.author != ctx.author and message.channel != ctx.channel:
                return False
            try:
                date = string_to_date(message.content)
                if date < datetime.today() and not past_allowed:
                    return False
                return True
            except ValueError:
                return False

        log.info(f"waiting for a date from {ctx.author} in the channel {ctx.channel}")
        try: 
            date_message: Message = await self.bot.wait_for("message", check=check, timeout=TIMEOUT)
        except asyncio.TimeoutError:
            msg = await ctx.send("You took to long to respond (TIMEOUT)")
            log.info(f"aborting command from {ctx.author} because TIMEOUT")
            messages.append(msg)

            await wait_for(seconds=2)
            return (None, messages)

        date = string_to_date(date_message.content)
        messages.append(date_message)

        return (date, messages)

def setup(bot: commands.Bot):
    bot.add_cog(Utils(bot))
