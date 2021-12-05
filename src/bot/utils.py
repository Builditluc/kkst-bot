from typing import List
from datetime import time, timedelta
from nextcord.message import Message
from nextcord.utils import utcnow, sleep_until

from bot.logging import get_logger

log = get_logger("kkst-bot")


async def delete_message(message: Message):
    await message.delete()
    log.debug(f"removed the message '{message.id}' in '{message.channel}' from '{message.author}'")


async def cleanup(messages: List[Message]):
    for message in messages:
        await delete_message(message)

async def wait_for(days=0, seconds=0, microseconds=0):
    log.debug(f"waiting for days: {days} seconds: {seconds} microseconds: {microseconds}")
    when = utcnow() + timedelta(days, seconds, microseconds)
    await sleep_until(when)
