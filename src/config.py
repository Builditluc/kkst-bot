from dataclasses import dataclass
from typing import List
import os

__all__ = ["CONFIG", "Role"]


@dataclass
class Role:
    id: int
    name: str


@dataclass
class Config:
    allowed_guilds: List[int]
    developer: Role
    moderator: Role
    exams_channel: int
    staff_channel: int

    @staticmethod
    def fromFile(path: str):
        pass

    @staticmethod
    def fromEnvironment():
        env = os.environ
        return Config(
            allowed_guilds=list(map(int, env.get("ALLOWED_GUILDS", "-1").split(" "))),
            developer=Role(int(env.get("ID_DEVELOPER", -1)), "Developer"),
            moderator=Role(int(env.get("ID_MODERATOR", -1)), "Moderator"),
            exams_channel=int(env.get("CHANNEL_EXAMS", -1)),
            staff_channel=int(env.get("CHANNEL_STAFF", -1)),
        )


CONFIG: Config = Config.fromEnvironment()
