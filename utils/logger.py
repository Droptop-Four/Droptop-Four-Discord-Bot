import datetime as dt
import json
import logging.config

import discord
import sentry_sdk

_logger = logging.getLogger(__name__)


class ColorFormatter(logging.Formatter):
    LEVEL_COLOURS = [
        (logging.DEBUG, "\x1b[40;1m"),
        (logging.INFO, "\x1b[34;1m"),
        (logging.WARNING, "\x1b[33;1m"),
        (logging.ERROR, "\x1b[31m"),
        (logging.CRITICAL, "\x1b[41m"),
    ]

    FORMATS = {
        level: logging.Formatter(
            f"[\x1b[30;1m%(asctime)s\x1b[0m] [{colour}%(levelname)-8s\x1b[0m] \x1b[35m%(name)s\x1b[0m %(message)s",
            "%d-%m-%Y %H:%M:%S",
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        output = formatter.format(record)
        record.exc_text = None
        return output


def initialize_logger(sentry_dsn):
    """
    Initializes the logger.

    Returns:
        bool: If the logger was initialized
    """

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[{asctime}] [{levelname:<8}] {name}: {message}",
                "datefmt": "%d-%m-%Y %H:%M:%S",
                "style": "{",
            },
            "colored": {
                "()": ColorFormatter,
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "formatter": "colored",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "default",
                "filename": "discord.log",
                "encoding": "utf-8",
                "maxBytes": 4 * 1024 * 1024,  # 4 MiB
                "backupCount": 5,  # Rotate through 5 files
            },
        },
        "loggers": {
            "discord": {
                "handlers": ["stdout", "file"],
                "level": "INFO",
                "propagate": True,
            },
            "discord.http": {
                "handlers": ["stdout", "file"],
                "level": "WARNING",
                "propagate": True,
            },
            "discord.state": {
                "handlers": ["stdout", "file"],
                "level": "INFO",
                "propagate": True,
            },
        },
        "root": {"level": "INFO", "handlers": ["stdout", "file"]},
    }

    discord.utils.setup_logging()

    logging.config.dictConfig(logging_config)

    root_logger = logging.getLogger()
    root_logger.info("------------------------------")

    _logger.info("Logger succesfully initialized")

    sentry_sdk.init(
        dsn=sentry_dsn,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
        enable_tracing=True,
    )

    return True
