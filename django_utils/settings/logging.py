import sys

from configurations import values


class LogMixin:
    """
    This mixins contains the logging configuration of our Django based
    web applications. Its default values are suited for production.
    """

    LOGGING_LEVEL = values.Value("WARNING")

    LOGGING_HANDLERS = values.ListValue(["stream"])

    LOGGING_STREAM = sys.stderr

    @property
    def LOGGING_FILENAME(self):
        default_value = super().BASE_DIR / "log" / "django.log"
        return values.Value(environ_name="LOGGING_FILENAME", default=default_value)

    @property
    def LOGGING(self):
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "verbose": {
                    "format": "{asctime} {levelname} {name} {message}",
                    "style": "{",
                },
                "simple": {
                    "format": "{message}",
                    "style": "{",
                },
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "verbose",
                    "stream": self.LOGGING_STREAM,
                },
                "file": {
                    "level": "DEBUG",
                    "class": "logging.FileHandler",
                    "formatter": "verbose",
                    "filename": self.LOGGING_FILENAME,
                },
                "stream": {
                    "class": "logging.StreamHandler",
                    "formatter": "verbose",
                },
            },
            "loggers": {
                "": {
                    "handlers": self.LOGGING_HANDLERS,
                    "level": self.LOGGING_LEVEL,
                },
                "django": {
                    "handlers": self.LOGGING_HANDLERS,
                    "level": self.LOGGING_LEVEL,
                    "propagate": False,
                },
                "django.db": {
                    "handlers": self.LOGGING_HANDLERS,
                    "level": self.LOGGING_LEVEL,
                    "propagate": False,
                },
            },
        }
