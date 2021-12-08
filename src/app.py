from bot.dbot import Bot, init_events
from bot.logging import init_logging, DEBUG
import db.interface
import os

# TODO: create __all__

TOKEN = os.environ.get("DISCORD_TOKEN")


def main():
    init_logging(DEBUG)
    bot = Bot(command_prefix="kkst.")

    init_events(bot)

    bot.run(TOKEN)


if __name__ == "__main__":
    main()
