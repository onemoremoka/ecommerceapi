import logging
from logging.config import dictConfig

from ecommerceapi.config import DevConfig, config


class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscation_length: int = 2):
        super().__init__(name)
        self.obfuscation_length = obfuscation_length

    def filter(self, recorder: logging.LogRecord) -> bool:
        if "email" in recorder.__dict__:
            recorder.email = self._obfuscated(recorder.email, self.obfuscation_length)
        return True

    def _obfuscated(email: str, filter_length: int):
        first, last = email.split("@")
        characters = first[:filter_length]
        return characters + "*" * (len(first) - filter_length) + "@" + last


def configurate_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-",
                },
                "obfuscation_email": {
                    "()": EmailObfuscationFilter,
                    "obfuscation_length": 2 if isinstance(config, DevConfig) else 0,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(levelname)s - %(message)s",
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    # "format": "%(asctime)s %(msecs)03dZ | %(levelname)s | [%(correlation_id)s] %(name)s:%(lineno)d - %(message)s",
                    "format": "%(asctime)s %(msecs)03d  %(levelname)-8s %(correlation_id)s %(name)s %(lineno)d %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id"],
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "ecommerceapi.log",
                    "maxBytes": 1024 * 1024 * 5,  # 5 MB
                    "backupCount": 5,
                    "encoding": "utf-8",
                    "filters": ["correlation_id"],
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default", "rotating_file"],
                    "level": "INFO",
                },
                "ecommerceapi": {
                    "handlers": ["default", "rotating_file"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "database": {"handlers": ["default"], "level": "WARNING"},
            },
        }
    )
