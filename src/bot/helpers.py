from nextcord.message import Message
from nextcord.ext import commands
from datetime import timedelta
from emote import EMOTES
from typing import List

import nextcord.utils as _utils

__all__ = ["cleanup", "ok", "error", "logContext"]


async def cleanup(log, msg: List[Message]):
    for message in msg:
        log.debug(
            f"Deleting the message: {message.id=} {message.channel=} {message.author=}"
        )
        await message.delete()


async def ok(log, msg: Message):
    await msg.add_reaction(EMOTES["white_check_mark"].emoij)
    log.debug(f"Added the emote 'white_check_mark' to {msg=}")


async def error(log, msg: Message):
    await msg.add_reaction(EMOTES["x"].emoij)
    log.debug(f"Added the emote 'x' to {msg=}")


async def wait_for(log, days=0, seconds=0, microseconds=0):
    log.info(f"Waiting for {days=} {seconds=} {microseconds=}")
    when = _utils.utcnow() + timedelta(
        days=days, seconds=seconds, microseconds=microseconds
    )
    await _utils.sleep_until(when)


def logContext(logger, ctx: commands.Context):
    logger.debug(f"context information: {ctx.__dict__=}")
