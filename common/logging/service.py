import logging
import logging.config
import os
import sys
import threading
from typing import Union
from types import TracebackType


def get_logger_name(service_name: str = None, env: str = None) -> str:
    return (
        f"{env or os.getenv('ENVIRONMENT', 'local')}_{service_name or os.getenv('SERVICE_NAME', 'service')}"
    )


def get_log_level() -> str:
    return os.getenv("LOG_LEVEL", "INFO").upper()


def build_log_config(_logger_name: str, _log_level: str, _version: Union[str, int] = 1):
    return {
        "version": _version,
        "disable_existing_loggers": False,
        "formatters": {
            "log": {"format": "%(asctime)s [%(levelname)-8s] %(message)s"},
            "msr": {"format": "%(thread)d %(asctime)s %(message)s"},
            "loki": {
                "format": "%(asctime)s %(funcName)s %(levelname)s %(message)s",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
        },
        "handlers": {
            "default_handler": {
                "level": _log_level,
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "loki",
            },
        },
        "loggers": {
            _logger_name: {
                "handlers": ["default_handler"],
                "level": _log_level,
                "propagate": False,
            },
        },
    }


ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
LOG_LEVEL = get_log_level()
LOGGER_NAME = get_logger_name(env=ENVIRONMENT)


LOG_CONFIG = build_log_config(LOGGER_NAME, LOG_LEVEL)
logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(LOGGER_NAME)


def except_logging(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def unraisable_logging(args: "sys.UnraisableHookArgs") -> None:
    default_msg = "Unraisable exception"
    logger.error(args.err_msg or default_msg, exc_info=args.exc_value)
    raise args.exc_type


def threading_except_logging(args: tuple) -> None:
    exc_type, exc_value, exc_traceback, _ = args
    logger.error(
        "Uncaught threading exception", exc_info=(exc_type, exc_value, exc_traceback)
    )


def monkey_patch_exception_hooks() -> None:
    sys.excepthook = except_logging
    sys.unraisablehook = unraisable_logging
    threading.excepthook = threading_except_logging
