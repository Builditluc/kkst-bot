import asyncio
from datetime import datetime
from typing import List, Optional, Tuple
from nextcord.ext import commands
from nextcord.message import Message
from emote import Emote
from bot.cogs.cog import Cog
from log import init_logger, LogLevel
from bot.helpers import wait_for

__all__ = ["Utils"]

log = init_logger(__name__, LogLevel.DEBUG)
TIMEOUT = 200


class Utils(Cog, name="utils"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__("utils", bot)

    async def getInput(
        self, ctx: commands.Context, message: str
    ) -> Tuple[Optional[str], List[Message]]:
        messages: List[Message] = []

        msg = await ctx.send(message)
        messages.append(msg)

        def check(message: Message) -> bool:
            return ctx.author == message.author and ctx.channel == message.channel

        log.info(
            f"Waiting for a message from {ctx.author} in the channel {ctx.channel}"
        )
        try:
            message_input: Message = await self.bot.wait_for(
                "message", check=check, timeout=TIMEOUT
            )
            messages.append(message_input)
        except asyncio.TimeoutError:
            return await self._timeoutError(ctx, messages)

        return (message_input.content, messages)

    async def getReaction(
        self, ctx: commands.Context, message: Message, reactions: List[Emote], user
    ) -> Tuple[Optional[int], List[Message]]:
        messages: List[Message] = []

        for reaction in reactions:
            await message.add_reaction(reaction.emoij)

        def check(reaction, _user) -> bool:
            return _user == user and reaction in reactions

        log.info(
            f"Waiting for a reaction ({list(map(str, reactions))}) from {user.name} on the message {message.id}"
        )
        try:
            reaction, _ = await self.bot.wait_for(
                "reaction_add", check=check, timeout=TIMEOUT
            )
        except asyncio.TimeoutError:
            return await self._timeoutError(ctx, messages)

        return (reactions.index(reaction), messages)

    async def getDate(
        self, ctx: commands.Context, past_allowed: bool
    ) -> Tuple[Optional[datetime], List[Message]]:
        messages: List[Message] = []

        msg = await ctx.send(
            f"Please enter a valid date in the following format: 'dd-mm-yyyy'"
        )
        messages.append(msg)

        def dateFromString(date: str) -> datetime:
            return datetime.strptime(date, "%d-%m-%Y")

        def check(message: Message) -> bool:
            if message.author != ctx.author and message.channel != ctx.channel:
                return False
            try:
                date = dateFromString(message.content)
                if date < datetime.today() and not past_allowed:
                    return False
                return True
            except ValueError:
                return False

        log.info(f"Waiting for a date from {ctx.author} in the channel {ctx.channel}")
        try:
            date_message: Message = await self.bot.wait_for(
                "message", check=check, timeout=TIMEOUT
            )
        except asyncio.TimeoutError:
            return await self._timeoutError(ctx, messages)

        date = dateFromString(date_message.content)
        messages.append(date_message)

        return (date, messages)

    async def _timeoutError(
        self, ctx: commands.Context, messages: List[Message]
    ) -> Tuple[None, List[Message]]:
        msg = await ctx.send("I've waited and waited but you did not respond (TIMEOUT)")
        messages.append(msg)
        log.info(f"Aborting command from {ctx.author} because TIMEOUT is reached")

        await wait_for(log, seconds=2)
        return (None, messages)
