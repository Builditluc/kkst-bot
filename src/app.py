from bot import logging as log


def main():
    log.init_logging(log.DEBUG)

    root_logger = log.get_logger("kkst-bot")
    root_logger.info("test")


if __name__ == "__main__":
    main()
