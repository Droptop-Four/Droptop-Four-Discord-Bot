import logging
import logging.handlers


def initialize_logger():
    """
    Initializes the logger.

    Returns:
            bool: If the logger was initialized
            logger (logger): The logger
    """

    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)
    logging.getLogger("discord.http").setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename="discord.log",
        encoding="utf-8",
        maxBytes=4 * 1024 * 1024,  # 4 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("------------------------------")
    logger.info("Logger succesfully initialized")

    return True, logger
