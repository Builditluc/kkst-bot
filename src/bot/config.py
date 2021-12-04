import os
from typing import List

from bot.logging import get_logger

log = get_logger("kkst-bot")


class Config:
    def __init__(self, _moderator: int, _developer: int, _channel_staff: int, _allowed_guilds: List[int]):
        self.id_moderator: int = _moderator
        self.id_developer: int = _developer

        self.channel_staff: int = _channel_staff

        self.allowed_guilds: List[int] = _allowed_guilds

    @staticmethod
    def from_environment():
        log.debug("loading the config from the environment")
        env = os.environ

        return Config(
            _moderator=int(env.get("ID_MODERATOR", -1)),
            _developer=int(env.get("ID_DEVELOPER", -1)),
            _channel_staff=int(env.get("CHANNEL_STAFF", -1)),
            _allowed_guilds=list(map(int, env.get("ALLOWED_GUILDS", "-1").split(" "))),
        )


CONFIG = Config.from_environment()
