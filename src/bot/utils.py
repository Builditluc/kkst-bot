from typing import List
from nextcord.message import Message

from bot.logging import get_logger

log = get_logger("kkst-bot")


async def delete_message(message: Message):
    await message.delete()
    log.debug(f"removed the message '{message.id}' in '{message.channel}' from '{message.author}'")


async def cleanup(messages: List[Message]):
    for message in messages:
        await delete_message(message)
