from logging import FileHandler, StreamHandler, Formatter, getLogger
from enum import IntEnum
import os

__all__ = ["LogLevel", "init_logger"]

FORMATTER = Formatter("%(asctime)s [%(name)s:%(funcName)s] [%(levelname)s] %(message)s")
LOG_PATH = "logs"

ROOT_LOG = os.path.join(LOG_PATH, "kkst-discord.log")
NEXTCORD_LOG = os.path.join(LOG_PATH, "nextcord.log")

NEXTCORD_CONSOLE_ENABLED = False


class LogLevel(IntEnum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


def init_logger(name: str, level: LogLevel):
    logger = getLogger(name)
    logger.setLevel(level)

    consoleHandler = StreamHandler()
    consoleHandler.setLevel(level.value)
    consoleHandler.setFormatter(FORMATTER)

    fileHandler = FileHandler(filename=ROOT_LOG, mode="a")
    fileHandler.setLevel(level.value)
    fileHandler.setFormatter(FORMATTER)

    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)
    logger.info(f"Initialized the logger '{name}' with the level '{level.name}'")

    return logger


def init_logging(level: LogLevel):
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)

    if os.path.exists(ROOT_LOG):
        os.remove(ROOT_LOG)

    nc = getLogger("nextcord")
    nc.setLevel(level)

    fileHandler = FileHandler(filename=NEXTCORD_LOG, mode="w")
    fileHandler.setLevel(level.value)
    fileHandler.setFormatter(FORMATTER)

    nc.addHandler(fileHandler)

    if NEXTCORD_CONSOLE_ENABLED:
        consoleHandler = StreamHandler()
        consoleHandler.setLevel(level.value)
        consoleHandler.setFormatter(FORMATTER)

        nc.addHandler(consoleHandler)

    nc.info(f"Initialized the nextcord logger with the level '{level.name}'")
