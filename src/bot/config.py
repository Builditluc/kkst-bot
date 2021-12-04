from typing import List
from dataclasses import dataclass
import os

from bot.logging import get_logger

log = get_logger("kkst-bot")


@dataclass
class Role:
    id: int
    name: str


class Config:
    def __init__(self, _moderator: int, _developer: int, _channel_staff: int, _allowed_guilds: List[int]):
        self.moderator: Role = Role(_moderator, "Moderator")
        self.developer: Role = Role(_developer, "Developer")

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
