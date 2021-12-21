from log import init_logging, LogLevel
import os

__all__ = []

TOKEN = os.environ.get("DISCORD_TOKEN")


def main():
    init_logging(LogLevel.DEBUG)

    from bot import Bot, init_events

    bot = Bot(command_prefix="kkst.")
    init_events(bot)
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
