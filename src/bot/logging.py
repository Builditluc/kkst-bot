from logging import (FileHandler, StreamHandler, Formatter, getLogger)
import os
import sys

FORMATTER = Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
LOG_PATH = "logs"

ROOT_LOG = os.path.join(LOG_PATH, "kkst-discord.log")
NEXTCORD_LOG = os.path.join(LOG_PATH, "nextcord.log")

DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50


def get_logger(name: str):
    return getLogger(name)


def init_logging(level: int):
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)

    consoleHandler = StreamHandler(sys.stdout)
    consoleHandler.setFormatter(FORMATTER)

    # root logger
    root = getLogger("kkst-bot")
    root.setLevel(level)

    rootFileHandler = FileHandler(filename=ROOT_LOG, mode="w")
    rootFileHandler.setFormatter(FORMATTER)

    root.addHandler(consoleHandler)
    root.addHandler(rootFileHandler)

    # nextcord logger
    nc = getLogger("nextcord")
    nc.setLevel(DEBUG)

    ncFileHandler = FileHandler(filename=NEXTCORD_LOG, mode="w")
    ncFileHandler.setFormatter(FORMATTER)

    nc.addHandler(consoleHandler)
    nc.addHandler(ncFileHandler)
